import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Stockage local des leads (en production, utiliser une vraie DB)
const LEADS_FILE = path.join(process.cwd(), 'data', 'leads.json');

// Validation email
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Validation téléphone français
function isValidPhone(phone) {
  const cleaned = phone.replace(/[\s\-\.]/g, '');
  return /^(\+33|0)[1-9][0-9]{8}$/.test(cleaned);
}

export async function POST(request) {
  try {
    const body = await request.json();
    
    const { montant, prenom, nom, email, telephone, creditType, city, creditName, source, timestamp } = body;

    // Validation des champs obligatoires
    if (!montant || !prenom || !nom || !email || !telephone) {
      return NextResponse.json(
        { error: 'Tous les champs sont obligatoires' },
        { status: 400 }
      );
    }

    // Validation du montant
    const montantNum = parseInt(montant);
    if (isNaN(montantNum) || montantNum < 1000) {
      return NextResponse.json(
        { error: 'Le montant doit être au minimum de 1000€' },
        { status: 400 }
      );
    }

    // Validation email
    if (!isValidEmail(email)) {
      return NextResponse.json(
        { error: 'Adresse email invalide' },
        { status: 400 }
      );
    }

    // Validation téléphone
    if (!isValidPhone(telephone)) {
      return NextResponse.json(
        { error: 'Numéro de téléphone invalide (format français attendu)' },
        { status: 400 }
      );
    }

    // Créer le lead
    const lead = {
      id: `lead_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      montant: montantNum,
      prenom: prenom.trim(),
      nom: nom.trim(),
      email: email.toLowerCase().trim(),
      telephone: telephone.replace(/[\s\-\.]/g, ''),
      creditType: creditType || 'unknown',
      city: city || 'unknown',
      creditName: creditName || 'Crédit',
      source: source || 'direct',
      timestamp: timestamp || new Date().toISOString(),
      status: 'new',
      createdAt: new Date().toISOString()
    };

    // Sauvegarder le lead
    let leads = [];
    
    // Créer le dossier data s'il n'existe pas
    const dataDir = path.join(process.cwd(), 'data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    // Lire les leads existants
    if (fs.existsSync(LEADS_FILE)) {
      const content = fs.readFileSync(LEADS_FILE, 'utf-8');
      try {
        leads = JSON.parse(content);
      } catch {
        leads = [];
      }
    }

    // Ajouter le nouveau lead
    leads.push(lead);

    // Sauvegarder
    fs.writeFileSync(LEADS_FILE, JSON.stringify(leads, null, 2), 'utf-8');

    console.log(`📧 Nouveau lead reçu: ${lead.prenom} ${lead.nom} - ${lead.email} - ${lead.creditType}/${lead.city} - ${lead.montant}€`);

    return NextResponse.json({
      success: true,
      message: 'Lead enregistré avec succès',
      leadId: lead.id
    });

  } catch (error) {
    console.error('Erreur lors de l\'enregistrement du lead:', error);
    return NextResponse.json(
      { error: 'Erreur serveur. Veuillez réessayer.' },
      { status: 500 }
    );
  }
}

// GET pour récupérer les leads (protégé)
export async function GET(request) {
  // En production, ajouter une authentification ici
  const { searchParams } = new URL(request.url);
  const apiKey = searchParams.get('key');
  
  // Simple protection par clé API (à remplacer par une vraie auth)
  if (apiKey !== process.env.LEADS_API_KEY && apiKey !== 'admin123') {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 });
  }

  try {
    if (!fs.existsSync(LEADS_FILE)) {
      return NextResponse.json({ leads: [], count: 0 });
    }

    const content = fs.readFileSync(LEADS_FILE, 'utf-8');
    const leads = JSON.parse(content);

    return NextResponse.json({
      leads,
      count: leads.length,
      lastUpdate: new Date().toISOString()
    });

  } catch (error) {
    return NextResponse.json({ error: 'Erreur lecture leads' }, { status: 500 });
  }
}

