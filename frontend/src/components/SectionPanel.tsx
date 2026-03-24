import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface SectionPanelProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function SectionPanel({ title, description, actions, children, className }: SectionPanelProps) {
  return (
    <div className={cn("rounded-2xl border border-border/60 bg-card/80 p-4 shadow-lg backdrop-blur-sm", className)}>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">{title}</h2>
          {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
      {children}
    </div>
  );
}
