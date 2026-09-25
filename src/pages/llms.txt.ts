// /llms.txt（llmstxt.org の形式）。AI の回答や要約がこのサイトを読むときの案内。ビルドのたびに料金データと公開済みの記事から作る。
// 効果は確かめられていない（Google は検索に使わないと明言している）。手間が小さいので置いている。
// 下書きの記事は、確認用のビルド（SHOW_DRAFTS=1）でも載せない。
import type { APIRoute } from 'astro';
import prices from '../data/prices.json';
import { faqs } from '../data/faq.mjs';
import { publishedPosts, postUrl } from '../lib/blog.mjs';
import { yen } from '../lib/format.mjs';
import { SITE, WORKS } from '../site.mjs';

export const GET: APIRoute = async () => {
  const abs = (p: string) => new URL(p, SITE.url).href;
  const minOf = (rows: Record<string, { price: number; billing?: string }>, monthlyOnly = false) =>
    Math.min(...Object.values(rows).filter((r) => !monthlyOnly || r.billing === '月額').map((r) => r.price));
  const tax = prices.tax_included ? '税込' : '税抜';
  const posts = (await publishedPosts()).filter((p) => !p.data.draft);
  const op = SITE.operator;
  const lines = [
    `# ${SITE.name}（${SITE.nameEn}）`,
    '',
    `> ${SITE.description}`,
    '',
    `- 事業者: ${op.name}（個人事業・代表 ${op.representative}）。事業者の方（お店・会社）向けのサービス`,
    `- 所在地: ${op.address}`,
    `- 対応地域: ${SITE.area}`,
    `- 連絡先: [お問い合わせフォーム](${abs('/contact.html')})・${op.email}・${op.phone}（受付時間 ${op.hours.label}。${op.hours.note}）`,
    `- 返信: ${op.reply}（営業日は${op.businessDays}）`,
    `- 料金の目安（${tax}）: LP の制作 ${yen(minOf(prices.plans))}から・ホームページのフルオーダー ${yen(prices.fullorder.fullorder_hp.price)}から・保守 月${yen(minOf(prices.subscriptions, true))}から`,
    '',
    '## サービスと料金',
    '',
    `- [サービスと料金](${abs('/services.html')}): LP の制作、ホームページのフルオーダー制作、公開後の保守と運用、付随する機能の開発。各プランに含まれるものと、保守をやめるときの条件`,
    `- [料金表](${abs('/#lp')}): デザインの種類ごとの料金と納期`,
    `- [LP の見本](${abs('/products.html#samples')}): 架空の店に仕立てた、演出つきとプレミアムの見本の画面`,
    `- [お問い合わせ](${abs('/contact.html')}): ご相談・お見積もりのフォーム（無料）`,
    `- [特定商取引法に基づく表示](${abs('/tokusho.html')}): 取引の条件の全文`,
    '',
    '## よくある質問',
    '',
    ...faqs.map((f) => `- ${f.q} ${f.text}`),
    '',
    '## 事業者と、つくったもの',
    '',
    `- [会社概要・代表プロフィール](${abs('/company.html')})`,
    `- [つくったもの](${abs('/products.html')}): 自分で運営している ${WORKS.kaiyaku.name}（${WORKS.kaiyaku.url}）とこのサイトの設計`,
    '',
    ...(posts.length
      ? ['## ブログ', '', ...posts.map((p) => `- [${p.data.title}](${abs(postUrl(p))}): ${p.data.description}`), '']
      : []),
    '## Optional',
    '',
    `- [サイトポリシー・アクセシビリティ方針](${abs('/site-policy.html')})`,
    '',
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
