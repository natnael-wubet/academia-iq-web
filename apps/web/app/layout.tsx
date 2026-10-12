import type { Metadata } from "next";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

export const metadata: Metadata = {
  title: "Academia IQ",
  description: "Free research intelligence over OpenAlex, Semantic Scholar, Crossref, and ORCID.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        <SiteHeader />
        {children}
      </body>
    </html>
  );
}
