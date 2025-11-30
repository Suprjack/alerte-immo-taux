import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { remark } from 'remark'
import html from 'remark-html'

// Génère les routes statiques pour toutes les pages pSEO
export async function generateStaticParams() {
  const pseoDir = path.join(process.cwd(), 'content/pseo')
  
  if (!fs.existsSync(pseoDir)) {
    return []
  }

  const files = fs.readdirSync(pseoDir).filter(f => f.endsWith('.md'))
  
  return files.map(filename => ({
    slug: [filename.replace('.md', '')]
  }))
}

async function getPageContent(slug) {
  const filePath = path.join(process.cwd(), 'content/pseo', `${slug}.md`)
  
  if (!fs.existsSync(filePath)) {
    return null
  }

  const fileContent = fs.readFileSync(filePath, 'utf-8')
  const { data, content } = matter(fileContent)
  
  const processedContent = await remark()
    .use(html)
    .process(content)
  
  return {
    frontmatter: data,
    content: processedContent.toString()
  }
}

export async function generateMetadata({ params }) {
  const slug = params.slug?.join('/') || ''
  const page = await getPageContent(slug)
  
  if (!page) {
    return { title: 'Page non trouvée' }
  }

  return {
    title: page.frontmatter.title,
    description: page.frontmatter.description,
  }
}

export default async function DynamicPage({ params }) {
  const slug = params.slug?.join('/') || ''
  const page = await getPageContent(slug)

  if (!page) {
    return (
      <div className="text-center py-20">
        <h1 className="text-2xl font-bold">Page non trouvée</h1>
        <a href="/" className="text-yellow-500 mt-4 inline-block">← Retour à l'accueil</a>
      </div>
    )
  }

  return (
    <article className="prose prose-invert max-w-none">
      <div 
        dangerouslySetInnerHTML={{ __html: page.content }} 
        className="pseo-content"
      />
      
      {/* CTA Lead Gen injecté automatiquement */}
      <div className="alert-cta mt-8">
        <h3>⚠️ Les taux changent demain ?</h3>
        <p>Vérifiez votre capacité d'emprunt AVANT que ça monte.</p>
        <a href="/calculateur" className="btn">CALCULER MA CAPACITÉ →</a>
      </div>
    </article>
  )
}

