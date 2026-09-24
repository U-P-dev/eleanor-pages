// 構造化データ（schema.org）。どのページも @id でつないだ 1 つの @graph で出す（組み立ては layouts/Base.astro）。
// 値は画面に出しているものと同じデータ（SITE・prices.json・記事の frontmatter）から作る
// （Google: 構造化データは見えている本文と一致させる。AI の回答用に特別なマークアップは要らない）。
import { SITE } from '../site.mjs';
import { isoJst } from './date.mjs';

export const ORG_ID = `${SITE.url}/#organization`;
export const SITE_ID = `${SITE.url}/#website`;
export const PERSON_ID = `${SITE.url}/company.html#representative`;
export const abs = (path) => new URL(path, SITE.url).href;

/** 事業者。full は会社概要用（番地・郵便番号・設立。ほかのページの画面には市区までしか出ていない） */
export function organization({ full = false } = {}) {
  const op = SITE.operator;
  return {
    '@type': 'Organization',
    '@id': ORG_ID,
    name: op.name,
    alternateName: op.nameEn,
    url: `${SITE.url}/`,
    logo: { '@type': 'ImageObject', url: abs('/logo.png'), width: 512, height: 512 },
    email: op.email,
    telephone: op.phoneIntl,
    areaServed: { '@type': 'Country', name: '日本' },
    founder: { '@id': PERSON_ID },
    address: {
      '@type': 'PostalAddress',
      addressCountry: 'JP',
      addressRegion: op.addressParts.region,
      addressLocality: op.addressParts.locality,
      ...(full ? { postalCode: op.postalCode, streetAddress: op.addressParts.street } : {}),
    },
    ...(full ? { foundingDate: op.founded, description: SITE.description } : {}),
  };
}

/** 代表（勤め先は書かない。worksFor はエレノアだけ） */
export function person() {
  return {
    '@type': 'Person',
    '@id': PERSON_ID,
    name: SITE.operator.representative,
    url: abs('/company.html#profile'),
    jobTitle: '代表',
    worksFor: { '@id': ORG_ID },
  };
}

export function website() {
  return {
    '@type': 'WebSite',
    '@id': SITE_ID,
    url: `${SITE.url}/`,
    name: SITE.name,
    alternateName: SITE.nameEn,
    inLanguage: 'ja',
    publisher: { '@id': ORG_ID },
  };
}

export function webPage({ url, title, description, type = 'WebPage', breadcrumbId, extra = {} }) {
  return {
    '@type': type,
    '@id': `${url}#webpage`,
    url,
    name: title,
    description,
    inLanguage: 'ja',
    isPartOf: { '@id': SITE_ID },
    ...(breadcrumbId ? { breadcrumb: { '@id': breadcrumbId } } : {}),
    ...extra,
  };
}

export function blogPosting({ url, headline, description, published, modified, image }) {
  return {
    '@type': 'BlogPosting',
    '@id': `${url}#article`,
    mainEntityOfPage: { '@id': `${url}#webpage` },
    headline,
    description,
    datePublished: isoJst(published),
    dateModified: isoJst(modified),
    inLanguage: 'ja',
    author: { '@id': PERSON_ID },
    publisher: { '@id': ORG_ID },
    image: image ?? abs('/og.jpg'),
  };
}

/** よくある質問（画面と同じ src/data/faq.mjs から）。Google の FAQ の表示は終わったが、Bing と AI の回答が読む */
export function faqPage({ url, items }) {
  return {
    '@type': 'FAQPage',
    '@id': `${url}#faq`,
    mainEntity: items.map((item) => ({
      '@type': 'Question',
      name: item.q,
      acceptedAnswer: { '@type': 'Answer', text: item.text },
    })),
  };
}

/** 同じ @id のノードは 1 つにまとめる（後に渡したほうの項目が勝つ） */
export function graph(nodes) {
  const byId = new Map();
  const anonymous = [];
  for (const node of nodes) {
    if (!node) continue;
    const id = node['@id'];
    if (!id) anonymous.push(node);
    else byId.set(id, { ...(byId.get(id) ?? {}), ...node });
  }
  return { '@context': 'https://schema.org', '@graph': [...byId.values(), ...anonymous] };
}
