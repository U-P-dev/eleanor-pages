import { SITE } from '../site.mjs';

/** パンくずの JSON-LD（BreadcrumbList）。items は Breadcrumb.astro と同じ形（最後が現在のページ・href は現在の URL で補う） */
export function breadcrumbLd(items, currentPath) {
  const trail = [{ label: 'ホーム', href: '/' }, ...items];
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: trail.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.label,
      item: new URL(item.href ?? currentPath, SITE.url).href,
    })),
  };
}
