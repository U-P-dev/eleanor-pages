import { SITE } from '../site.mjs';

/** パンくずの構造化データ（BreadcrumbList）。items は Breadcrumb.astro と同じ形（最後が現在のページ・href は現在の URL で補う） */
export function breadcrumbLd(items, currentPath) {
  const url = new URL(currentPath, SITE.url).href;
  const trail = [{ label: 'ホーム', href: '/' }, ...items];
  return {
    '@type': 'BreadcrumbList',
    '@id': `${url}#breadcrumb`,
    itemListElement: trail.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.label,
      item: new URL(item.href ?? currentPath, SITE.url).href,
    })),
  };
}
