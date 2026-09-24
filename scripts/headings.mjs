// ビルドの後に dist/ の HTML の見出しを仕上げる（npm run build の中で astro build と copy_generated.mjs の後に走る）。
//   1. 見出し（h1〜h4）の文節の区切りに <wbr> を入れる。iPhone の Safari は word-break: auto-phrase が効かないので、
//      CSS の keep-all と組み合わせて「文節の途中で折り返さない」を全ブラウザで揃える（移したページの本文には入れない）
//   2. 見出しとロゴに使っている字だけを、Google Fonts から Zen Kaku Gothic New 700 の woff2 として切り出し、
//      dist/fonts/ に置いてこのサイトから配る（閲覧者の情報を外部に送らない。書体は SIL OFL 1.1・public/fonts/OFL.txt）
//   3. 各ページの <head> に @font-face と preload を差し込む
// 書体の取得に失敗しても終了コードは 0（見出しは本文と同じ OS の書体で出る。scripts/check_site.py が WARN を出す）。
// HEADING_FONT=off で 2 と 3 を飛ばす（書体なしでも組めるかを確かめるとき）。
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.dirname(path.dirname(new URL(import.meta.url).pathname));
const DIST = path.join(ROOT, 'dist');
const FAMILY = 'Zen Kaku Gothic New';
const WEIGHT = 700;
const CSS_NAME = 'Eleanor Heading';
const REPORT = path.join(ROOT, '.astro', 'heading-font.json');
// 自動生成の 3 枚（別の仕組みが書く）と Search Console の確認ファイルには触らない
const SKIP = new Set(['tokusho.html', 'privacy-lp.html', 'terms-lp.html', 'googlef3142e0a3a00e599.html']);
// 旧サイトから移したページ: 本文（div.legal の中）は一字も変えない約束なので <wbr> を入れない（書体の字は集める）
const MIGRATED = new Set(['privacy.html', 'support.html', 'account-deletion.html', 'privacy-hitomoyou.html', 'terms-hitomoyou.html',
  'tokusho-hitomoyou.html', 'support-hitomoyou.html', 'thanks.html', 'cancel.html']);
// Chrome の User-Agent でないと woff2 が返らない
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36';

const HEADING = /<(h[1-4])(\s[^>]*)?>([\s\S]*?)<\/\1>/g;
// 見出しの書体は使わないが、狭い枠で文節の途中で折り返しやすいもの（表の見出しのセル・仕組みの図の文字）にも <wbr> を入れる
const NARROW = /<(th|span)(\s[^>]*?(?:scope=|class="flow__(?:title|body)")[^>]*)>([\s\S]*?)<\/\1>/g;
const LOGO = /<a class="site-logo"[^>]*>([\s\S]*?)<\/a>/g;
const TAGLINE = /<p class="site-footer__tagline">([\s\S]*?)<\/p>/g;

function pages(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...pages(p));
    else if (e.name.endsWith('.html') && !SKIP.has(path.relative(DIST, p))) out.push(p);
  }
  return out;
}

const decode = (s) =>
  s.replace(/&(#x?[0-9a-f]+|amp|lt|gt|quot|#39|nbsp);/gi, (m, e) => {
    const named = { amp: '&', lt: '<', gt: '>', quot: '"', nbsp: ' ' };
    if (named[e.toLowerCase()]) return named[e.toLowerCase()];
    return String.fromCodePoint(e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10));
  });
const textOf = (html) => decode(html.replace(/<[^>]+>/g, ''));

// ── 1. 文節の区切りに <wbr> ─────────────────────────────
const segmenter = new Intl.Segmenter('ja', { granularity: 'word' });
const KANA_ONLY = /^[ぁ-ゟー]+$/; // ひらがな・長音だけの切れ端（助詞・語尾）は前の語に付ける
const CLOSE = /^[、。，．・：；？！）」』】〕〉》”’ー…]+$/; // 閉じ括弧・句読点は前に付ける
const OPEN = /[（「『【〔〈《“‘]$/; // 開き括弧は次の語に付ける
const CJK = /[　-ヿ㐀-鿿＀-￯]/;

function phrases(text) {
  const out = [];
  for (const { segment } of segmenter.segment(text)) {
    const prev = out[out.length - 1];
    if (prev !== undefined && (KANA_ONLY.test(segment) || CLOSE.test(segment) || OPEN.test(prev) || /^\s+$/.test(segment) || /\s$/.test(prev))) {
      out[out.length - 1] = prev + segment;
    } else {
      out.push(segment);
    }
  }
  return out;
}

// 見出しの中の文字の部分だけに <wbr> を入れる（タグ・文字参照はそのまま）。和文どうしの区切りだけに入れる
function withWbr(inner) {
  return inner
    .split(/(<[^>]+>)/)
    .map((part) => {
      if (part.startsWith('<') || !CJK.test(part)) return part;
      // 文字参照を 1 文字として扱うために一度置き換える
      const refs = [];
      const plain = part.replace(/&[#a-z0-9]+;/gi, (m) => {
        refs.push(m);
        return `\u{F0000}${refs.length - 1}\u{F0001}`;
      });
      const joined = phrases(plain)
        .map((p, i, arr) => (i > 0 && CJK.test(arr[i - 1].slice(-1)) && CJK.test(p[0]) ? '<wbr>' : '') + p)
        .join('');
      return joined.replace(/\u{F0000}(\d+)\u{F0001}/gu, (m, n) => refs[Number(n)]);
    })
    .join('');
}

