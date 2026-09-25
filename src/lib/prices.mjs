// 料金データ（prices.json）から、ページで使う数字をつくる。ここで計算し、.astro に金額を直書きしない。
import prices from '../data/prices.json';

export const tax = prices.tax_included ? '税込' : '税抜';
export const taxRate = Math.round(prices.tax_rate * 100);

/** 行の中の最安（月額だけに絞れる） */
export const minOf = (rows, monthlyOnly = false) =>
  Math.min(...Object.values(rows).filter((r) => !monthlyOnly || r.billing === '月額').map((r) => r.price));

export const lpFrom = minOf(prices.plans);
export const careFrom = minOf(prices.subscriptions, true);
export const bundle = prices.plans.bundle_standard;
export const standalone = prices.plans.standalone_standard;
export const fastest = bundle.delivery_days;

/** 公開から 1 年間の合計の例（スタンダードの LP＋保守と、いちばん安い保守を月額で 12 か月・年額で 1 年）。ドメインの費用は別 */
const light = prices.subscriptions.light_monthly;
const lightAnnual = prices.subscriptions.light_annual;
export const firstYear = {
  lp: bundle.price,
  monthly: light.price,
  monthlyTotal: bundle.price + light.price * 12,
  annual: lightAnnual.price,
  annualTotal: bundle.price + lightAnnual.price,
  careName: light.name.replace(/（月額）$/, ''),
};

/** 保守の内容の文を「＋」の区切りで箇条にする（文言は料金データのまま。括弧の中の「＋」では切らない） */
export function splitPlus(text) {
  const out = [];
  let depth = 0;
  let cur = '';
  for (const ch of text) {
    if (ch === '（' || ch === '(') depth++;
    if (ch === '）' || ch === ')') depth = Math.max(0, depth - 1);
    if (ch === '＋' && depth === 0) {
      out.push(cur.trim());
      cur = '';
    } else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}
