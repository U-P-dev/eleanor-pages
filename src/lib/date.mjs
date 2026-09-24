/** Date → 'YYYY-MM-DD'（frontmatter の日付は UTC の 0 時として読まれるので UTC で切る） */
export const ymd = (d) => d.toISOString().slice(0, 10);

const parts = (s) => String(s).slice(0, 10).split('-').map(Number);
/** 'YYYY-MM-DD' → '2026年9月23日' */
export const jaDate = (s) => {
  const [y, m, d] = parts(s);
  return `${y}年${m}月${d}日`;
};
/** 'YYYY-MM-DD' → '2026年9月' */
export const jaMonth = (s) => {
  const [y, m] = parts(s);
  return `${y}年${m}月`;
};
/** 'YYYY-MM-DD' → '2026-09-23T00:00:00+09:00'（構造化データの日時。日本時間の 0 時として書く） */
export const isoJst = (s) => `${String(s).slice(0, 10)}T00:00:00+09:00`;
