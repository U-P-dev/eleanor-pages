import { getCollection } from 'astro:content';

/** 公開する記事（新しい順）。下書きは確認用のビルド（SHOW_DRAFTS=1）でだけ含める */
export async function publishedPosts() {
  const showDrafts = process.env.SHOW_DRAFTS === '1';
  const posts = await getCollection('blog', (p) => showDrafts || !p.data.draft);
  return posts.sort((a, b) => b.data.published_at.getTime() - a.data.published_at.getTime());
}

export const postUrl = (post) => `/blog/${post.data.slug}.html`;
