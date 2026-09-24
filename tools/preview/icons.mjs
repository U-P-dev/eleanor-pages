// public/favicon.svg（ロゴの印）から、アイコン一式を書き出す。印の形を変えたら走らせ直す（開発用。ビルドには含まれない）。
//   node tools/preview/icons.mjs
//   - public/favicon.ico          16・32・48px（検索結果のアイコンは 48px 以上を推奨・SVG だけでは足りない）
//   - public/apple-touch-icon.png 180px・白地（iPhone のホーム画面）
//   - public/logo.png             512px・白地（構造化データの Organization.logo。112px 以上）
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const PUBLIC = path.join(ROOT, 'public');
const svg = fs.readFileSync(path.join(PUBLIC, 'favicon.svg'));

// 透明の地に印だけ（ファビコン）
const bare = (size) => sharp(svg, { density: 72 * (size / 32) * 4 }).resize(size, size).png().toBuffer();
// 白地に余白をとって印を置く（ホーム画面・ロゴ）
async function onWhite(size, pad) {
  const inner = await sharp(svg, { density: 72 * ((size - pad * 2) / 32) * 4 }).resize(size - pad * 2, size - pad * 2).png().toBuffer();
  return sharp({ create: { width: size, height: size, channels: 4, background: '#ffffff' } })
    .composite([{ input: inner, top: pad, left: pad }])
    .png()
    .toBuffer();
}

// ICO は PNG をそのまま入れられる（Vista 以降）。頭 6 バイト＋1 枚 16 バイトの目録＋PNG の本体
function ico(pngs) {
  const head = Buffer.alloc(6 + 16 * pngs.length);
  head.writeUInt16LE(0, 0);
  head.writeUInt16LE(1, 2);
  head.writeUInt16LE(pngs.length, 4);
  let offset = head.length;
  pngs.forEach(({ size, data }, i) => {
    const e = 6 + 16 * i;
    head.writeUInt8(size >= 256 ? 0 : size, e);
    head.writeUInt8(size >= 256 ? 0 : size, e + 1);
    head.writeUInt8(0, e + 2);
    head.writeUInt8(0, e + 3);
    head.writeUInt16LE(1, e + 4);
    head.writeUInt16LE(32, e + 6);
    head.writeUInt32LE(data.length, e + 8);
    head.writeUInt32LE(offset, e + 12);
    offset += data.length;
  });
  return Buffer.concat([head, ...pngs.map((p) => p.data)]);
}

const sizes = [16, 32, 48];
const pngs = await Promise.all(sizes.map(async (size) => ({ size, data: await bare(size) })));
fs.writeFileSync(path.join(PUBLIC, 'favicon.ico'), ico(pngs));
fs.writeFileSync(path.join(PUBLIC, 'apple-touch-icon.png'), await onWhite(180, 26));
fs.writeFileSync(path.join(PUBLIC, 'logo.png'), await onWhite(512, 64));
for (const f of ['favicon.ico', 'apple-touch-icon.png', 'logo.png']) {
  console.log(f, fs.statSync(path.join(PUBLIC, f)).size, 'bytes');
}
