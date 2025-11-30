import './globals.css'
import Script from 'next/script'

export const metadata = {
  title: "L'Alerte Immo & Taux | Le Financial Insider",
  description: "Ce que les banques ne vous disent pas sur les taux immobiliers. Mis à jour matin et soir.",
  keywords: "taux immobilier, crédit immobilier, rachat de crédit, OAT 10 ans, Euribor",
}

// Google Analytics ID - à configurer dans Netlify env vars
const GA_ID = process.env.NEXT_PUBLIC_GA_ID || 'G-XXXXXXXXXX';

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <head>
        {/* Google Analytics */}
        <Script
          src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${GA_ID}', {
              page_path: window.location.pathname,
            });
          `}
        </Script>
      </head>
      <body className="min-h-screen">
        {/* Header */}
        <header className="border-b border-gray-800 py-4">
          <div className="max-w-4xl mx-auto px-4 flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold text-yellow-500">
                🔔 L'ALERTE IMMO
              </h1>
              <p className="text-xs text-gray-500">Le Financial Insider</p>
            </div>
            <nav className="flex gap-4 text-sm">
              <a href="/" className="text-gray-400 hover:text-white">Flash Marché</a>
              <a href="/archives" className="text-gray-400 hover:text-white">Archives</a>
              <a href="/calculateur" className="text-yellow-500 font-semibold">💰 Calculer</a>
            </nav>
          </div>
        </header>

        {/* Rates Ticker */}
        <div className="rates-ticker">
          <div className="max-w-4xl mx-auto px-4 flex gap-6 overflow-x-auto">
            <div className="rate-badge rate-up">
              <span>OAT 10 ans</span>
              <span className="font-bold">3.12%</span>
              <span>↑ +0.05</span>
            </div>
            <div className="rate-badge rate-down">
              <span>Euribor 3M</span>
              <span className="font-bold">3.45%</span>
              <span>↓ -0.02</span>
            </div>
            <div className="rate-badge rate-stable">
              <span>Taux moyen 20 ans</span>
              <span className="font-bold">3.89%</span>
              <span>→ 0.00</span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto px-4 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 py-8 mt-12">
          <div className="max-w-4xl mx-auto px-4 text-center text-gray-500 text-sm">
            <p>© 2024 L'Alerte Immo & Taux - Informations à titre indicatif uniquement</p>
            <p className="mt-2">Mis à jour automatiquement 2x par jour</p>
          </div>
        </footer>
      </body>
    </html>
  )
}

