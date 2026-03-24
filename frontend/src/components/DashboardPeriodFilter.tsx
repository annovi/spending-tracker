"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const MONTHS = [
  { value: "1", label: "January" },
  { value: "2", label: "February" },
  { value: "3", label: "March" },
  { value: "4", label: "April" },
  { value: "5", label: "May" },
  { value: "6", label: "June" },
  { value: "7", label: "July" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "October" },
  { value: "11", label: "November" },
  { value: "12", label: "December" },
];

function yearOptions(): string[] {
  const current = new Date().getFullYear();
  const start = Math.min(current - 10, 2015);
  const years: string[] = [];
  for (let y = current + 1; y >= start; y -= 1) {
    years.push(String(y));
  }
  return years;
}

interface DashboardPeriodFilterProps {
  year: string;
  month: string;
  onYearChange: (year: string) => void;
  onMonthChange: (month: string) => void;
}

export function DashboardPeriodFilter({
  year,
  month,
  onYearChange,
  onMonthChange,
}: DashboardPeriodFilterProps) {
  const years = yearOptions();

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-xl border border-border/60 bg-card/60 p-4 backdrop-blur-sm">
      <div className="space-y-1.5">
        <Label className="text-muted-foreground">Period</Label>
        <p className="text-xs text-muted-foreground">Filter charts, totals, and the table by year or month.</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <div className="grid gap-1.5">
          <Label htmlFor="dash-year" className="text-xs">
            Year
          </Label>
          <Select
            value={year || "all"}
            onValueChange={(v) => {
              onYearChange(v === "all" ? "" : v);
              if (v === "all") {
                onMonthChange("");
              }
            }}
          >
            <SelectTrigger id="dash-year" className="w-[140px]">
              <SelectValue placeholder="All years" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All years</SelectItem>
              {years.map((y) => (
                <SelectItem key={y} value={y}>
                  {y}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label htmlFor="dash-month" className="text-xs">
            Month
          </Label>
          <Select
            value={month || "all"}
            onValueChange={(v) => onMonthChange(v === "all" ? "" : v)}
            disabled={!year}
          >
            <SelectTrigger id="dash-month" className="w-[160px]">
              <SelectValue placeholder={year ? "All months" : "Pick a year first"} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All months in year</SelectItem>
              {MONTHS.map((m) => (
                <SelectItem key={m.value} value={m.value}>
                  {m.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
