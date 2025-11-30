'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// Supabase config
const SUPABASE_URL = 'https://rhsrzffbeiqpciqanjvi.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoc3J6ZmZiZWlxcGNpcWFuanZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0MTU4NzYsImV4cCI6MjA3OTk5MTg3Nn0.-yZ8puHc-9wznPfd_3TxbF6fjitgcPX9hhnkzTkV2dA';

export default function AdminDashboard() {
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({ total: 0, new: 0, converted: 0, revenue: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [filter, setFilter] = useState('all');

  // Simple auth (à remplacer par Supabase Auth en prod)
  const handleLogin = (e) => {
    e.preventDefault();
    if (password === 'admin2024') {
      setIsAuthenticated(true);
      localStorage.setItem('admin_auth', 'true');
    } else {
      alert('Mot de passe incorrect');
    }
  };

  useEffect(() => {
    if (localStorage.getItem('admin_auth') === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) fetchLeads();
  }, [isAuthenticated, filter]);

  const fetchLeads = async () => {
    setIsLoading(true);
    try {
      let url = `${SUPABASE_URL}/rest/v1/leads?order=created_at.desc`;
      if (filter !== 'all') url += `&status=eq.${filter}`;

      const response = await fetch(url, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        }
      });
      const data = await response.json();
      setLeads(data || []);

      // Calculer les stats
      const total = data.length;
      const newLeads = data.filter(l => l.status === 'new').length;
      const converted = data.filter(l => l.status === 'converted').length;
      const revenue = data.reduce((sum, l) => sum + (parseFloat(l.revenue) || 0), 0);
      setStats({ total, new: newLeads, converted, revenue });
    } catch (error) {
      console.error('Erreur fetch leads:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateLeadStatus = async (leadId, newStatus) => {
    try {
      await fetch(`${SUPABASE_URL}/rest/v1/leads?id=eq.${leadId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      fetchLeads();
    } catch (error) {
      console.error('Erreur update:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <form onSubmit={handleLogin} className="bg-gray-800 p-8 rounded-xl">
          <h1 className="text-2xl font-bold text-white mb-6">🔐 Admin Dashboard</h1>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Mot de passe"
            className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white mb-4"
          />
          <button type="submit" className="w-full bg-green-600 text-white py-3 rounded-lg">
            Connexion
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">📊 Dashboard Leads</h1>
          <Link href="/" className="text-gray-400 hover:text-white">← Retour au site</Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <p className="text-gray-400 text-sm">Total Leads</p>
            <p className="text-3xl font-bold text-white">{stats.total}</p>
          </div>
          <div className="bg-blue-900/50 p-6 rounded-xl">
            <p className="text-blue-300 text-sm">Nouveaux</p>
            <p className="text-3xl font-bold text-blue-400">{stats.new}</p>
          </div>
          <div className="bg-green-900/50 p-6 rounded-xl">
            <p className="text-green-300 text-sm">Convertis</p>
            <p className="text-3xl font-bold text-green-400">{stats.converted}</p>
          </div>
          <div className="bg-yellow-900/50 p-6 rounded-xl">
            <p className="text-yellow-300 text-sm">Revenus</p>
            <p className="text-3xl font-bold text-yellow-400">{stats.revenue.toFixed(0)}€</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-4">
          {['all', 'new', 'contacted', 'converted', 'lost'].map((f) => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg ${filter === f ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300'}`}>
              {f === 'all' ? 'Tous' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Leads Table */}
        <div className="bg-gray-800 rounded-xl overflow-hidden">
          {isLoading ? (
            <p className="p-8 text-center text-gray-400">Chargement...</p>
          ) : leads.length === 0 ? (
            <p className="p-8 text-center text-gray-400">Aucun lead pour le moment</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="p-4 text-gray-300">Date</th>
                    <th className="p-4 text-gray-300">Nom</th>
                    <th className="p-4 text-gray-300">Contact</th>
                    <th className="p-4 text-gray-300">Montant</th>
                    <th className="p-4 text-gray-300">Type</th>
                    <th className="p-4 text-gray-300">Ville</th>
                    <th className="p-4 text-gray-300">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {leads.map((lead) => (
                    <tr key={lead.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                      <td className="p-4 text-gray-400 text-sm">
                        {new Date(lead.created_at).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="p-4 text-white">{lead.first_name} {lead.last_name}</td>
                      <td className="p-4">
                        <div className="text-sm text-gray-300">{lead.email}</div>
                        <div className="text-sm text-gray-500">{lead.phone}</div>
                      </td>
                      <td className="p-4 text-green-400 font-bold">{lead.amount?.toLocaleString()}€</td>
                      <td className="p-4 text-gray-300">{lead.credit_type}</td>
                      <td className="p-4 text-gray-300">{lead.city}</td>
                      <td className="p-4">
                        <select value={lead.status || 'new'} onChange={(e) => updateLeadStatus(lead.id, e.target.value)}
                          className="bg-gray-600 text-white px-2 py-1 rounded text-sm">
                          <option value="new">🆕 Nouveau</option>
                          <option value="contacted">📞 Contacté</option>
                          <option value="converted">✅ Converti</option>
                          <option value="lost">❌ Perdu</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

