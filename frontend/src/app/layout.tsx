import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InfiniteMarketCap",
  description: "Global market cap dashboard for macro structure and anomaly tracking.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
