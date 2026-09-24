// eleanor-dev.com の入口。静的なファイル（dist/）の前に必ずここを通す（wrangler.jsonc の run_worker_first）。
//
// なぜ Worker が要るか: URL は「/company.html」の形のまま転送なしで返す必要がある（決済の遷移先・アプリストア・
// 配布済みアプリが直接参照している）。その形で返せるのは html_handling: "none" だけで、none では「/」が
// index.html に引けない。そこで「/」だけをここで index.html に向ける。
const CANONICAL_HOST = 'eleanor-dev.com';
// 本番以外のホスト（確認用のカスタムドメインなど）は、自動生成のページも含めて検索に出さない
const PRODUCTION_HOSTS = new Set([CANONICAL_HOST]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // www と http は本体の https へ（旧サイトの GitHub Pages と同じ振る舞い）
    if (url.hostname === `www.${CANONICAL_HOST}` || (url.protocol === 'http:' && url.hostname === CANONICAL_HOST)) {
      url.hostname = CANONICAL_HOST;
      url.protocol = 'https:';
      return Response.redirect(url.href, 301);
    }

    const assetUrl = new URL(url);
    if (assetUrl.pathname === '/') assetUrl.pathname = '/index.html';
    let response = await env.ASSETS.fetch(new Request(assetUrl, request));
    // 旧サイト（GitHub Pages）は「/company」のような拡張子なしでも開けた。ブックマーク用に .html 付きへ転送する
    if (response.status === 404 && !/\.[a-z0-9]+$/i.test(url.pathname) && url.pathname !== '/') {
      const withHtml = new URL(url);
      withHtml.pathname = url.pathname.replace(/\/$/, '') + '.html';
      const probe = await env.ASSETS.fetch(new Request(withHtml, { method: 'HEAD' }));
      if (probe.ok) return Response.redirect(withHtml.href, 301);
    }
    if (response.status === 404) {
      const notFound = await env.ASSETS.fetch(new Request(new URL('/404.html', url), request));
      response = new Response(notFound.body, { status: 404, headers: notFound.headers });
    } else {
      response = new Response(response.body, response);
    }

    response.headers.set('X-Content-Type-Options', 'nosniff');
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    if (!PRODUCTION_HOSTS.has(url.hostname)) response.headers.set('X-Robots-Tag', 'noindex');
    return response;
  },
};
