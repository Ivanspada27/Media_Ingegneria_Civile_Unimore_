"""
calcoli.py — Funzioni di calcolo per media ponderata, simulazioni e stime

Tutte le funzioni lavorano su liste di dizionari esame (vedi dati.py).
Nessuna funzione modifica i dati originali: restituiscono sempre nuovi valori.
"""

from copy import deepcopy


# ═══════════════════════════════════════════════════════════════
#  CALCOLI BASE
# ═══════════════════════════════════════════════════════════════

def esami_con_voto(piano):
    """Filtra solo gli esami sostenuti che hanno un voto numerico (no idoneità)."""
    return [e for e in piano if e["sostenuto"] and e["tipo"] == "voto" and isinstance(e["voto"], (int, float))]


def media_ponderata(piano):
    """
    Calcola la media ponderata sui CFU degli esami con voto.
    
    Formula: Σ(voto_i × cfu_i) / Σ(cfu_i)
    
    Returns:
        float: media ponderata, oppure 0.0 se nessun esame con voto
    """
    validi = esami_con_voto(piano)
    if not validi:
        return 0.0

    somma_pesata = sum(e["voto"] * e["cfu"] for e in validi)
    somma_cfu = sum(e["cfu"] for e in validi)

    return somma_pesata / somma_cfu


def riepilogo_cfu(piano):
    """
    Calcola il riepilogo dei CFU.
    
    Returns:
        dict con: acquisiti, rimanenti, totali, percentuale, 
                  acquisiti_con_voto, acquisiti_idoneita
    """
    totali = sum(e["cfu"] for e in piano if e["cfu"] > 0)

    acquisiti_voto = sum(e["cfu"] for e in piano 
                         if e["sostenuto"] and e["tipo"] == "voto" and e["cfu"] > 0)
    acquisiti_idoneita = sum(e["cfu"] for e in piano 
                             if e["sostenuto"] and e["tipo"] == "idoneita" and e["cfu"] > 0)
    acquisiti = acquisiti_voto + acquisiti_idoneita

    return {
        "acquisiti": acquisiti,
        "acquisiti_con_voto": acquisiti_voto,
        "acquisiti_idoneita": acquisiti_idoneita,
        "rimanenti": totali - acquisiti,
        "totali": totali,
        "percentuale": (acquisiti / totali * 100) if totali > 0 else 0,
    }


def conta_lodi(piano):
    """Conta il numero di lodi ottenute."""
    return sum(1 for e in piano if e["sostenuto"] and e["lode"])


# ═══════════════════════════════════════════════════════════════
#  STIMA VOTO DI LAUREA
# ═══════════════════════════════════════════════════════════════

def stima_voto_laurea(media, punti_tesi=0, punti_bonus=0):
    """
    Stima il voto di laurea su 110.
    
    La conversione standard è: media × 110 / 30
    I punti tesi e bonus sono approssimativi e variano per ateneo.
    
    ⚠️  Questa è una STIMA. Il regolamento ufficiale di Unimore
        può prevedere criteri diversi (lodi, tempi, commissione).
    
    Args:
        media: media ponderata attuale
        punti_tesi: punti stimati per la prova finale (0-7 indicativo)
        punti_bonus: eventuali punti aggiuntivi (lodi, tempistica, ecc.)
    
    Returns:
        dict con: base_110, con_tesi, con_bonus, nota_disclaimer
    """
    base = media * 110 / 30

    return {
        "base_110": round(base, 2),
        "con_tesi": round(base + punti_tesi, 2),
        "con_bonus": round(base + punti_tesi + punti_bonus, 2),
        "nota": (
            "⚠️ Stima indicativa. Il calcolo effettivo dipende dal regolamento "
            "di Ateneo e dalla commissione di laurea."
        ),
    }


# ═══════════════════════════════════════════════════════════════
#  SIMULAZIONE SCENARI
# ═══════════════════════════════════════════════════════════════

def simula_scenario(piano, modifiche):
    """
    Simula uno scenario applicando voti ipotetici a esami non ancora sostenuti.
    
    NON modifica il piano originale.
    
    Args:
        piano: lista esami originale
        modifiche: dict {nome_esame: voto_ipotetico}
                   oppure lista di dict [{"nome": ..., "voto": ..., "lode": False}, ...]
    
    Returns:
        dict con: piano_simulato, media_simulata, media_attuale, delta, riepilogo
    """
    piano_sim = deepcopy(piano)
    media_attuale = media_ponderata(piano)

    # Normalizza modifiche in formato lista
    if isinstance(modifiche, dict):
        modifiche = [{"nome": k, "voto": v} for k, v in modifiche.items()]

    # Applica le modifiche
    for mod in modifiche:
        for esame in piano_sim:
            if esame["nome"] == mod["nome"]:
                esame["voto"] = mod["voto"]
                esame["lode"] = mod.get("lode", mod["voto"] == 30)
                esame["sostenuto"] = True
                break

    media_sim = media_ponderata(piano_sim)
    riepilogo = riepilogo_cfu(piano_sim)

    return {
        "piano_simulato": piano_sim,
        "media_simulata": round(media_sim, 3),
        "media_attuale": round(media_attuale, 3),
        "delta": round(media_sim - media_attuale, 3),
        "riepilogo": riepilogo,
    }


