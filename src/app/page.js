import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

// Récupère les articles depuis le dossier content
function getArticles() {
  const articlesDir = path.join(process.cwd(), 'content/articles')
  
  if (!fs.existsSync(articlesDir)) {
    return []
  }

  const files = fs.readdirSync(articlesDir)
    .filter(file => file.endsWith('.md'))
    .sort((a, b) => b.localeCompare(a)) // Plus récent en premier

  return files.slice(0, 10).map(filename => {
    const filePath = path.join(articlesDir, filename)
    const fileContent = fs.readFileSync(filePath, 'utf-8')
    const { data, content } = matter(fileContent)
    
    return {
      slug: filename.replace('.md', ''),
      ...data,
      excerpt: content.slice(0, 200) + '...'
    }
  })
}

// Récupère les données de taux
function getRatesData() {
  const dataPath = path.join(process.cwd(), 'data/rates.json')
  
  if (!fs.existsSync(dataPath)) {
    return {
      oat_10y: { value: 3.12, change: 0.05, direction: 'up' },
      euribor_3m: { value: 3.45, change: -0.02, direction: 'down' },
      taux_20y: { value: 3.89, change: 0, direction: 'stable' },
      updated_at: new Date().toISOString()
    }
  }

  return JSON.parse(fs.readFileSync(dataPath, 'utf-8'))
}

export default function Home() {
  const articles = getArticles()
  const rates = getRatesData()
  const latestFlash = articles.find(a => a.type === 'flash') || articles[0]
  const otherArticles = articles.filter(a => a !== latestFlash)

  return (
    <div>
      {/* Flash Marché du jour */}
      {latestFlash && (
        <div className="flash-market urgence-high">
          <span className="timestamp">
            🔴 FLASH MARCHÉ • {latestFlash.date || 'Aujourd\'hui'}
          </span>
          <h1 className="headline">{latestFlash.title || "Les taux bougent. Voici ce que ça signifie pour vous."}</h1>
          <p className="text-gray-300 leading-relaxed">
            {latestFlash.excerpt}
          </p>
          <a href={`/article/${latestFlash.slug}`} className="text-yellow-500 font-semibold mt-4 inline-block hover:underline">
            Lire l'analyse complète →
          </a>
        </div>
      )}

      {/* CTA Lead Gen */}
      <div className="alert-cta">
        <h3>⚠️ Les taux changent demain ?</h3>
        <p>Vérifiez votre capacité d'emprunt AVANT que ça monte.</p>
        <a href="/calculateur" className="btn">CALCULER MA CAPACITÉ →</a>
      </div>

      {/* Autres articles */}
      <section className="mt-12">
        <h2 className="text-lg font-semibold text-gray-400 mb-6 uppercase tracking-wider">
          📰 Dernières Alertes
        </h2>
        <div className="space-y-6">
          {otherArticles.length > 0 ? (
            otherArticles.map(article => (
              <article key={article.slug} className="article-card">
                <span className="tag">{article.type === 'evening' ? '🌙 Récap Soir' : '☀️ Flash Matin'}</span>
                <h2>{article.title}</h2>
                <p className="excerpt">{article.excerpt}</p>
                <a href={`/article/${article.slug}`} className="text-yellow-500 text-sm mt-4 inline-block">
                  Lire →
                </a>
              </article>
            ))
          ) : (
            <p className="text-gray-500">Aucun article pour le moment. Le prochain flash arrive bientôt...</p>
          )}
        </div>
      </section>

      {/* Signature Insider */}
      <div className="mt-16 text-center border-t border-gray-800 pt-8">
        <p className="text-gray-500 italic text-sm">
          "La fenêtre de tir se referme."
        </p>
        <p className="text-xs text-gray-600 mt-2">— L'Insider</p>
      </div>
    </div>
  )
}

