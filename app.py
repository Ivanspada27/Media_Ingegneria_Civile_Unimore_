"""
app.py — Media Ingegneria Civile — Streamlit App

Interfaccia interattiva per gestione voti, simulazione scenari
e stima voto di laurea per Ingegneria Civile (Unimore).

Avvio:  streamlit run app.py
"""

import json
import os
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from dati import genera_piano_completo, CONFIGURAZIONI_OPZIONALI, CFU_OPZIONALI_TOTALI
from calcoli import (
    media_ponderata,
    riepilogo_cfu,
    conta_lodi,
    stima_voto_laurea,
    simula_scenario,
    scenario_uniforme,
    scenari_preconfigurati,
    voto_minimo_per_target,
    impatto_esami,
)

# ═══════════════════════════════════════════════════════════════
#  CONFIGURAZIONE PAGINA
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Media Ingegneria Civile",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

FILE_DATI = Path("dati_esami.json")

# ═══════════════════════════════════════════════════════════════
#  TEMA E CSS PERSONALIZZATO
# ═══════════════════════════════════════════════════════════════

if "tema" not in st.session_state:
    st.session_state.tema = "scuro"

def get_css():
    is_dark = st.session_state.tema == "scuro"
    
    if is_dark:
        bg = "#0e1117"
        bg_card = "#1a1f2e"
        text = "#e2e8f0"
        text_muted = "#94a3b8"
        accent = "#6366f1"
        accent_light = "#818cf8"
        accent_bg = "rgba(99, 102, 241, 0.1)"
        success = "#22c55e"
        border = "#2d3548"
        input_bg = "#1e2433"
        sidebar_bg = "#0b0f1a"
        divider = "#2d3548"
    else:
        bg = "#f8fafc"
        bg_card = "#ffffff"
        text = "#1e293b"
        text_muted = "#64748b"
        accent = "#4f46e5"
        accent_light = "#6366f1"
        accent_bg = "rgba(79, 70, 229, 0.06)"
        success = "#16a34a"
        border = "#e2e8f0"
        input_bg = "#f1f5f9"
        sidebar_bg = "#ffffff"
        divider = "#e2e8f0"

    return f"""
    <style>
        .stApp {{
            background-color: {bg};
            color: {text};
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
            border-right: 1px solid {border};
        }}
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown span {{
            color: {text};
        }}
        
        h1, h2, h3 {{
            color: {text} !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}
        h1 {{ font-size: 2rem !important; margin-bottom: 0.5rem !important; }}
        h2 {{ font-size: 1.4rem !important; margin-top: 1.5rem !important; }}
        h3 {{ font-size: 1.1rem !important; color: {text_muted} !important; }}
        
        div[data-testid="stMetric"] {{
            background-color: {bg_card};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1rem 1.25rem;
        }}
        div[data-testid="stMetric"] label {{
            color: {text_muted} !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            color: {text} !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            background-color: {bg_card};
            border-radius: 10px;
            padding: 4px;
            border: 1px solid {border};
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            color: {text_muted};
            font-weight: 500;
            padding: 0.5rem 1rem;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {accent} !important;
            color: white !important;
            border-radius: 8px;
        }}
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {{
            display: none;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {accent}, {accent_light});
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
        }}
        
        .stNumberInput input,
        .stTextInput input,
        .stSelectbox > div > div {{
            background-color: {input_bg} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
            color: {text} !important;
        }}
        .stNumberInput input:focus,
        .stTextInput input:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 2px {accent_bg} !important;
        }}
        
        .stCheckbox label span {{
            color: {text} !important;
            font-weight: 500;
        }}
        
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {accent}, {accent_light}) !important;
            border-radius: 999px;
        }}
        .stProgress > div > div > div {{
            background-color: {border} !important;
            border-radius: 999px;
        }}
        
        hr {{ border-color: {divider} !important; opacity: 0.5; }}
        .stAlert {{ border-radius: 10px; border: none; }}
        
        .stRadio > div {{ gap: 2px !important; }}
        .stRadio > div > label {{
            background-color: transparent;
            border-radius: 8px;
            padding: 0.5rem 0.75rem !important;
            transition: background-color 0.15s ease;
            color: {text} !important;
        }}
        .stRadio > div > label:hover {{
            background-color: {accent_bg};
        }}
        
        .stMultiSelect > div > div {{
            background-color: {input_bg} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
        }}
        
        .stDownloadButton > button {{
            background: transparent !important;
            border: 1px solid {border} !important;
            color: {text} !important;
            box-shadow: none !important;
        }}
        .stDownloadButton > button:hover {{
            border-color: {accent} !important;
            color: {accent} !important;
        }}
        
        .anno-badge {{
            display: inline-block;
            background: linear-gradient(135deg, {accent}, {accent_light});
            color: white;
            padding: 0.3rem 1rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.85rem;
            letter-spacing: 0.03em;
            margin: 1.2rem 0 0.8rem 0;
        }}
        
        .footer {{
            color: {text_muted};
            text-align: center;
            padding: 2rem 0 1rem 0;
            font-size: 0.8rem;
        }}
        
        section[data-testid="stSidebar"] div[data-testid="stMetric"] {{
            background-color: {accent_bg};
            border: 1px solid transparent;
        }}
        section[data-testid="stSidebar"] div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            color: {accent_light} !important;
            font-size: 1.5rem !important;
        }}
        
        .stCaption, small {{ color: {text_muted} !important; }}
        div[data-testid="stToast"] {{ border-radius: 10px; }}
    </style>
    """


