import './globals.css';

export const metadata = {
  title: 'TKD Bağış Potansiyeli Tahmini',
  description: 'Türk Kanser Derneği için şirket bağış potansiyeli tahmin sistemi',
};

export default function RootLayout({ children }) {
  return (
    <html lang="tr">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
