// よくある質問。画面（サービスのページ）と構造化データ（FAQPage）の両方をここから作る。
// 金額・日数・条件は prices.json（料金の正本から抜き出したもの）から入れる。ここに数字を直書きしない。
// html は画面用（リンクを含む）、text は構造化データ用（タグなしで同じ内容）。
import prices from './prices.json';
import { CONTACT, SITE } from '../site.mjs';
import { yen } from '../lib/format.mjs';

const tokusho = (label = '特定商取引法に基づく表示') => `<a href="/tokusho.html">${label}</a>`;
const strip = (html) => html.replace(/<[^>]+>/g, '');

const meeting = prices.fullorder.fullorder_lp.includes.find((line) => line.startsWith('お打ち合わせ'));
// 保守を解約したときの差額（LP単体 − LP＋保守）。デザインの種類ごとに計算し、同じなら 1 つの金額で書く
const diffs = ['standard', 'rich', 'premium']
  .map((t) => prices.plans[`standalone_${t}`]?.price - prices.plans[`bundle_${t}`]?.price)
  .filter((n) => Number.isFinite(n));
const buyout = Math.min(...diffs) === Math.max(...diffs) ? yen(diffs[0]) : `${yen(Math.min(...diffs))}〜${yen(Math.max(...diffs))}`;
const methods = prices.payment_methods.join('・');

const items = [
  {
    q: 'お打ち合わせや電話は必要ですか？',
    html: `LP の制作と保守はメールだけで進みます。フルオーダーは${meeting}があります。お電話の受付時間は${SITE.operator.hours.label}です。${SITE.operator.hours.note}`,
  },
  {
    q: 'どの地域から依頼できますか？',
    html: SITE.area,
  },
  {
    q: '支払いはいつ、どの方法でできますか？',
    html: `${prices.payment_timing}で、${methods}です。お支払いを確認してから制作に入ります。`,
  },
  {
    q: '申し込んだあとで取り消せますか？',
    html: `お支払いから${prices.refund_window_hours}時間以内なら、理由を問わず全額を返金します。それ以降の返金はありません。`,
  },
  {
    q: '公開する前に内容を確かめられますか？',
    html: `はい。公開の前に実物をご確認いただき、手直ししてから公開します。テンプレートから選ぶ LP の手直しは${prices.pre_delivery_revisions}回まで、ご返信から${prices.revision_turnaround}で手直し版をお送りします。`,
  },
  {
    q: '保守メンテナンスはいつやめられますか？',
    html: `${prices.subscription_cancellation}。くわしい条件は${tokusho()}をご覧ください。`,
  },
  {
    q: '保守をやめたら、LP と独自ドメインはどうなりますか？',
    html: `LP＋保守プランでお申し込みの場合、LP単体プランとの差額（${buyout}）をお支払いいただければ、LP${
      prices.buyout_includes_domain ? 'と独自ドメイン' : ''
    }をそのままお持ち帰りいただけます。くわしい条件は${tokusho()}をご覧ください。`,
  },
  {
    q: 'いま使っているサイトの引っ越しだけを頼めますか？',
    html: `内容によってお受けできます。<a href="/contact.html">お問い合わせ</a>の種類で「${CONTACT.kinds.find((k) => k.startsWith('フルオーダー'))}」を選び、いまの状況をお書きください。`,
  },
];

export const faqs = items.map((item) => ({ ...item, text: strip(item.html) }));