# ═══════════════════════════════════════════════════════════════
#  SALVATAGGIO E CARICAMENTO
# ═══════════════════════════════════════════════════════════════

def salva_dati(piano):
    with open(FILE_DATI, "w", encoding="utf-8") as f:
        json.dump(piano, f, ensure_ascii=False, indent=2)

def carica_dati():
    if FILE_DATI.exists():
        with open(FILE_DATI, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def inizializza_piano():
    dati_salvati = carica_dati()
    if dati_salvati:
        return dati_salvati
    return genera_piano_completo("3 esami da 6 CFU")


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════

if "piano" not in st.session_state:
    st.session_state.piano = inizializza_piano()
if "scenari_salvati" not in st.session_state:
    st.session_state.scenari_salvati = {}

st.markdown(get_css(), unsafe_allow_html=True)


def plotly_template():
    is_dark = st.session_state.tema == "scuro"
    return {
        "template": "plotly_dark" if is_dark else "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font_color": "#e2e8f0" if is_dark else "#1e293b",
    }


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    col_title, col_toggle = st.columns([3, 1])
    with col_title:
        st.markdown("## 🎓 Media")
        st.caption("Ingegneria Civile · Unimore")
    with col_toggle:
        tema_icon = "☀️" if st.session_state.tema == "scuro" else "🌙"
        if st.button(tema_icon, key="tema_btn", help="Cambia tema"):
            st.session_state.tema = "chiaro" if st.session_state.tema == "scuro" else "scuro"
            st.rerun()

    st.divider()

    media = media_ponderata(st.session_state.piano)
    riepilogo = riepilogo_cfu(st.session_state.piano)

    if media > 0:
        st.metric("Media ponderata", f"{media:.2f}")
        laurea = stima_voto_laurea(media)
        st.metric("Stima laurea", f"{laurea['base_110']}/110")
    else:
        st.metric("Media ponderata", "—")

    st.metric("CFU", f"{riepilogo['acquisiti']}/{riepilogo['totali']}")
    st.progress(riepilogo["percentuale"] / 100)
    st.caption(f"{riepilogo['percentuale']:.0f}% completato")

    st.divider()

    pagina = st.radio(
        "Navigazione",
        ["📋 Piano di studi", "📊 Riepilogo", "🔮 Simulatore", "📈 Grafici", "⚙️ Impostazioni"],
        label_visibility="collapsed",
    )


# ═══════════════════════════════════════════════════════════════
#  PIANO DI STUDI
# ═══════════════════════════════════════════════════════════════

if pagina == "📋 Piano di studi":
    st.markdown("# 📋 Piano di studi")
    st.caption("Inserisci i voti degli esami sostenuti. Salvataggio automatico.")

    modificato = False

    for anno in [1, 2, 3]:
        st.markdown(f'<div class="anno-badge">Anno {anno}</div>', unsafe_allow_html=True)
        esami_anno = [e for e in st.session_state.piano if e["anno"] == anno]

        for esame in esami_anno:
            idx = st.session_state.piano.index(esame)

            with st.container():
                if esame["tipo"] == "idoneita":
                    cols = st.columns([4, 1, 1.5])
                    with cols[0]:
                        st.markdown(f"**{esame['nome']}**  \n`{esame['cfu']} CFU · Idoneità`")
                    with cols[2]:
                        sostenuto = st.checkbox(
                            "✓ Idoneo", value=esame["sostenuto"], key=f"idoneo_{idx}",
                        )
                        if sostenuto != esame["sostenuto"]:
                            st.session_state.piano[idx]["sostenuto"] = sostenuto
                            st.session_state.piano[idx]["voto"] = "idoneo" if sostenuto else None
                            modificato = True

                elif esame["tipo"] == "voto":
                    cols = st.columns([4, 1, 1, 0.5])
                    with cols[0]:
                        voto_display = ""
                        if esame["sostenuto"] and isinstance(esame["voto"], (int, float)):
                            lode_str = "L" if esame.get("lode") else ""
                            voto_display = f" → **{esame['voto']}{lode_str}**"
                        st.markdown(f"**{esame['nome']}**  \n`{esame['cfu']} CFU`{voto_display}")

                    with cols[1]:
                        sostenuto = st.checkbox(
                            "Sostenuto", value=esame["sostenuto"], key=f"sost_{idx}",
                        )

                    if sostenuto:
                        with cols[2]:
                            voto = st.number_input(
                                "Voto", min_value=18, max_value=30,
                                value=esame["voto"] if isinstance(esame["voto"], int) else 24,
                                key=f"voto_{idx}", label_visibility="collapsed",
                            )
                        with cols[3]:
                            lode = st.checkbox("L", value=esame.get("lode", False), key=f"lode_{idx}")

                        if (sostenuto != esame["sostenuto"] or
                            voto != esame.get("voto") or
                            lode != esame.get("lode")):
                            st.session_state.piano[idx]["sostenuto"] = True
                            st.session_state.piano[idx]["voto"] = voto
                            st.session_state.piano[idx]["lode"] = lode if voto == 30 else False
                            modificato = True
                    else:
                        if esame["sostenuto"]:
                            st.session_state.piano[idx]["sostenuto"] = False
                            st.session_state.piano[idx]["voto"] = None
                            st.session_state.piano[idx]["lode"] = False
                            modificato = True

    # Esami a scelta
    esami_opzionali = [e for e in st.session_state.piano if "scelta" in e["nome"].lower()]
    if esami_opzionali:
        st.markdown('<div class="anno-badge">Esami a scelta</div>', unsafe_allow_html=True)
        st.caption("Rinomina gli esami quando sai cosa sceglierai.")

        for esame in esami_opzionali:
            idx = st.session_state.piano.index(esame)
            cols = st.columns([3, 1, 1, 1, 0.5])

            with cols[0]:
                nuovo_nome = st.text_input(
                    "Nome", value=esame["nome"],
                    key=f"nome_opz_{idx}", label_visibility="collapsed",
                )
                if nuovo_nome != esame["nome"]:
                    st.session_state.piano[idx]["nome"] = nuovo_nome
                    modificato = True

            with cols[1]:
                st.caption(f"{esame['cfu']} CFU")

            with cols[2]:
                sostenuto = st.checkbox("Sostenuto", value=esame["sostenuto"], key=f"sost_opz_{idx}")

            if sostenuto:
                with cols[3]:
                    voto = st.number_input(
                        "Voto", min_value=18, max_value=30,
                        value=esame["voto"] if isinstance(esame["voto"], int) else 24,
                        key=f"voto_opz_{idx}", label_visibility="collapsed",
                    )
                with cols[4]:
                    lode = st.checkbox("L", value=esame.get("lode", False), key=f"lode_opz_{idx}")

                if (sostenuto != esame["sostenuto"] or voto != esame.get("voto") or lode != esame.get("lode")):
                    st.session_state.piano[idx]["sostenuto"] = True
                    st.session_state.piano[idx]["voto"] = voto
                    st.session_state.piano[idx]["lode"] = lode if voto == 30 else False
                    modificato = True
            else:
                if esame["sostenuto"]:
                    st.session_state.piano[idx]["sostenuto"] = False
                    st.session_state.piano[idx]["voto"] = None
                    st.session_state.piano[idx]["lode"] = False
                    modificato = True

    if modificato:
        salva_dati(st.session_state.piano)
        st.toast("Salvato!", icon="✅")


# ═══════════════════════════════════════════════════════════════
#  RIEPILOGO
# ═══════════════════════════════════════════════════════════════

elif pagina == "📊 Riepilogo":
    st.markdown("# 📊 Riepilogo")

    piano = st.session_state.piano
    media = media_ponderata(piano)
    riepilogo = riepilogo_cfu(piano)
    lodi = conta_lodi(piano)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Media ponderata", f"{media:.2f}" if media > 0 else "—")
    with col2:
        st.metric("CFU acquisiti", f"{riepilogo['acquisiti']}/{riepilogo['totali']}")
    with col3:
        n_esami = len([e for e in piano if e["sostenuto"] and e["tipo"] == "voto"])
        st.metric("Esami sostenuti", str(n_esami))
    with col4:
        st.metric("Lodi", str(lodi))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Dettaglio CFU")
        st.write(f"Con voto: **{riepilogo['acquisiti_con_voto']}** · "
                 f"Idoneità: **{riepilogo['acquisiti_idoneita']}** · "
                 f"Rimanenti: **{riepilogo['rimanenti']}**")
        st.progress(riepilogo["percentuale"] / 100)

    with col2:
        if media > 0:
            st.markdown("### Stima voto di laurea")
            punti_tesi = st.slider("Punti tesi", 0, 7, 3, key="tesi_riepilogo")
            punti_bonus = st.slider("Bonus (lodi, tempistica)", 0, 4, 0, key="bonus_riepilogo")
            laurea = stima_voto_laurea(media, punti_tesi, punti_bonus)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Base", f"{laurea['base_110']}")
            with c2:
                st.metric("+ Tesi", f"{laurea['con_tesi']}")
            with c3:
                st.metric("+ Bonus", f"{laurea['con_bonus']}")
            st.info(laurea["nota"])

    st.divider()
    st.markdown("### Esami sostenuti")
    sostenuti = [e for e in piano if e["sostenuto"]]
    if sostenuti:
        for e in sorted(sostenuti, key=lambda x: (x["anno"], x["nome"])):
            if isinstance(e["voto"], (int, float)):
                lode_str = " L" if e.get("lode") else ""
                voto_str = f"{e['voto']}{lode_str}"
            else:
                voto_str = "Idoneo"
            st.write(f"{'🟢' if e['tipo'] == 'voto' else '🔵'} "
                     f"**{e['nome']}** · {e['cfu']} CFU → **{voto_str}**")
    else:
        st.caption("Nessun esame ancora sostenuto.")


# ═══════════════════════════════════════════════════════════════
#  SIMULATORE
# ═══════════════════════════════════════════════════════════════

elif pagina == "🔮 Simulatore":
    st.markdown("# 🔮 Simulatore")
    st.caption("Esplora scenari e calcola la media con voti ipotetici.")

    piano = st.session_state.piano
    media_attuale = media_ponderata(piano)
    pt = plotly_template()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Scenario libero", "Voto uniforme", "Confronto scenari", "Media target"
    ])

    with tab1:
        non_sostenuti = [e for e in piano if not e["sostenuto"] and e["tipo"] == "voto"]
        if not non_sostenuti:
            st.info("Tutti gli esami con voto sono già sostenuti.")
        else:
            esami_sel = st.multiselect(
                "Seleziona esami da simulare",
                [e["nome"] for e in non_sostenuti], key="sim_libero_esami",
            )
            modifiche = {}
            if esami_sel:
                cols = st.columns(min(len(esami_sel), 3))
                for i, nome in enumerate(esami_sel):
                    esame = next(e for e in non_sostenuti if e["nome"] == nome)
                    with cols[i % 3]:
                        voto = st.slider(
                            f"{nome} ({esame['cfu']} CFU)",
                            18, 30, 26, key=f"sim_{nome}",
                        )
                        modifiche[nome] = voto

            if modifiche and st.button("▶️  Simula scenario", key="btn_sim_libero"):
                risultato = simula_scenario(piano, modifiche)
                st.divider()
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Media attuale", f"{risultato['media_attuale']:.2f}")
                with c2:
                    st.metric("Media simulata", f"{risultato['media_simulata']:.2f}")
                with c3:
                    st.metric("Variazione", f"{risultato['delta']:+.3f}")
                laurea_sim = stima_voto_laurea(risultato["media_simulata"])
                st.write(f"Stima base laurea: **{laurea_sim['base_110']}/110**")

    with tab2:
        st.caption("Se prendo lo stesso voto in tutti gli esami rimanenti...")
        voto_uni = st.slider("Voto", 18, 30, 26, key="voto_uniforme")
        if st.button("▶️  Simula", key="btn_uniforme"):
            risultato = scenario_uniforme(piano, voto_uni)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Media attuale", f"{risultato['media_attuale']:.2f}")
            with c2:
                st.metric("Media finale", f"{risultato['media_simulata']:.2f}")
            with c3:
                st.metric("Variazione", f"{risultato['delta']:+.3f}")
            laurea_sim = stima_voto_laurea(risultato["media_simulata"])
            st.write(f"Stima base laurea: **{laurea_sim['base_110']}/110**")

    with tab3:
        st.caption("Confronto tra tre scenari tipo.")
        if st.button("▶️  Genera confronto", key="btn_preconf"):
            scenari = scenari_preconfigurati(piano)
            cols = st.columns(3)
            colors = ["#ef4444", "#f59e0b", "#22c55e"]
            icons = ["📉", "📊", "📈"]
            for i, (nome, risultato) in enumerate(scenari.items()):
                with cols[i]:
                    laurea = stima_voto_laurea(risultato["media_simulata"])
                    st.markdown(f"#### {icons[i]} {nome}")
                    st.metric("Media", f"{risultato['media_simulata']:.2f}")
                    st.metric("Δ", f"{risultato['delta']:+.3f}")
                    st.caption(f"Stima laurea: {laurea['base_110']}/110")

            nomi = list(scenari.keys())
            medie = [scenari[n]["media_simulata"] for n in nomi]
            fig = go.Figure(data=[
                go.Bar(x=nomi, y=medie, text=[f"{m:.2f}" for m in medie],
                       textposition="outside", marker_color=colors, marker_line_width=0)
            ])
            if media_attuale > 0:
                fig.add_hline(y=media_attuale, line_dash="dash", line_color="#6366f1",
                              annotation_text=f"Attuale: {media_attuale:.2f}",
                              annotation_font_color="#6366f1")
            fig.update_layout(yaxis_title="Media ponderata", yaxis_range=[20, 31],
                              margin=dict(t=30, b=30), height=400, **pt)
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.caption("Che voto medio serve nei rimanenti per raggiungere un obiettivo?")
        target = st.slider("Media obiettivo", 22.0, 30.0, 27.0, step=0.5, key="target_media")
        risultato = voto_minimo_per_target(piano, target)
        if risultato["voto_necessario"] is not None:
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Voto medio necessario", f"{risultato['voto_necessario']:.1f}")
                st.write(f"In **{risultato['esami_rimanenti']}** esami ({risultato['cfu_rimanenti']} CFU)")
            with c2:
                if risultato["raggiungibile"]:
                    st.success(risultato["nota"])
                elif risultato["voto_necessario"] < 18:
                    st.success(risultato["nota"])
                else:
                    st.error(risultato["nota"])
        else:
            st.info(risultato["nota"])


