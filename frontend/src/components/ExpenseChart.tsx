"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { SectionPanel } from "@/components/SectionPanel";
import { MonthlySummary } from "@/types";

interface ExpenseChartProps {
  data: MonthlySummary[];
}

export function ExpenseChart({ data }: ExpenseChartProps) {
  return (
    <SectionPanel title="Monthly Trend">
      <div className="mt-4 h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 33% 18%)" />
            <XAxis dataKey="month" stroke="hsl(215 20% 55%)" tick={{ fill: "hsl(215 20% 55%)" }} />
            <YAxis stroke="hsl(215 20% 55%)" tick={{ fill: "hsl(215 20% 55%)" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(222 40% 10%)",
                border: "1px solid hsl(217 33% 18%)",
                borderRadius: "0.5rem",
                color: "hsl(210 40% 96%)",
              }}
            />
            <Bar dataKey="income" fill="#34d399" radius={[4, 4, 0, 0]} />
            <Bar dataKey="expense" fill="#f87171" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </SectionPanel>
  );
}