def scenario_uniforme(piano, voto_uniforme):
    """
    Simula: 'prendo X in tutti gli esami rimanenti'.
    
    Args:
        piano: lista esami
        voto_uniforme: voto da assegnare a tutti gli esami non sostenuti
    
    Returns:
        risultato di simula_scenario
    """
    non_sostenuti = [
        e for e in piano 
        if not e["sostenuto"] and e["tipo"] == "voto"
    ]
    modifiche = {e["nome"]: voto_uniforme for e in non_sostenuti}
    return simula_scenario(piano, modifiche)


def scenari_preconfigurati(piano):
    """
    Genera tre scenari standard: conservativo, realistico, ambizioso.
    
    Returns:
        dict con tre chiavi, ognuna contenente il risultato di scenario_uniforme
    """
    return {
        "Conservativo (24)": scenario_uniforme(piano, 24),
        "Realistico (27)":   scenario_uniforme(piano, 27),
        "Ambizioso (30)":    scenario_uniforme(piano, 30),
    }


def voto_minimo_per_target(piano, media_target):
    """
    Calcola il voto medio minimo necessario nei restanti esami per raggiungere una media target.
    
    Formula inversa della media ponderata:
        voto_necessario = (media_target × cfu_totali_con_voto - somma_pesata_attuale) / cfu_rimanenti_con_voto
    
    Args:
        piano: lista esami
        media_target: media obiettivo (es. 28.0)
    
    Returns:
        dict con: voto_necessario, raggiungibile (bool), nota
    """
    validi = esami_con_voto(piano)
    non_sostenuti_con_voto = [e for e in piano if not e["sostenuto"] and e["tipo"] == "voto"]

    if not non_sostenuti_con_voto:
        return {
            "voto_necessario": None,
            "raggiungibile": False,
            "nota": "Tutti gli esami con voto sono già sostenuti.",
        }

    somma_pesata_attuale = sum(e["voto"] * e["cfu"] for e in validi)
    cfu_attuali = sum(e["cfu"] for e in validi)
    cfu_rimanenti = sum(e["cfu"] for e in non_sostenuti_con_voto)
    cfu_totali = cfu_attuali + cfu_rimanenti

    # media_target = (somma_pesata_attuale + voto_necessario × cfu_rimanenti) / cfu_totali
    # → voto_necessario = (media_target × cfu_totali - somma_pesata_attuale) / cfu_rimanenti
    voto_necessario = (media_target * cfu_totali - somma_pesata_attuale) / cfu_rimanenti

    raggiungibile = 18 <= voto_necessario <= 30

    if voto_necessario < 18:
        nota = f"Bastano voti medi di {voto_necessario:.1f} — già raggiungibile anche con voti bassi."
    elif voto_necessario > 30:
        nota = f"Servirebbe una media di {voto_necessario:.1f} nei rimanenti — non raggiungibile."
    else:
        nota = f"Serve una media di almeno {voto_necessario:.1f} nei prossimi {len(non_sostenuti_con_voto)} esami."

    return {
        "voto_necessario": round(voto_necessario, 2),
        "raggiungibile": raggiungibile,
        "nota": nota,
        "esami_rimanenti": len(non_sostenuti_con_voto),
        "cfu_rimanenti": cfu_rimanenti,
    }


# ═══════════════════════════════════════════════════════════════
#  ANALISI IMPATTO
# ═══════════════════════════════════════════════════════════════

def impatto_esami(piano):
    """
    Calcola il peso relativo di ogni esame sulla media in base ai CFU.
    
    Utile per capire quali esami 'contano di più'.
    
    Returns:
        Lista di dict ordinata per peso decrescente: [{nome, cfu, peso_percentuale}, ...]
    """
    esami_voto = [e for e in piano if e["tipo"] == "voto"]
    cfu_totali = sum(e["cfu"] for e in esami_voto)

    if cfu_totali == 0:
        return []

    impatti = [
        {
            "nome": e["nome"],
            "cfu": e["cfu"],
            "peso_percentuale": round(e["cfu"] / cfu_totali * 100, 1),
            "sostenuto": e["sostenuto"],
            "voto": e["voto"],
        }
        for e in esami_voto
    ]

    return sorted(impatti, key=lambda x: x["cfu"], reverse=True)
