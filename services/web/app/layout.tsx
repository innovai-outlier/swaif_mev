import Sidebar from '@/components/Sidebar';
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Motor Clínico - MEV',
  description: 'Plataforma de gamificação para medicina de estilo de vida',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto bg-gray-50">
            <div className="container mx-auto px-6 py-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
