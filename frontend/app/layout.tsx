import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "HomeScout — Know your neighborhood before you buy",
  description:
    "AI-powered neighborhood research. Enter any city, neighborhood, or zip code.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${plusJakarta.variable} h-full`}
    >
      <body className="min-h-full flex flex-col bg-[#0f0f0f] font-[family-name:var(--font-display)] antialiased">
        {children}
      </body>
    </html>
  );
}
