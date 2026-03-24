/** Build API query params for optional date range (YYYY-MM-DD). */

export type DateRangeParams = {
  date_from?: string;
  date_to?: string;
};

export function dateRangeFromYearMonth(year: string, month: string): DateRangeParams {
  if (!year.trim()) {
    return {};
  }
  const y = parseInt(year, 10);
  if (Number.isNaN(y)) {
    return {};
  }
  const pad = (n: number) => String(n).padStart(2, "0");
  if (!month.trim()) {
    return { date_from: `${y}-01-01`, date_to: `${y}-12-31` };
  }
  const m = parseInt(month, 10);
  if (Number.isNaN(m) || m < 1 || m > 12) {
    return { date_from: `${y}-01-01`, date_to: `${y}-12-31` };
  }
  const lastDay = new Date(y, m, 0).getDate();
  return {
    date_from: `${y}-${pad(m)}-01`,
    date_to: `${y}-${pad(m)}-${pad(lastDay)}`,
  };
}

export function appendDateRange(searchParams: URLSearchParams, range: DateRangeParams): void {
  if (range.date_from) {
    searchParams.set("date_from", range.date_from);
  }
  if (range.date_to) {
    searchParams.set("date_to", range.date_to);
  }
}
