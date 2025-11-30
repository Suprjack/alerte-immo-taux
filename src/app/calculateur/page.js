'use client'

import { useState } from 'react'

export default function Calculateur() {
  const [revenus, setRevenus] = useState('')
  const [apport, setApport] = useState('')
  const [duree, setDuree] = useState('20')
  const [result, setResult] = useState(null)

  const calculer = (e) => {
    e.preventDefault()
    
    const rev = parseFloat(revenus) || 0
    const app = parseFloat(apport) || 0
    const dur = parseInt(duree)
    
    // Calcul simplifié (33% d'endettement max)
    const mensualiteMax = rev * 0.33
    const tauxAnnuel = 0.0389 // Taux moyen actuel
    const tauxMensuel = tauxAnnuel / 12
    const nbMensualites = dur * 12
    
    // Formule de capacité d'emprunt
    const capacite = mensualiteMax * ((1 - Math.pow(1 + tauxMensuel, -nbMensualites)) / tauxMensuel)
    const budgetTotal = capacite + app

    setResult({
      capacite: Math.round(capacite),
      budget: Math.round(budgetTotal),
      mensualite: Math.round(mensualiteMax)
    })
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">💰 Calculateur de Capacité d'Emprunt</h1>
      <p className="text-gray-400 mb-8">Découvrez combien vous pouvez emprunter en 30 secondes.</p>

      <form onSubmit={calculer} className="bg-gray-900 p-8 rounded-2xl border border-gray-800">
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Revenus nets mensuels (€)</label>
          <input
            type="number"
            value={revenus}
            onChange={(e) => setRevenus(e.target.value)}
            placeholder="Ex: 3500"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
            required
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Apport personnel (€)</label>
          <input
            type="number"
            value={apport}
            onChange={(e) => setApport(e.target.value)}
            placeholder="Ex: 30000"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Durée du prêt</label>
          <select
            value={duree}
            onChange={(e) => setDuree(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
          >
            <option value="15">15 ans</option>
            <option value="20">20 ans</option>
            <option value="25">25 ans</option>
          </select>
        </div>

        <button
          type="submit"
          className="w-full bg-yellow-500 text-black font-bold py-4 rounded-lg hover:bg-yellow-400 transition-all"
        >
          CALCULER MA CAPACITÉ →
        </button>
      </form>

      {result && (
        <div className="mt-8 bg-gradient-to-br from-green-900/50 to-green-800/30 p-8 rounded-2xl border border-green-700">
          <h2 className="text-xl font-bold mb-4">📊 Votre capacité d'emprunt</h2>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-black/30 p-4 rounded-lg">
              <p className="text-sm text-gray-400">Capacité d'emprunt</p>
              <p className="text-2xl font-bold text-green-400">{result.capacite.toLocaleString()} €</p>
            </div>
            <div className="bg-black/30 p-4 rounded-lg">
              <p className="text-sm text-gray-400">Budget total</p>
              <p className="text-2xl font-bold text-yellow-400">{result.budget.toLocaleString()} €</p>
            </div>
          </div>

          <p className="text-sm text-gray-400">
            Mensualité maximale: <strong>{result.mensualite} €/mois</strong> (33% d'endettement)
          </p>

          <div className="alert-cta mt-6">
            <h3>🎯 Obtenez une offre personnalisée</h3>
            <p>Un courtier peut vous faire économiser jusqu'à 0.3% sur votre taux.</p>
            <a href="#" className="btn">ÊTRE RAPPELÉ GRATUITEMENT →</a>
          </div>
        </div>
      )}

      <p className="text-xs text-gray-600 mt-8 text-center">
        *Simulation indicative basée sur un taux de 3.89%. Consultez un professionnel pour une offre définitive.
      </p>
    </div>
  )
}

