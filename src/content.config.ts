import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// ブログ記事の正本は content/blog/*.md（README.md は書き方の約束なので除く）。
// ここで落ちた記事はビルドが止まる = 説明文や日付の無い記事は公開されない。
const blog = defineCollection({
  loader: glob({ base: './content/blog', pattern: ['*.md', '!README.md'] }),
  schema: z.object({
    title: z.string().min(10),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    description: z.string().min(50),
    // 集客＝お店・会社の経営者向け／つくったもの＝自社プロダクトの設計の話
    category: z.enum(['集客', 'つくったもの']),
    published_at: z.coerce.date(),
    updated_at: z.coerce.date(),
    // 公開前の下書き。本番のビルドには含めない（確認用のビルドだけ SHOW_DRAFTS=1 で出す）
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
