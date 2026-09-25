// サイト全体の定数。事業者の値は公開済みのもの（特定商取引法に基づく表示と同じ）だけを置く。
export const SITE = {
  name: 'エレノア',
  nameEn: 'Eleanor',
  url: 'https://eleanor-dev.com',
  tagline: '「つくって終わり」に、しない。',
  description:
    '東京・新宿のエレノアは、お店と小さな会社のホームページと LP をつくり、公開後の保守まで同じ開発者が引き受けます。全国からメールとオンラインでご依頼をお受けします。',
  // 対応地域。看板・お問い合わせ・会社概要・よくある質問・フッター・構造化データで同じ言い方にそろえる
  area: '新宿を拠点に、全国からご依頼をお受けします（やりとりはメールとオンライン）。',
  operator: {
    name: 'エレノア',
    nameEn: 'Eleanor',
    representative: '豊島 悠右',
    email: 'contact@eleanor-dev.com',
    phone: '03-4218-8634',
    // 構造化データ用（国番号つき）。表示は上の phone
    phoneIntl: '+81-3-4218-8634',
    postalCode: '160-0022',
    address: '東京都新宿区新宿2丁目8番15号 パークフロント新宿 202号室',
    addressParts: { region: '東京都', locality: '新宿区', street: '新宿2丁目8番15号 パークフロント新宿 202号室' },
    // 開業の日（開業届の提出日）
    founded: '2026-03-06',
    // 電話の受付時間（2026-09-25 👤）。特定商取引法に基づく表示（LP 事業の config の support_hours）と同じ言い方にする
    hours: {
      label: '平日 8:00〜23:00、土日祝 9:00〜18:00',
      note: '出られないときは留守番電話に用件をお残しください。1営業日以内に折り返します。',
      // 構造化データ（ContactPoint）用
      spec: [
        { days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], opens: '08:00', closes: '23:00' },
        { days: ['Saturday', 'Sunday', 'PublicHolidays'], opens: '09:00', closes: '18:00' },
      ],
    },
    // 営業日（納期と返信の日数の数え方）。LP 事業の決定と同じ
    businessDays: '土曜・日曜・祝日を除く平日',
    reply: '原則1営業日以内に、メールでお返事します',
  },
  // Cloudflare Web Analytics のサイトトークン（公開前提の識別子で、秘密ではない）。空のあいだは計測タグを出さない
  analytics: { cloudflareBeaconToken: '' },
};

// 自分でつくって運営しているもの（トップの事例・つくったもの・構造化データで使う）。載せるのは公開中のものだけ
export const WORKS = {
  kaiyaku: {
    name: '解約手帳',
    url: 'https://kaiyaku-techo.com/',
    host: 'kaiyaku-techo.com',
    since: '2026-09-23',
    summary: 'サブスクの解約手順を、公式ページで確かめた日付つきでまとめたサイト',
    // 画面（src/assets/shots/kaiyaku-*.webp）を撮った日。撮り直したら更新する
    shotAt: '2026-09-24',
    // 公開中の記事の本数（サイトマップで数えた日と一緒に。数え直したら両方を更新する）
    articles: { count: 16, countedAt: '2026-09-25' },
  },
};

// ヘッダーの水平メニュー（DADS: ラベルは行き先のページ名。項目は絞る）。お問い合わせはメニューの右のボタン
export const NAV = [
  { href: '/services.html', label: 'サービスと料金' },
  { href: '/products.html', label: 'つくったもの' },
  { href: '/blog.html', label: 'ブログ' },
  { href: '/company.html', label: '会社概要' },
];

// 問い合わせフォームの送り先。LP 事業の受け口（Cloudflare Worker）の「自社サイト用」の番号で、届いたものは
// M8 が 5 分おきに回収して contact@ へ転送する（受け口・番号・回収の仕組みは LP 事業の worker/README.md）。
// どれも公開の HTML に載る値（秘密ではない）。ここ以外に書かない（scripts/check_site.py が見る）
export const CONTACT = {
  endpoint: 'https://form.eleanor-dev.com/f/61034df2214f89b1',
  turnstileSiteKey: '0x4AAAAAAExj4crLxGMaJEXa',
  // 相談の種類（件名に入る）。名前を変えると、よくある質問の文言と受信側の振り分けがずれる
  kinds: ['LP 制作', 'HP 制作', '保守・運用', 'フルオーダー・その他相談', 'アプリについて', 'その他'],
};
