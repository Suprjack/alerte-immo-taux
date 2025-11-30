'use client';

import { useState, useEffect } from 'react';

// Supabase config
const SUPABASE_URL = 'https://rhsrzffbeiqpciqanjvi.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoc3J6ZmZiZWlxcGNpcWFuanZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0MTU4NzYsImV4cCI6MjA3OTk5MTg3Nn0.-yZ8puHc-9wznPfd_3TxbF6fjitgcPX9hhnkzTkV2dA';

export default function LeadForm({ creditType, city, creditName }) {
  const [formData, setFormData] = useState({
    montant: '',
    prenom: '',
    nom: '',
    email: '',
    telephone: ''
  });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [utmParams, setUtmParams] = useState({});

  // Capturer les UTM params au chargement (pour tracking campagnes)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      setUtmParams({
        utm_source: urlParams.get('utm_source') || '',
        utm_medium: urlParams.get('utm_medium') || '',
        utm_campaign: urlParams.get('utm_campaign') || ''
      });
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Track conversion in Google Analytics
  const trackConversion = () => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'generate_lead', {
        event_category: 'Lead',
        event_label: `${creditType} - ${city}`,
        value: parseInt(formData.montant) || 0
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus({ type: '', message: '' });

    // Données pour Supabase (format BDD)
    const supabaseData = {
      first_name: formData.prenom,
      last_name: formData.nom,
      email: formData.email,
      phone: formData.telephone,
      amount: parseInt(formData.montant) || 0,
      credit_type: creditType,
      city: city,
      source_page: typeof window !== 'undefined' ? window.location.pathname : '',
      ...utmParams
    };

    try {
      // 1. Envoi vers Supabase (priorité - vraie BDD)
      const supabaseResponse = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify(supabaseData)
      });

      if (!supabaseResponse.ok) {
        console.warn('Supabase backup failed, continuing with Formspree');
      }

      // 2. Envoi vers Formspree (backup email)
      const FORMSPREE_ID = process.env.NEXT_PUBLIC_FORMSPREE_ID || 'xpwzgvpd';
      const response = await fetch(`https://formspree.io/f/${FORMSPREE_ID}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          creditType,
          city,
          creditName,
          source: `${creditType}/${city}`,
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok || supabaseResponse.ok) {
        // 3. Track conversion in GA
        trackConversion();

        // 4. Backup localStorage
        const existingLeads = JSON.parse(localStorage.getItem('leads') || '[]');
        existingLeads.push({ ...supabaseData, id: `lead_${Date.now()}` });
        localStorage.setItem('leads', JSON.stringify(existingLeads));

        setStatus({ type: 'success', message: '✅ Demande envoyée ! Un conseiller vous contactera rapidement.' });
        setFormData({ montant: '', prenom: '', nom: '', email: '', telephone: '' });
      } else {
        throw new Error('Erreur serveur');
      }
    } catch (error) {
      // Fallback: sauvegarder en localStorage seulement
      const existingLeads = JSON.parse(localStorage.getItem('leads') || '[]');
      existingLeads.push({ ...supabaseData, id: `lead_${Date.now()}`, status: 'pending' });
      localStorage.setItem('leads', JSON.stringify(existingLeads));

      setStatus({ type: 'success', message: '✅ Demande enregistrée ! Nous vous contacterons bientôt.' });
      setFormData({ montant: '', prenom: '', nom: '', email: '', telephone: '' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 md:p-8 border border-gray-700 shadow-2xl">
      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold text-white mb-2">
          🎯 Obtenez votre {creditName?.toLowerCase() || 'crédit'}
        </h3>
        <p className="text-gray-400">
          Simulation gratuite et sans engagement à {city}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Montant souhaité */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            💰 Montant souhaité (€)
          </label>
          <input
            type="number"
            name="montant"
            value={formData.montant}
            onChange={handleChange}
            placeholder="Ex: 150000"
            required
            min="1000"
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>

        {/* Prénom et Nom */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Prénom
            </label>
            <input
              type="text"
              name="prenom"
              value={formData.prenom}
              onChange={handleChange}
              placeholder="Jean"
              required
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Nom
            </label>
            <input
              type="text"
              name="nom"
              value={formData.nom}
              onChange={handleChange}
              placeholder="Dupont"
              required
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            📧 Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="jean.dupont@email.com"
            required
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>

        {/* Téléphone */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            📱 Téléphone
          </label>
          <input
            type="tel"
            name="telephone"
            value={formData.telephone}
            onChange={handleChange}
            placeholder="06 12 34 56 78"
            required
            pattern="[0-9\s\+]{10,14}"
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>

        {/* Status Message */}
        {status.message && (
          <div className={`p-4 rounded-lg ${status.type === 'success' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`}>
            {status.message}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white font-bold py-4 px-6 rounded-lg hover:from-green-600 hover:to-green-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-lg"
        >
          {isLoading ? '⏳ Envoi en cours...' : '🚀 Recevoir ma simulation gratuite'}
        </button>

        <p className="text-xs text-gray-500 text-center mt-4">
          🔒 Vos données sont protégées et ne seront jamais revendues.
          En soumettant ce formulaire, vous acceptez d'être contacté par un conseiller.
        </p>
      </form>
    </div>
  );
}

