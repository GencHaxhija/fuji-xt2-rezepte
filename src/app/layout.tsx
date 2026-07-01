import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Fuji X-T2 Rezepte',
  description: 'Persönliche Fujifilm Rezept-Datenbank',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
