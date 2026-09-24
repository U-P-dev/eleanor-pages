// @ts-check
import { readdirSync, readFileSync } from 'node:fs';
import { unified } from '@astrojs/markdown-remark';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';
import {
  rehypeEleanor,
  remarkCallouts,
  remarkExtractH1,
  remarkLinkCodeUrls,
  remarkSoftBreaks,
  remarkStripComments,
} from './src/lib/markdown.mjs';
import { SITE } from './src/site.mjs';

// 記事ごとの updated_at（sitemap の lastmod）。設定ファイルからは getCollection を呼べないので frontmatter を直接読む
function articleUpdatedAt() {
  const dir = new URL('./content/blog/', import.meta.url);
  const dates = new Map();
  for (const name of readdirSync(dir)) {
    if (!name.endsWith('.md') || name === 'README.md') continue;
    const fm = readFileSync(new URL(name, dir), 'utf8').match(/^---\n([\s\S]*?)\n---/)?.[1] ?? '';
    const slug = fm.match(/^slug:\s*(\S+)/m)?.[1];
    const updated = fm.match(/^updated_at:\s*(\d{4}-\d{2}-\d{2})/m)?.[1];
    if (slug && updated) dates.set(`/blog/${slug}.html`, updated);
  }
  return dates;
}
// 固定ページの最終更新日（src/data/updated.json。中身を変えたときだけ更新する）と記事の updated_at を合わせる
const pageUpdated = JSON.parse(readFileSync(new URL('./src/data/updated.json', import.meta.url), 'utf8'));
const updatedAt = new Map([...Object.entries(pageUpdated).filter(([k]) => k.startsWith('/')), ...articleUpdatedAt()]);

// 本番の URL は「/company.html」の形（Stripe・アプリストア・アプリ内のリンクが依存しているので変えない）
export default defineConfig({
  site: SITE.url,
  build: { format: 'file' },
  trailingSlash: 'never',
  integrations: [
    sitemap({
      // LP 事業が自動生成して直下に置く3枚も載せる（このビルドでは作らないので自動では拾われない）
      customPages: ['tokusho.html', 'privacy-lp.html', 'terms-lp.html'].map((p) => `${SITE.url}/${p}`),
      // 決済の完了・取消の画面と 404 は検索に出さない。llms.txt などページでないものも載せない
      filter: (page) => {
        const p = new URL(page).pathname;
        return !/\/(404|thanks|cancel)(\.html)?$/.test(p) && !/\.(txt|xml|json)$/.test(p);
      },
      serialize(item) {
        // format: 'file' の URL は拡張子つき（/company.html）。sitemap は拡張子なしで出すので、実際の URL に揃える
        const url = new URL(item.url);
        if (url.pathname !== '/' && !url.pathname.endsWith('.html')) url.pathname += '.html';
        const lastmod = updatedAt.get(url.pathname);
        return { ...item, url: url.href, ...(lastmod && { lastmod }) };
      },
    }),
  ],
  markdown: {
    processor: unified({
      // 和文の引用符・ダッシュを英文用に書き換えさせない
      smartypants: false,
      remarkPlugins: [remarkStripComments, remarkExtractH1, remarkCallouts, remarkLinkCodeUrls, remarkSoftBreaks],
      rehypePlugins: [rehypeEleanor],
    }),
  },
});
