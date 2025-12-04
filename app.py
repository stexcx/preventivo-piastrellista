import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Preventivi Pro", page_icon="🛠️", layout="wide")

# --- CSS PER MIGLIORARE LA VISIBILITÀ DELLA SIDEBAR ---
# Questo codice colora la barra laterale per renderla ben visibile
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        border-right: 2px solid #d1d1d1;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONE LOGICA COLLA ---
def stima_colla(lato_a, lato_b):
    """
    Stima i kg/mq di colla in base alla dimensione della piastrella.
    Logica: Più grande è il formato, maggiore è il consumo (doppia spalmatura).
    """
    area_cmq = lato_a * lato_b
    if area_cmq <= 0:
        return 0
    elif area_cmq <= 1200: # Es. fino a 30x40 o 20x20
        return 4.5 # Consumo standard
    elif area_cmq <= 3600: # Es. fino a 60x60
        return 5.5 # Media spalmatura
    else: # Grandi formati (es. 80x80, 120x120, lastre)
        return 7.0 # Doppia spalmatura abbondante

# --- FUNZIONE PDF ---
def crea_pdf(dati_preventivo, dati_azienda, dati_cliente):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione
    pdf.set_font("Arial", 'B', 16)
    if dati_azienda['logo_path']:
        try:
            pdf.image(dati_azienda['logo_path'], 10, 8, 33)
            pdf.cell(40)
        except:
            pass
            
    pdf.cell(0, 10, f"Preventivo: {dati_azienda['nome_azienda']}", ln=True, align='R')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"P.IVA: {dati_azienda['piva']} | Tel: {dati_azienda['telefono']}", ln=True, align='R')
    pdf.line(10, 30, 200, 30)
    pdf.ln(20)

    # Dati Cliente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Dati Cliente:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Nome: {dati_cliente['nome']}", ln=True)
    pdf.cell(0, 8, f"Indirizzo: {dati_cliente['indirizzo']}", ln=True)
    pdf.cell(0, 8, f"Cantiere: {dati_cliente['cantiere']}", ln=True)
    pdf.ln(10)

    # Tabella
    pdf.set_fill_color(230, 240, 255) # Azzurrino chiaro
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Descrizione", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Quantità", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Prezzo Unit.", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Totale", 1, 1, 'C', 1)

    pdf.set_font("Arial", size=10)
    totale_generale = 0
    for voce in dati_preventivo:
        pdf.cell(90, 10, voce['desc'], 1)
        pdf.cell(30, 10, str(voce['qta']), 1, 0, 'C')
        pdf.cell(30, 10, f"E {voce['prezzo']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"E {voce['totale']:.2f}", 1, 1, 'R')
        totale_generale += voce['totale']

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, "TOTALE STIMATO:", 0, 0, 'R')
    pdf.cell(40, 10, f"E {totale_generale:.2f}", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA UTENTE ---

# SIDEBAR EVIDENZIATA
st.sidebar.header("🛠️ IMPOSTAZIONI AZIENDA")
st.sidebar.markdown("Compila qui i tuoi dati che appariranno nel PDF.")
logo_file = st.sidebar.file_uploader("Carica Logo", type=['png', 'jpg', 'jpeg'])
nome_azienda = st.sidebar.text_input("Nome Ditta", "Edil Piastrelle Rossi")
piva = st.sidebar.text_input("Partita IVA", "IT00000000000")
telefono = st.sidebar.text_input("Telefono", "333 1234567")

logo_path = None
if logo_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(logo_file.getvalue())
        logo_path = tmp_file.name
dati_azienda = {"nome_azienda": nome_azienda, "piva": piva, "telefono": telefono, "logo_path": logo_path}

# PAGINA PRINCIPALE
st.title("📑 Gestionale Preventivi 3.0")

# --- SEZIONE 1: CLIENTE ---
st.subheader("1. Dati Cliente")
col_c1, col_c2 = st.columns(2)
with col_c1:
    c_nome = st.text_input("Nome Cliente")
    c_indirizzo = st.text_input("Indirizzo Residenza")
with col_c2:
    c_cantiere = st.text_input("Indirizzo Cantiere")
    c_email = st.text_input("Email / Note")

st.markdown("---")

# --- SEZIONE 2: MISURE E TECNICA ---
st.subheader("2. Misure e Posa")
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    lunghezza = st.number_input("Lunghezza Stanza (m)", 0.0, step=0.1)
    larghezza = st.number_input("Larghezza Stanza (m)", 0.0, step=0.1)

with col_m2:
    tipo_posa = st.selectbox("Tipo di Posa", ["Dritta (Standard)", "Diagonale", "Spina di Pesce"])
    
    # Logica Sfrido Automatica
    if "Dritta" in tipo_posa:
        sfrido_suggerito = 10
    elif "Diagonale" in tipo_posa:
        sfrido_suggerito = 15
    else:
        sfrido_suggerito = 12 # Spina di pesce
        
    sfrido_perc = st.number_input("Sfrido (%)", value=sfrido_suggerito, step=1, help="Modificabile se necessario")

with col_m3:
    mq_netti = lunghezza * larghezza
    mq_calcolati = mq_netti + (mq_netti * sfrido_perc / 100)
    st.metric("Totale Mq (con sfrido)", f"{mq_calcolati:.2f} mq")

st.markdown("---")

# --- SEZIONE 3: MATERIALI (Nuova Logica Formati) ---
st.subheader("3. Scelta Piastrelle & Colla Auto")

col_f1, col_f2 = st.columns(2)

with col_f1:
    st.write("**Formato Piastrella**")
    # Menu a tendina preimpostato
    opzioni_formato = [
        "60x60 (Standard)", 
        "30x30 (Piccolo)", 
        "20x120 (Effetto Legno)", 
        "80x80 (Grande)", 
        "120x120 (Lastra)", 
        "Altro / Personalizzato"
    ]
    scelta_formato = st.selectbox("Seleziona Formato:", opzioni_formato)
    
    # Logica per estrarre le misure dalla scelta o farle inserire a mano
    if scelta_formato == "Altro / Personalizzato":
        p_lato_a = st.number_input("Lato A (cm)", value=60)
        p_lato_b = st.number_input("Lato B (cm)", value=60)
    else:
        # Prende i numeri dalla stringa (es "20x120" -> 20 e 120)
        parti = scelta_formato.split(" ")[0].split("x")
        p_lato_a = float(parti[0])
        p_lato_b = float(parti[1])
        st.info(f"Misure bloccate: {p_lato_a} x {p_lato_b} cm")

    # Calcolo pezzi
    if p_lato_a > 0 and p_lato_b > 0 and mq_calcolati > 0:
        area_piastrella_mq = (p_lato_a * p_lato_b) / 10000
        numero_piastrelle = mq_calcolati / area_piastrella_mq
        st.write(f"🧱 Pezzi stimati: **{int(numero_piastrelle) + 1}**")

with col_f2:
    st.write("**Stima Colla (Automatica)**")
    
    # Calcolo automatico consumo in base al formato
    consumo_stimato = stima_colla(p_lato_a, p_lato_b)
    
    kg_totali_colla = mq_netti * consumo_stimato
    sacchi_colla = (kg_totali_colla / 25)
    
    # Visualizzazione non modificabile (st.info o st.metric)
    st.info(f"Consumo stimato per questo formato: **{consumo_stimato} kg/mq**")
    st.metric("Sacchi Colla (25kg)", f"{int(sacchi_colla) + 1} pz", delta=f"Tot: {kg_totali_colla:.1f} kg")

st.markdown("---")

# --- SEZIONE 4: COSTI ---
st.subheader("4. Costi")
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    prezzo_mat = st.number_input("Costo Piastrella (€/mq)", 0.0, step=1.0)
with col_p2:
    prezzo_posa = st.number_input("Costo Manodopera (€/mq)", 0.0, step=1.0)
with col_p3:
    costo_colla_sacco = st.number_input("Costo Colla (€/sacco)", 25.0, step=1.0)

# --- CALCOLO FINALE ---
if st.button("CALCOLA E GENERA PDF 🚀"):
    if mq_netti > 0:
        tot_materiale = mq_calcolati * prezzo_mat
        tot_posa = mq_netti * prezzo_posa
        tot_colla = (int(sacchi_colla) + 1) * costo_colla_sacco
        
        voci = [
            {"desc": f"Piastrelle {scelta_formato} (Sfrido {sfrido_perc}%)", "qta": f"{mq_calcolati:.2f} mq", "prezzo": prezzo_mat, "totale": tot_materiale},
            {"desc": f"Posa in opera ({tipo_posa})", "qta": f"{mq_netti:.2f} mq", "prezzo": prezzo_posa, "totale": tot_posa},
            {"desc": f"Colla (Stima {consumo_stimato}kg/mq)", "qta": f"{int(sacchi_colla)+1} sacchi", "prezzo": costo_colla_sacco, "totale": tot_colla}
        ]
        
        totale_prev = tot_materiale + tot_posa + tot_colla
        st.success(f"Totale Preventivo: € {totale_prev:.2f}")
        
        pdf_bytes = crea_pdf(voci, dati_azienda, {"nome": c_nome, "indirizzo": c_indirizzo, "cantiere": c_cantiere})
        st.download_button("📥 SCARICA PDF UFFICIALE", pdf_bytes, f"Preventivo_{c_nome}.pdf", "application/pdf")
    else:
        st.error("Mancano le misure della stanza!")
