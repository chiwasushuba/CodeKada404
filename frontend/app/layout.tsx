import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Sidebar } from "@/components/Sidebar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Central Brain",
  description: "Hackathon-ready frontend for Central Brain",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-zinc-950 text-zinc-100">
        <div className="relative min-h-screen overflow-hidden">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(56,189,248,0.13),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.12),transparent_40%)]" />
          <div className="relative mx-auto flex min-h-screen w-full max-w-7xl">
            <Sidebar />
            <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
