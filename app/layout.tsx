import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css'; // Global styles
import { AppShell } from '@/components/layout/AppShell';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains-mono' });

export const metadata: Metadata = {
  title: 'Podcast Episode Explorer',
  description: 'Search, analyze, and navigate long-form conversations.',
  openGraph: {
    title: 'Podcast Episode Explorer',
    description: 'Search, analyze, and navigate long-form conversations.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Podcast Episode Explorer',
    description: 'Search, analyze, and navigate long-form conversations.',
  },
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="antialiased font-sans" suppressHydrationWarning>
        <AppShell>
          {children}
        </AppShell>
      </body>
    </html>
  );
}
