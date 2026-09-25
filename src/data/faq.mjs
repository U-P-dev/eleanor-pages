// よくある質問。画面（サービスのページ）と構造化データ（FAQPage）の両方をここから作る。
// 金額・日数・条件は prices.json（料金の正本から抜き出したもの）から入れる。ここに数字を直書きしない。
// html は画面用（リンクを含む）、text は構造化データ用（タグなしで同じ内容）。
import fs from 'node:fs';
import path from 'node:path';
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

// 事業を続けられなくなったときの約束は、利用規約（LP 事業が生成する terms-lp.html）の第15条が正本。
// よくある質問はその要約なので、条文の要点が変わったらビルドを止める（食い違ったまま公開しない）
const terms = fs
  .readFileSync(path.join(process.cwd(), 'terms-lp.html'), 'utf8')
  .replace(/<[^>]+>/g, '')
  .replace(/\s+/g, ' ');
const art15 = terms.slice(terms.indexOf('第15条'), terms.indexOf('第16条'));
if (!/3 か月前までに登録メールへ通知し、引き渡し版と独自ドメインの移管を無償で行い、年額の前払い分のうち未提供の期間に相当する額を返金/.test(art15)) {
  throw new Error('利用規約 第15条の文言が変わった。src/data/faq.mjs の「続けられなくなったら」の答えを直してから公開する');
}

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
    q: 'ひとりで運営していて、続けられなくなったらどうなりますか？',
    html: `代表ひとりで運営しています。事業の終了や長期の不在でサービスを続けられなくなるときは、3か月前までにお知らせし、LP のファイル一式（引き渡し版）と独自ドメインの移管を無償で行います。年額でお支払いの保守は、残りの期間の分を返金します（<a href="/terms-lp.html">利用規約</a> 第15条）。`,
  },
  {
    q: '請求書払い（後払い）はできますか？',
    html: prices.credit_terms
      ? `できます。お支払いの方法は${methods}です。`
      : `できません。制作費はご注文のときに${prices.payment_timing}でお支払いいただきます（${methods}）。お支払いを確認してから制作に入ります。`,
  },
  {
    q: '「営業日」はいつですか？',
    html: `${SITE.operator.businessDays}です。納期と、お問い合わせへのお返事の日数は、営業日で数えます。お電話は${SITE.operator.hours.label}に受け付けています。`,
  },
  {
    q: 'いま使っているサイトの引っ越しだけを頼めますか？',
    html: `内容によってお受けできます。<a href="/contact.html">お問い合わせ</a>の種類で「${CONTACT.kinds.find((k) => k.startsWith('フルオーダー'))}」を選び、いまの状況をお書きください。`,
  },
];

export const faqs = items.map((item) => ({ ...item, text: strip(item.html) }));
