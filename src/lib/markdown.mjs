// ブログ記事 Markdown の加工（依存パッケージなし）。astro.config.mjs の unified() に載せる。
// remark 段階（Markdown の木）で目印を付け、rehype 段階（HTML の木）でデジタル庁デザインシステムの部品に組み立てる。
// 見た目は src/styles/global.css、原稿の書き方は content/blog/README.md、設計の理由は DESIGN.md。
// 解約手帳（kaiyaku-navi）の src/lib/markdown.mjs から、確認日バナーと広告枠を除いて流用した。
import { rehypeHeadingIds } from '@astrojs/markdown-remark';

// コメントだけでできた HTML ノード。記事ファイルのコメント（広告枠の雛形・編集メモ）を公開ページに出さない
const COMMENT_ONLY = /^\s*(?:<!--[\s\S]*?-->\s*)+$/;
// 目次を差し込む位置の目印（本文の一番外側に書く）
const TOC_SLOT = /^\s*<!--\s*toc\s*-->\s*$/i;
// URL だけのコードスパン（出典表の `https://…`）
const URL_ONLY = /^https?:\/\/[^\s`<>]+$/;
// 囲みの記号（GitHub と同じ書き方）。`> [!WARNING] 題` の「題」は任意・装飾なしの文字だけ
const CALLOUT = /^\[!([A-Za-z]+)\][^\S\n]*(.*)$/;
const CALLOUTS = { NOTE: 'note', WARNING: 'warning' };
// 引用の最終行に書く出典（`> — 消費者庁「…」`）
const ATTRIBUTION = /^[—―]/;

/** ブログ記事（content/blog/*.md）か。記事だけの処理（目次）はこれで分ける */
const isArticle = (file) => /[\\/]content[\\/]blog[\\/]/.test(String(file.path ?? ''));

/**
 * 本文の最初の H1 を取り出して remarkPluginFrontmatter.h1 に渡す。
 * ページ側で H1 → 本文 の順に並べ、H1 の直下に PR 表記を置けるようにするため。
 */
export function remarkExtractH1() {
  return (tree, file) => {
    const i = tree.children.findIndex((n) => n.type === 'heading' && n.depth === 1);
    if (i < 0) return;
    const [h1] = tree.children.splice(i, 1);
    file.data.astro.frontmatter.h1 = plainText(h1);
  };
}

/**
 * 段落内の改行を <br> にする。原稿は1文ごと・1項目ごとに改行して書いているため。
 * そのままだと改行が空白1つに潰れて、和文の文と文の間に半端な空白が入り、確認日の囲みも1行に詰まる。
 */
export function remarkSoftBreaks() {
  return (tree) => {
    walk(tree, (node) => {
      if (!node.children) return;
      node.children = node.children.flatMap((c) =>
        c.type === 'text' && c.value.includes('\n')
          ? c.value.split(/\r?\n/).flatMap((value, i) => (i === 0 ? [{ type: 'text', value }] : [{ type: 'break' }, { type: 'text', value }]))
          : [c],
      );
    });
  };
}

/** HTML コメントを落とす。`<!-- toc -->` だけは目次の差し込み口として残す。 */
export function remarkStripComments() {
  return (tree) => {
    walk(tree, (node) => {
      if (!node.children) return;
      node.children = node.children.flatMap((c) => {
        if (c.type !== 'html') return [c];
        if (TOC_SLOT.test(c.value)) return [{ type: 'tocSlot', data: { hName: 'div', hProperties: { dataTocSlot: '' } }, children: [] }];
        return COMMENT_ONLY.test(c.value) ? [] : [c];
      });
    });
  };
}

/** `https://…` だけのコードスパンをリンクにする。出典の URL をクリックできるように。 */
export function remarkLinkCodeUrls() {
  return (tree) => {
    walk(tree, (node) => {
      if (node.type === 'link') return false;
      if (!node.children) return;
      node.children = node.children.map((c) =>
        c.type === 'inlineCode' && URL_ONLY.test(c.value) ? { type: 'link', url: c.value, children: [c] } : c,
      );
    });
  };
}

/**
 * 囲み（`>`）に目印を付ける。組み立ては rehypeEleanor。行単位で判定するので remarkSoftBreaks より前に置く。
 *   - `> [!WARNING] 題` / `> [!NOTE]` … 注意・補足（知らない記号はビルドを止める）
 *   - 最終行が「— 出典」の引用 … 出典を blockquote の外（figcaption）に出す（HTML の仕様どおり）
 * 残った `>` は本物の引用だけになる（DADS: 引用ブロックを引用以外に使わない）。
 */
export function remarkCallouts() {
  return (tree, file) => {
    walk(tree, (node) => {
      if (!node.children) return;
      node.children = node.children.map((c) => {
        // 組み替えた figure の中の blockquote にもう一度来るので、一度見たものは飛ばす
        if (c.type !== 'blockquote' || c.data?.seen) return c;
        c.data = { ...c.data, seen: true };
        if (markCallout(c, file)) return c;
        return splitAttribution(c) ?? c;
      });
    });
  };
}

function markCallout(bq, file) {
  const para = bq.children[0];
  const head = para?.type === 'paragraph' ? para.children[0] : null;
  if (head?.type !== 'text') return null;
  const nl = head.value.indexOf('\n');
  const m = (nl < 0 ? head.value : head.value.slice(0, nl)).match(CALLOUT);
  if (!m) return null;
  const kind = CALLOUTS[m[1].toUpperCase()];
  if (!kind) {
    const known = Object.keys(CALLOUTS).map((k) => `[!${k}]`).join(' / ');
    file.fail(`未対応の囲み [!${m[1]}]（使えるのは ${known}）`, head);
  }
  head.value = nl < 0 ? '' : head.value.slice(nl + 1);
  if (!head.value) para.children.shift();
  if (para.children.length === 0) bq.children.shift();
  const title = m[2].trim();
  setProps(bq, { dataCallout: kind, ...(title && { dataCalloutTitle: title }) });
  return kind;
}

/** 最終行（または最後の段落）が「— 出典」なら、figure > blockquote + figcaption に組み替える */
function splitAttribution(bq) {
  const last = bq.children.at(-1);
  if (last?.type !== 'paragraph') return null;
  let caption = null;
  const first = last.children[0];
  if (bq.children.length > 1 && first?.type === 'text' && ATTRIBUTION.test(first.value)) {
    bq.children.pop();
    caption = last.children;
  } else {
    for (let i = last.children.length - 1; i >= 0 && !caption; i--) {
      const c = last.children[i];
      if (c.type !== 'text' || !c.value.includes('\n')) continue;
      const cut = c.value.lastIndexOf('\n');
      const tail = c.value.slice(cut + 1);
      if (!ATTRIBUTION.test(tail)) return null;
      caption = [{ type: 'text', value: tail }, ...last.children.slice(i + 1)];
      last.children = [...last.children.slice(0, i), ...(cut > 0 ? [{ type: 'text', value: c.value.slice(0, cut) }] : [])];
    }
  }
  if (!caption) return null;
  return {
    type: 'quoteFigure',
    data: { hName: 'figure', hProperties: { className: ['quote'] } },
    children: [bq, { type: 'quoteCaption', data: { hName: 'figcaption' }, children: caption }],
  };
}

/**
 * HTML の木を部品に組み立てる。順序は固定（入れ替えると id や表の名前がずれる）:
 *   ① 囲み・番号付きリスト（ここでは見出し要素を作らない）
 *   ② 見出しに id（Astro と同じ rehypeHeadingIds。Astro も後で走らせるが、付いた id はそのまま保たれる）
 *   ③ 表の枠（直前の見出しを枠の名前にする）
 *   ④ 目次（記事だけ）
 */
export function rehypeEleanor() {
  const headingIds = rehypeHeadingIds();
  return (tree, file) => {
    walk(tree, (node) => {
      if (!node.children) return;
      node.children = node.children.map((c) => (c.type === 'element' ? buildBlock(c) : c));
    });
    headingIds(tree, file);
    wrapTables(tree);
    if (isArticle(file)) insertToc(tree);
  };
}

function buildBlock(node) {
  if (node.tagName === 'ol') return numberList(node);
  const kind = node.tagName === 'blockquote' ? node.properties?.dataCallout : null;
  if (!kind) return node;
  const title = node.properties.dataCalloutTitle;
  const body = node.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
  if (kind === 'warning') {
    // 題を書いた場合も「注意」の種類が読み上げで伝わるよう、アイコンに名前を付ける（題が「注意」なら重複するので付けない）
    return el('div', { className: ['banner', 'banner--warning'] }, [
      el('p', { className: ['banner__heading'] }, [icon('warning', title ? '注意' : null), el('span', {}, [txt(title || '注意')])]),
      el('div', { className: ['banner__body'] }, body),
    ]);
  }
  // kind === 'note'
  return el('div', { className: ['notice'] }, [el('p', { className: ['notice__title'] }, [txt(title || '補足')]), ...body]);
}

/** <ol> → <ul> ＋番号を文字で（DADS: <ol> の番号は装飾扱いで、コピーすると消える）。VoiceOver 対策で role="list" */
function numberList(ol) {
  const { start, ...properties } = ol.properties ?? {};
  let n = Number(start ?? 1);
  for (const li of ol.children) {
    if (li.type !== 'element' || li.tagName !== 'li') continue;
    // 項目の間に空行がある（段落の）リストは <li><p>…</p></li> なので、番号は最初の段落の先頭に置く
    const target = li.children.find((c) => c.type === 'element' && c.tagName === 'p') ?? li;
    target.children.unshift(el('span', { className: ['list-number__num'] }, [txt(`${n++}. `)]));
  }
  return el('ul', { ...properties, className: ['list-number'], role: 'list' }, ol.children);
}

/** 表を横スクロールの枠で包み、名前（直前の見出し）を付ける。キーボードでもスクロールできるよう tabindex="0" */
function wrapTables(tree) {
  const found = [];
  let heading = null;
  (function visit(node) {
    for (const [index, c] of (node.children ?? []).entries()) {
      if (c.type !== 'element') continue;
      if (/^h[2-4]$/.test(c.tagName) && c.properties?.id) heading = c;
      if (c.tagName === 'table') found.push({ parent: node, index, table: c, heading });
      else visit(c);
    }
  })(tree);
  const total = new Map();
  for (const f of found) total.set(f.heading, (total.get(f.heading) ?? 0) + 1);
  const seen = new Map();
  found.forEach((f, i) => {
    const thead = f.table.children.find((c) => c.tagName === 'thead');
    if (thead) walk(thead, (n) => void (n.tagName === 'th' && (n.properties.scope = 'col')));
    const k = (seen.get(f.heading) ?? 0) + 1;
    seen.set(f.heading, k);
    const children = [f.table];
    let labelledBy;
    if (f.heading && total.get(f.heading) === 1) {
      labelledBy = [f.heading.properties.id];
    } else {
      // 同じ見出しの下に表が2つ以上（または見出しが無い）→「表1」「表2」を足して区別する
      const id = `table-label-${i + 1}`;
      children.unshift(el('span', { id, className: ['visually-hidden'] }, [txt(`表${k}`)]));
      labelledBy = f.heading ? [f.heading.properties.id, id] : [id];
    }
    f.parent.children[f.index] = el('div', { className: ['table-region'], role: 'region', tabIndex: 0, ariaLabelledBy: labelledBy }, children);
  });
}

/** 本文の H2 が3つ以上なら目次を入れる。位置は `<!-- toc -->`、無ければ最初の H2 の前（DADS: ページの冒頭） */
function insertToc(tree) {
  const h2s = tree.children.filter((c) => c.type === 'element' && c.tagName === 'h2' && c.properties?.id);
  const slot = tree.children.findIndex((c) => c.type === 'element' && c.properties?.dataTocSlot !== undefined);
  if (h2s.length < 3) {
    if (slot >= 0) tree.children.splice(slot, 1);
    return;
  }
  const nav = el('nav', { className: ['toc'], ariaLabelledBy: ['toc-heading'] }, [
    el('h2', { id: 'toc-heading', className: ['toc__heading'] }, [txt('このページの目次')]),
    el(
      'ul',
      { className: ['toc__list'] },
      h2s.map((h) => el('li', {}, [el('a', { href: `#${h.properties.id}` }, [txt(plainText(h))])])),
    ),
  ]);
  if (slot >= 0) tree.children.splice(slot, 1, nav);
  else tree.children.splice(tree.children.indexOf(h2s[0]), 0, nav);
}

// アイコン（24×24）。形は DADS のノティフィケーションバナーに合わせた（丸に i ／三角に !）。色は枠と同じ currentColor
const ICONS = {
  warning: [
    ['path', { d: 'M12 1.8 23 21.4H1Z', fill: 'currentColor', stroke: 'currentColor', strokeWidth: 1.6, strokeLinejoin: 'round' }],
    ['rect', { x: 10.9, y: 8, width: 2.2, height: 8, rx: 1.1, fill: 'Canvas' }],
    ['circle', { cx: 12, cy: 18.2, r: 1.4, fill: 'Canvas' }],
  ],
};
function icon(kind, label) {
  const a11y = label ? { role: 'img', ariaLabel: label } : { ariaHidden: 'true' };
  return el(
    'svg',
    { className: ['banner__icon'], viewBox: '0 0 24 24', width: 24, height: 24, focusable: 'false', ...a11y },
    ICONS[kind].map(([tagName, properties]) => el(tagName, properties, [])),
  );
}

function setProps(node, props) {
  node.data = { ...node.data, hProperties: { ...node.data?.hProperties, ...props } };
}

const el = (tagName, properties, children) => ({ type: 'element', tagName, properties, children });
const txt = (value) => ({ type: 'text', value });

function plainText(node) {
  if (node.type === 'text' || node.type === 'inlineCode') return node.value;
  return (node.children ?? []).map(plainText).join('');
}

function walk(node, fn) {
  if (fn(node) === false) return;
  for (const child of node.children ?? []) walk(child, fn);
}
