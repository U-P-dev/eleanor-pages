/** Date → 'YYYY-MM-DD'（frontmatter の日付は UTC の 0 時として読まれるので UTC で切る） */
export const ymd = (d) => d.toISOString().slice(0, 10);
