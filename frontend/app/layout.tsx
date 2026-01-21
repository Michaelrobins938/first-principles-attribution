import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Attribution Matrix - Behavioral Intelligence System",
  description: "Military-grade tactical attribution analysis platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
