// LP 事業（jido-lp-sales）が GitHub API でリポジトリ直下に書き込む3枚を、ビルドの出力（dist/）へ写す。
// この3枚は向こうの仕組みが本文から組み立てて push するもので、このリポジトリでは手で直さない・動かさない・消さない。
// 1枚でも無ければビルドを止める（特定商取引法の表示が消えたまま公開しないため）。
import { copyFileSync, existsSync } from 'node:fs';

const GENERATED = ['tokusho.html', 'privacy-lp.html', 'terms-lp.html'];
let failed = false;
for (const name of GENERATED) {
  if (!existsSync(name)) {
    console.error(`✗ 自動生成のページ ${name} がリポジトリ直下に無い（jido-lp-sales の公開を確かめる）`);
    failed = true;
    continue;
  }
  if (existsSync(`dist/${name}`)) {
    console.error(`✗ dist/${name} をこのサイトのページが上書きしている（src/pages に同じ名前を作らない）`);
    failed = true;
    continue;
  }
  copyFileSync(name, `dist/${name}`);
}
if (failed) process.exit(1);
console.log(`自動生成のページ ${GENERATED.length} 枚を dist/ へ写した`);