# ═══════════════════════════════════════════════════════════════
#  GRAFICI
# ═══════════════════════════════════════════════════════════════

elif pagina == "📈 Grafici":
    st.markdown("# 📈 Grafici")
    piano = st.session_state.piano
    pt = plotly_template()

    tab1, tab2, tab3 = st.tabs(["Andamento", "Impatto CFU", "Distribuzione"])

    with tab1:
        sostenuti = [e for e in piano if e["sostenuto"] and e["tipo"] == "voto" and isinstance(e["voto"], (int, float))]
        if len(sostenuti) < 2:
            st.info("Servono almeno 2 esami con voto per il grafico.")
        else:
            sostenuti_ord = sorted(sostenuti, key=lambda x: (x["anno"], x["nome"]))
            nomi, voti, medie_cum = [], [], []
            sp, sc = 0, 0
            for e in sostenuti_ord:
                nomi.append(e["nome"])
                voti.append(e["voto"])
                sp += e["voto"] * e["cfu"]
                sc += e["cfu"]
                medie_cum.append(sp / sc)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=nomi, y=voti, mode="markers+lines", name="Voto",
                marker=dict(size=10, color="#94a3b8"),
                line=dict(dash="dot", color="#94a3b8"),
            ))
            fig.add_trace(go.Scatter(
                x=nomi, y=medie_cum, mode="markers+lines", name="Media cumulativa",
                marker=dict(size=9, color="#6366f1"),
                line=dict(color="#6366f1", width=3),
                fill="tozeroy", fillcolor="rgba(99, 102, 241, 0.05)",
            ))
            fig.update_layout(
                yaxis_title="Voto", yaxis_range=[17, 31], xaxis_tickangle=-45,
                margin=dict(t=20, b=60), height=450,
                legend=dict(yanchor="bottom", y=1.02, xanchor="right", x=1, orientation="h"),
                **pt,
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        impatti = impatto_esami(piano)
        if not impatti:
            st.info("Nessun esame con voto nel piano.")
        else:
            colori = ["#6366f1" if e["sostenuto"] else "#334155" for e in impatti]
            fig = go.Figure(data=[
                go.Bar(
                    x=[e["nome"] for e in impatti],
                    y=[e["peso_percentuale"] for e in impatti],
                    text=[f"{e['peso_percentuale']}%" for e in impatti],
                    textposition="outside", marker_color=colori, marker_line_width=0,
                )
            ])
            fig.update_layout(
                yaxis_title="Peso %", xaxis_tickangle=-45,
                margin=dict(t=20, b=60), height=450, **pt,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🟣 Sostenuto · ⚫ Non sostenuto")

    with tab3:
        sostenuti = [e for e in piano if e["sostenuto"] and e["tipo"] == "voto" and isinstance(e["voto"], (int, float))]
        if not sostenuti:
            st.info("Nessun esame sostenuto.")
        else:
            voti = [e["voto"] for e in sostenuti]
            fig = go.Figure(data=[
                go.Histogram(x=voti, nbinsx=13, marker_color="#6366f1", marker_line_width=0)
            ])
            fig.update_layout(
                xaxis_title="Voto", yaxis_title="Frequenza",
                xaxis=dict(dtick=1, range=[17.5, 30.5]),
                margin=dict(t=20, b=30), height=400, **pt,
            )
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  IMPOSTAZIONI
# ═══════════════════════════════════════════════════════════════

elif pagina == "⚙️ Impostazioni":
    st.markdown("# ⚙️ Impostazioni")

    st.markdown("### Esami a scelta libera")
    st.caption(f"Configura i {CFU_OPZIONALI_TOTALI} CFU di esami a scelta.")

    config = st.selectbox("Configurazione", list(CONFIGURAZIONI_OPZIONALI.keys()))

    if config == "Personalizzata":
        st.caption("Definisci esami personalizzati (totale = 18 CFU).")
        num_esami = st.number_input("Numero esami", 1, 6, 3)
        esami_custom = []
        for i in range(num_esami):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input(f"Nome {i+1}", f"Esame a scelta {i+1}", key=f"custom_nome_{i}")
            with c2:
                cfu = st.number_input(f"CFU {i+1}", 3, 12, 6, key=f"custom_cfu_{i}")
            esami_custom.append({"nome": nome, "cfu": cfu})
        totale = sum(e["cfu"] for e in esami_custom)
        if totale != CFU_OPZIONALI_TOTALI:
            st.warning(f"Totale: {totale} CFU (devono essere {CFU_OPZIONALI_TOTALI})")
    else:
        esami_custom = None

    if st.button("🔄  Rigenera piano", type="primary"):
        voti_salvati = {
            e["nome"]: {"voto": e["voto"], "lode": e.get("lode", False), "sostenuto": True}
            for e in st.session_state.piano if e["sostenuto"]
        }
        nuovo_piano = genera_piano_completo(config, esami_custom)
        for esame in nuovo_piano:
            if esame["nome"] in voti_salvati:
                d = voti_salvati[esame["nome"]]
                esame["voto"] = d["voto"]
                esame["lode"] = d["lode"]
                esame["sostenuto"] = d["sostenuto"]
        st.session_state.piano = nuovo_piano
        salva_dati(nuovo_piano)
        st.success("Piano rigenerato! Voti preservati.")
        st.rerun()

    st.divider()

    st.markdown("### Tema")
    tema_corrente = "Scuro 🌙" if st.session_state.tema == "scuro" else "Chiaro ☀️"
    st.write(f"Tema attuale: **{tema_corrente}**")
    st.caption("Usa il pulsante ☀️/🌙 nella sidebar per cambiare.")

    st.divider()

    st.markdown("### Dati")
    c1, c2 = st.columns(2)
    with c1:
        dati_json = json.dumps(st.session_state.piano, ensure_ascii=False, indent=2)
        st.download_button(
            "📥 Esporta JSON", data=dati_json,
            file_name="dati_esami.json", mime="application/json",
        )
    with c2:
        if st.button("🗑️ Reset completo"):
            st.session_state.piano = genera_piano_completo("3 esami da 6 CFU")
            salva_dati(st.session_state.piano)
            st.session_state.scenari_salvati = {}
            st.warning("Dati resettati.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════

st.markdown('<div class="footer">Media Ingegneria Civile · Unimore · Python + Streamlit</div>',
            unsafe_allow_html=True)
