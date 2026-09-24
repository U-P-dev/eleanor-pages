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
    founded: '2026',
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
  },
};

// ヘッダーの水平メニュー（DADS: ラベルは行き先のページ名。項目は絞る）
export const NAV = [
  { href: '/services.html', label: 'サービス' },
  { href: '/#lp', label: '料金' },
  { href: '/products.html', label: 'つくったもの' },
  { href: '/blog.html', label: 'ブログ' },
  { href: '/company.html', label: '会社概要' },
];