// ── 2. 字を集めて書体を切り出す ─────────────────────────
async function fetchFont(chars) {
  const text = encodeURIComponent(chars);
  const cssUrl = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(FAMILY)}:wght@${WEIGHT}&display=swap&text=${text}`;
  const css = await (await fetch(cssUrl, { headers: { 'User-Agent': UA } })).text();
  const url = css.match(/src:\s*url\((https:\/\/fonts\.gstatic\.com[^)]+)\)/)?.[1];
  if (!url) throw new Error('Google Fonts の CSS に書体の URL が無い');
  const buf = Buffer.from(await (await fetch(url, { headers: { 'User-Agent': UA } })).arrayBuffer());
  if (buf.subarray(0, 4).toString('latin1') !== 'wOF2') throw new Error('woff2 ではないファイルが返った');
  return buf;
}

async function main() {
  const files = pages(DIST);
  const chars = new Set();
  let wbrPages = 0;
  for (const file of files) {
    let html = fs.readFileSync(file, 'utf8');
    const rel = path.relative(DIST, file);
    const legalStart = MIGRATED.has(rel) ? html.indexOf('<div class="legal"') : -1;
    html = html.replace(HEADING, (m, tag, attrs = '', inner, offset) => {
      for (const ch of textOf(inner)) chars.add(ch);
      // 移したページの本文には入れない。すでに入っていれば入れ直さない（何度走らせても同じ結果にする）
      if ((legalStart !== -1 && offset > legalStart) || inner.includes('<wbr>')) return m;
      return `<${tag}${attrs}>${withWbr(inner)}</${tag}>`;
    });
    html = html.replace(NARROW, (m, tag, attrs, inner, offset) => {
      if ((legalStart !== -1 && offset > legalStart) || inner.includes('<wbr>')) return m;
      return `<${tag}${attrs}>${withWbr(inner)}</${tag}>`;
    });
    for (const re of [LOGO, TAGLINE]) for (const [, inner] of html.matchAll(re)) for (const ch of textOf(inner)) chars.add(ch);
    fs.writeFileSync(file, html);
    wbrPages++;
  }
  // 空白・改行は書体に要らない
  const glyphs = [...chars].filter((c) => c.trim()).sort().join('');
  const report = { family: FAMILY, weight: WEIGHT, glyphs: glyphs.length, file: null, bytes: 0, error: null };

  if (process.env.HEADING_FONT === 'off') {
    report.error = 'HEADING_FONT=off（書体を取りに行かなかった）';
  } else {
    try {
      // 通信の一時的な失敗（2026-09-24 に 1 度あった）に備えて 3 回まで試す
      let buf;
      for (let attempt = 1; ; attempt++) {
        try {
          buf = await fetchFont(glyphs);
          break;
        } catch (e) {
          if (attempt >= 3) throw e;
          await new Promise((ok) => setTimeout(ok, 2000 * attempt));
        }
      }
      const name = `heading-${createHash('sha256').update(buf).digest('hex').slice(0, 10)}.woff2`;
      fs.mkdirSync(path.join(DIST, 'fonts'), { recursive: true });
      fs.writeFileSync(path.join(DIST, 'fonts', name), buf);
      const href = `/fonts/${name}`;
      const head =
        `<link rel="preload" href="${href}" as="font" type="font/woff2" crossorigin>` +
        `<style>@font-face{font-family:"${CSS_NAME}";src:url(${href}) format("woff2");font-weight:${WEIGHT};font-style:normal;font-display:swap}</style>`;
      for (const file of files) {
        const html = fs.readFileSync(file, 'utf8').replace(/<link rel="preload" href="\/fonts\/heading-[^"]+"[^>]*><style>@font-face\{font-family:"Eleanor Heading"[^<]*<\/style>/g, '');
        if (html.includes('</head>')) fs.writeFileSync(file, html.replace('</head>', `${head}</head>`));
      }
      report.file = href;
      report.bytes = buf.length;
    } catch (e) {
      report.error = String(e.message || e);
    }
  }
  fs.mkdirSync(path.dirname(REPORT), { recursive: true });
  fs.writeFileSync(REPORT, JSON.stringify({ ...report, chars: glyphs }, null, 2));
  const mark = report.file ? '✅' : '⚠️';
  console.log(
    `${mark} 見出し: <wbr> を ${wbrPages} ページに入れた・字 ${report.glyphs} 種` +
      (report.file ? `・書体 ${report.file}（${(report.bytes / 1024).toFixed(1)}KB）` : `・書体なし（${report.error}）`),
  );
}

main().catch((e) => {
  // ここで止めない（見出しは OS の書体で出る）。check_site.py が WARN にする
  console.error(`⚠️ 見出しの仕上げに失敗: ${e.stack || e}`);
});
