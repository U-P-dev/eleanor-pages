// サイト全体の定数。事業者の値は公開済みのもの（特定商取引法に基づく表示と同じ）だけを置く。
export const SITE = {
  name: 'エレノア',
  nameEn: 'Eleanor',
  url: 'https://eleanor-dev.com',
  tagline: '「つくって終わり」に、しない。',
  description:
    '東京・新宿のエレノアは、お店と小さな会社のホームページと LP をつくり、公開したあとの更新・移行・運用まで同じ開発者が見続けます。',
  operator: {
    name: 'エレノア',
    nameEn: 'Eleanor',
    representative: '豊島 悠右',
    email: 'contact@eleanor-dev.com',
    phone: '03-4218-8634',
    postalCode: '160-0022',
    address: '東京都新宿区新宿2丁目8番15号 パークフロント新宿 202号室',
  },
  // Cloudflare Web Analytics のサイトトークン（公開前提の識別子で、秘密ではない）。空のあいだは計測タグを出さない
  analytics: { cloudflareBeaconToken: '' },
};

// ヘッダーの水平メニュー（DADS: ラベルは行き先のページ名。項目は絞る）
export const NAV = [
  { href: '/services.html', label: 'サービス' },
  { href: '/#lp', label: '料金' },
  { href: '/products.html', label: 'つくったもの' },
  { href: '/blog.html', label: 'ブログ' },
  { href: '/company.html', label: '会社概要' },
];
