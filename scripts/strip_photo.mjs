// 代表の写真を、撮影データ（位置情報・端末名・撮影日時）を消してから src/assets/person/ に置く。
//   node scripts/strip_photo.mjs <元の写真>
// 向きは撮影データどおりに回してから消す。長辺は 1600px まで縮める。元の写真は動かさない（公開リポジトリに入れない）。
// sharp は既定で撮影データを書き出さない（withMetadata を呼ばない）。書き出したあとに撮影データが残っていないことも確かめる。
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const src = process.argv[2];
if (!src || !fs.existsSync(src)) {
  console.error('使い方: node scripts/strip_photo.mjs <元の写真>');
  process.exit(1);
}
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const outDir = path.join(ROOT, 'src', 'assets', 'person');
fs.mkdirSync(outDir, { recursive: true });
for (const f of fs.readdirSync(outDir)) fs.rmSync(path.join(outDir, f));
const out = path.join(outDir, 'representative.jpg');
await sharp(src).rotate().resize({ width: 1600, height: 1600, fit: 'inside', withoutEnlargement: true }).jpeg({ quality: 86, mozjpeg: true }).toFile(out);
const meta = await sharp(out).metadata();
if (meta.exif || meta.xmp || meta.iptc) {
  fs.rmSync(out);
  console.error('撮影データが残ったので書き出しを取り消した');
  process.exit(1);
}
console.log(`書き出した: ${path.relative(ROOT, out)}（${meta.width}×${meta.height}・撮影データなし）`);
