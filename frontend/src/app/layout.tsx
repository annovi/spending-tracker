import type { Metadata } from "next";
import type { ReactNode } from "react";

import { DM_Sans } from "next/font/google";

import "./globals.css";
import { AppHeader } from "@/components/AppHeader";
import { cn } from "@/lib/utils";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  title: "Spending Tracker",
  description: "Personal finance tracker with CSV import and AI categorization",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={cn("font-sans", dmSans.variable)}>
      <body className="min-h-screen">
        <AppHeader />
        {children}
      </body>
    </html>
  );
}
