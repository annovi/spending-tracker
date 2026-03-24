"use client";

import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { SectionPanel } from "@/components/SectionPanel";
import { CategoryBreakdown } from "@/types";

const COLORS = ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa", "#2dd4bf", "#fb923c"];

const LABEL_COLOR = "hsl(210 40% 88%)";
const MUTED_LABEL = "hsl(215 20% 65%)";

interface CategoryBreakdownChartProps {
  data: CategoryBreakdown[];
}

export function CategoryBreakdownChart({ data }: CategoryBreakdownChartProps) {
  return (
    <SectionPanel title="Category Breakdown">
      <div className="mt-4 h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="total"
              nameKey="category"
              innerRadius={50}
              outerRadius={90}
              stroke="hsl(222 40% 12%)"
              strokeWidth={2}
            >
              {data.map((entry, index) => (
                <Cell key={entry.category} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(222 40% 10%)",
                border: "1px solid hsl(217 33% 18%)",
                borderRadius: "0.5rem",
                color: LABEL_COLOR,
              }}
              labelStyle={{ color: LABEL_COLOR, fontWeight: 600 }}
              itemStyle={{ color: MUTED_LABEL }}
              formatter={(value: number) =>
                value.toLocaleString("en-CA", { style: "currency", currency: "CAD" })
              }
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              wrapperStyle={{ color: LABEL_COLOR, fontSize: "12px", paddingTop: "8px" }}
              formatter={(value) => <span style={{ color: LABEL_COLOR }}>{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </SectionPanel>
  );
}
