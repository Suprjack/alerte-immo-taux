import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';

// Types de crédit valides
const CREDIT_TYPES = [
  'courtier-immobilier',
  'rachat-credit', 
  'credit-auto',
  'pret-travaux',
  'credit-professionnel',
  'assurance-pret'
];

// Générer les routes statiques
export async function generateStaticParams() {
  const params = [];
  const contentDir = path.join(process.cwd(), 'content', 'pseo');
  
  for (const creditType of CREDIT_TYPES) {
    const typeDir = path.join(contentDir, creditType);
    
    if (fs.existsSync(typeDir)) {
      const files = fs.readdirSync(typeDir);
      
      for (const file of files) {
        if (file.endsWith('.md')) {
          const city = file.replace('.md', '');
          params.push({ creditType, city });
        }
      }
    }
  }
  
  return params;
}

// Générer les métadonnées
export async function generateMetadata({ params }) {
  const { creditType, city } = params;
  const filePath = path.join(process.cwd(), 'content', 'pseo', creditType, `${city}.md`);
  
  if (!fs.existsSync(filePath)) {
    return { title: 'Page non trouvée' };
  }
  
  const fileContent = fs.readFileSync(filePath, 'utf-8');
  const { data } = matter(fileContent);
  
  return {
    title: data.title,
    description: data.description,
    openGraph: {
      title: data.title,
      description: data.description,
      type: 'website',
    },
  };
}

// Composant Page
export default async function CreditCityPage({ params }) {
  const { creditType, city } = params;
  const filePath = path.join(process.cwd(), 'content', 'pseo', creditType, `${city}.md`);
  
  if (!fs.existsSync(filePath)) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <h1 className="text-3xl font-bold text-red-500">Page non trouvée</h1>
      </div>
    );
  }
  
  const fileContent = fs.readFileSync(filePath, 'utf-8');
  const { data, content } = matter(fileContent);
  
  const processedContent = await remark().use(html).process(content);
  const contentHtml = processedContent.toString();
  
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header avec breadcrumb */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <nav className="text-sm text-gray-400">
            <a href="/" className="hover:text-white">Accueil</a>
            <span className="mx-2">/</span>
            <a href={`/${creditType}`} className="hover:text-white">{data.credit_name}</a>
            <span className="mx-2">/</span>
            <span className="text-white">{data.city}</span>
          </nav>
        </div>
      </div>
      
      {/* Contenu principal */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Badge type de crédit */}
        <div className="mb-6">
          <span 
            className="inline-block px-4 py-2 rounded-full text-white text-sm font-semibold"
            style={{ backgroundColor: data.icon === '🏠' ? '#4CAF50' : '#FF9800' }}
          >
            {data.icon} {data.credit_name}
          </span>
        </div>
        
        {/* Titre H1 */}
        <h1 className="text-4xl font-bold text-white mb-4">
          {data.credit_name} à {data.city}
        </h1>
        
        {/* Infos ville */}
        <div className="flex gap-4 text-gray-400 mb-8 text-sm">
          <span>📍 {data.department} - {data.region}</span>
          {data.population && <span>👥 {data.population.toLocaleString()} hab.</span>}
        </div>
        
        {/* CTA Principal */}
        <div className="bg-gradient-to-r from-green-600 to-green-500 rounded-xl p-6 mb-8">
          <p className="text-white text-lg mb-4">
            🎯 Obtenez le meilleur taux pour votre projet à {data.city}
          </p>
          <a 
            href={data.cta_url}
            className="inline-block bg-white text-green-600 font-bold px-8 py-3 rounded-lg hover:bg-gray-100 transition"
          >
            {data.cta_text} →
          </a>
        </div>
        
        {/* Contenu Markdown */}
        <article 
          className="prose prose-invert prose-lg max-w-none
            prose-headings:text-white 
            prose-p:text-gray-300
            prose-a:text-green-400 prose-a:no-underline hover:prose-a:underline
            prose-strong:text-white
            prose-table:text-gray-300
            prose-th:text-white prose-th:bg-gray-800
            prose-td:border-gray-700"
          dangerouslySetInnerHTML={{ __html: contentHtml }}
        />
        
        {/* CTA Footer */}
        <div className="mt-12 bg-gray-800 rounded-xl p-8 text-center">
          <p className="text-xl text-white mb-4">
            Prêt à trouver votre {data.credit_name.toLowerCase()} à {data.city} ?
          </p>
          <a 
            href={data.cta_url}
            className="inline-block bg-green-500 text-white font-bold px-8 py-4 rounded-lg hover:bg-green-600 transition text-lg"
          >
            {data.cta_text} →
          </a>
        </div>
      </main>
    </div>
  );
}

