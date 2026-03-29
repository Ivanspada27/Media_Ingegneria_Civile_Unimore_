# 🏗️ Media Ingegneria Civile

Strumento interattivo per gestione voti, simulazione scenari e stima voto di laurea.  
Progetto didattico in Python + Streamlit per Ingegneria Civile — Unimore.

---

## Installazione e avvio

### Prerequisiti
- Python 3.9+
- pip

### Setup (una volta sola)

```bash
# Clona o copia la cartella del progetto, poi:
cd media-ingegneria
pip install -r requirements.txt
```

### Avvio

```bash
streamlit run app.py
```

Si apre automaticamente nel browser all'indirizzo `http://localhost:8501`.

---

## Struttura progetto

```
media-ingegneria/
├── app.py              # Interfaccia Streamlit (UI, pagine, interazione)
├── calcoli.py          # Funzioni di calcolo (media, simulazioni, stime)
├── dati.py             # Definizione piano di studi e strutture dati
├── requirements.txt    # Dipendenze Python
├── dati_esami.json     # ← generato automaticamente al primo salvataggio
└── README.md           # Questo file
```

### Responsabilità dei file

| File | Cosa fa | Quando lo modifichi |
|------|---------|---------------------|
| `dati.py` | Definisce il piano di studi, le configurazioni degli esami a scelta, le strutture dati | Se cambia il piano di studi o vuoi aggiungere esami |
| `calcoli.py` | Contiene tutta la logica: media ponderata, CFU, simulazioni, stima laurea, impatto esami | Se vuoi aggiungere nuovi tipi di calcolo o simulazione |
| `app.py` | L'interfaccia utente: pagine, widget, grafici, salvataggio | Se vuoi cambiare layout, aggiungere pagine, modificare grafici |

---

## Come usarlo

### Inserire voti
1. Vai a **📋 Piano di studi**
2. Spunta "Sostenuto" accanto all'esame
3. Inserisci il voto (18-30) e eventuale lode
4. I dati si salvano automaticamente in `dati_esami.json`

### Simulare scenari
1. Vai a **🔮 Simulatore**
2. Scegli il tipo di simulazione:
   - **Scenario libero**: seleziona esami specifici e assegna voti ipotetici
   - **Scenario uniforme**: "se prendo X in tutti i rimanenti"
   - **Scenari preconfigurati**: confronto conservativo/realistico/ambizioso
   - **Media target**: "che voto medio mi serve per arrivare a 28?"

### Configurare esami a scelta
1. Vai a **⚙️ Impostazioni**
2. Scegli la configurazione (2×9, 3×6, personalizzata...)
3. Clicca "Rigenera piano di studi" — i voti esistenti vengono preservati

---

## Evoluzione del progetto

### Prossimi passi consigliati

1. **Salvataggio multi-sessione**: aggiungere timestamp e storico delle medie nel tempo
2. **Confronto tra sessioni d'esame**: raggruppare gli esami per sessione (invernale, estiva, autunnale)
3. **Dashboard più ricca**: aggiungere grafici radar per aree tematiche (strutture, geotecnica, idraulica)
4. **Export PDF**: generare un report riepilogativo stampabile
5. **Scenario planner avanzato**: ottimizzazione per massimizzare la media dato un budget di studio

### Connessioni con l'ingegneria civile

- Usa le stesse tecniche di modellazione dati che applicherai in geotecnica (parametri, scenari, sensibilità)
- La logica di simulazione è analoga a quella che userai in analisi strutturale (variazione parametrica)
- Streamlit è lo stesso strumento usato per dashboard di monitoraggio in cantiere e project management
