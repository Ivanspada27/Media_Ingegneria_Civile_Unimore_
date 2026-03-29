"""
dati.py — Definizione del piano di studi di Ingegneria Civile (Unimore)

Ogni esame è un dizionario con:
- nome: nome dell'esame
- cfu: crediti formativi
- anno: anno di corso (1, 2, 3)
- tipo: "voto" (esame con voto), "idoneita" (solo superato/non superato), "opzionale" (a scelta)
- voto: None se non sostenuto, intero 18-30 se sostenuto, "idoneo" per idoneità
- lode: True/False (solo se voto == 30)
- sostenuto: True/False
"""

# Piano di studi completo — esami obbligatori
PIANO_STUDI_BASE = [
    # ── Anno 1 ──
    {"nome": "Analisi Matematica I",                "cfu": 9,  "anno": 1, "tipo": "voto"},
    {"nome": "Analisi Matematica II",               "cfu": 9,  "anno": 1, "tipo": "voto"},
    {"nome": "Disegno e CAD",                       "cfu": 6,  "anno": 1, "tipo": "voto"},
    {"nome": "Fisica Generale",                     "cfu": 9,  "anno": 1, "tipo": "voto"},
    {"nome": "Fondamenti di Chimica",               "cfu": 6,  "anno": 1, "tipo": "voto"},
    {"nome": "Geologia Applicata",                  "cfu": 6,  "anno": 1, "tipo": "voto"},
    {"nome": "Geometria",                           "cfu": 9,  "anno": 1, "tipo": "voto"},
    {"nome": "Informatica",                         "cfu": 6,  "anno": 1, "tipo": "voto"},
    {"nome": "Inglese",                             "cfu": 3,  "anno": 1, "tipo": "idoneita"},
    {"nome": "OFA",                                 "cfu": 0,  "anno": 1, "tipo": "idoneita"},

    # ── Anno 2 ──
    {"nome": "Fisica Tecnica",                      "cfu": 9,  "anno": 2, "tipo": "voto"},
    {"nome": "Geomatica",                           "cfu": 9,  "anno": 2, "tipo": "voto"},
    {"nome": "Idraulica e Costruzioni Idrauliche",  "cfu": 12, "anno": 2, "tipo": "voto"},
    {"nome": "Meccanica Razionale",                 "cfu": 9,  "anno": 2, "tipo": "voto"},
    {"nome": "Scienza delle Costruzioni",           "cfu": 9,  "anno": 2, "tipo": "voto"},
    {"nome": "Scienza e Tecnologia dei Materiali",  "cfu": 9,  "anno": 2, "tipo": "voto"},

    # ── Anno 3 ──
    {"nome": "Complementi di Scienza delle Costruzioni", "cfu": 9,  "anno": 3, "tipo": "voto"},
    {"nome": "Dinamica delle Strutture con Lab",         "cfu": 9,  "anno": 3, "tipo": "voto"},
    {"nome": "Geotecnica",                               "cfu": 9,  "anno": 3, "tipo": "voto"},
    {"nome": "Prova Finale",                             "cfu": 3,  "anno": 3, "tipo": "idoneita"},
    {"nome": "Tecnica delle Costruzioni",                "cfu": 12, "anno": 3, "tipo": "voto"},
]

# CFU totali a scelta libera
CFU_OPZIONALI_TOTALI = 18

# Configurazioni possibili per gli esami a scelta
CONFIGURAZIONI_OPZIONALI = {
    "3 esami da 6 CFU":  [6, 6, 6],
    "2 esami da 9 CFU":  [9, 9],
    "1 da 12 + 1 da 6":  [12, 6],
    "1 da 9 + 1 da 6 + 1 da 3": [9, 6, 3],
    "Personalizzata":    [],  # l'utente definisce i propri
}


def crea_esame(nome, cfu, anno, tipo="voto"):
    """Crea un dizionario esame con valori di default."""
    return {
        "nome": nome,
        "cfu": cfu,
        "anno": anno,
        "tipo": tipo,
        "voto": None,
        "lode": False,
        "sostenuto": False,
    }


def genera_piano_completo(config_opzionali="3 esami da 6 CFU", esami_custom=None):
    """
    Genera il piano di studi completo con esami obbligatori + opzionali.
    
    Args:
        config_opzionali: chiave da CONFIGURAZIONI_OPZIONALI
        esami_custom: lista di dict {"nome": ..., "cfu": ...} per config personalizzata
    
    Returns:
        Lista di dizionari esame
    """
    # Copia gli esami base
    piano = [crea_esame(**{k: v for k, v in e.items()}) for e in PIANO_STUDI_BASE]

    # Aggiungi esami opzionali
    if config_opzionali == "Personalizzata" and esami_custom:
        for i, esame in enumerate(esami_custom):
            piano.append(crea_esame(
                nome=esame.get("nome", f"Esame a scelta {i+1}"),
                cfu=esame["cfu"],
                anno=3,
                tipo="voto"
            ))
    else:
        cfu_list = CONFIGURAZIONI_OPZIONALI.get(config_opzionali, [6, 6, 6])
        for i, cfu in enumerate(cfu_list):
            piano.append(crea_esame(
                nome=f"Esame a scelta {i+1}",
                cfu=cfu,
                anno=3,
                tipo="voto"
            ))

    return piano