import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- CONFIGURAZIONE ---
icona_app = "logo.png" if os.path.exists("logo.png") else "logo.jpg"
if not os.path.exists(icona_app): icona_app = None 

st.set_page_config(page_title="Calcola & Posa", page_icon=icona_app, layout="centered")

if 'archivio_preventivi' not in st.session_state:
    st.session_state['archivio_preventivi'] = []

# --- CSS ALTO CONTRASTO (FIX DEFINITIVO VISIBILITÀ) ---
st.markdown("""
<style>
    /* 1. FORZARE SFONDO BIANCO SU TUTTA L'APP (ignora tema scuro telefono) */
    .stApp {
        background-color: #ffffff !important;
    }

    /* 2. BARRA LATERALE (SIDEBAR) - NERO TOTAL */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important; /* Tutto bianco nella sidebar */
    }

    /* 3. CASELLE DI INPUT (Dove scrivi) - FIX VISIBILITÀ */
    /* Lo sfondo della casella deve essere BIANCO */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important; /* Bordo Nero */
        border-radius: 8px !important;
    }
    
    /* Il testo che scrivi deve essere NERO */
    input[type="text"], input[type="number"] {
        color: #000000 !important;
        caret-color: #000000 !important; /* Cursore nero */
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
    /* Il testo fantasma (Placeholder) deve essere GRIGIO SCURO (leggibile) */
    ::placeholder {
        color: #555555 !important;
        opacity: 1 !important;
        font-weight: normal !important;
    }
    
    /* Le ETICHETTE sopra le caselle (es. "Lunghezza stanza") */
    label, .stInput > label {
        color: #000000 !important; /* Nere */
        font-size: 22px !important; /* Grandi */
        font-weight: 900 !important; /* Molto Grassetto */
        margin-bottom: 5px !important;
    }

    /* 4. MENU A TENDINA (Selectbox) */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
        font-size: 20px !important;
    }

    /* 5. TITOLI */
    h1, h2, h3 { 
        color: #000000 !important; 
        font-weight: 900 !important;
    }
    
    /* 6. RISULTATI E METRICHE */
    div[data-testid="stMetric"] {
        background-color: #f0f0f0 !important; /* Grigio chiarissimo */
        border: 4px solid #000000 !important;
        color: #000000 !important;
        border-radius: 15px;
        padding: 10px;
    }
    div[data-testid="stMetricValue"] { color: #000000 !important; font-size: 36px !important; }
    div[data-testid="stMetricLabel"] { color: #000000 !important; font-weight: bold; }

    /* 7. BOTTONI */
    div.stButton > button { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        border: 3px solid #000000; 
        font-size: 24px !important;
        padding: 15px;
        border-radius: 12px;
    }
    
    /* Nascondi footer */
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI ---
def pulisci_num(valore): return 0.0 if valore is None else valore

def stima_colla(lato_a, lato_b):
    lato_a, lato_b = pulisci_num(lato_a), pulisci_num(lato_b)
    area_cmq = lato_a * lato_b
    if area_cmq <= 0: return 0
    elif area_cmq <= 1200: return 4.5
    elif area_cmq <= 3600: return 5.5
    else: return 7.0

class PDF(FPDF):
    def header(self): pass

def crea_pdf(dati_preventivo, dati_azienda, dati_cliente, totali):
    pdf = PDF()
    pdf.add_page()
    
    # LOGO
    logo_da_stampare = None
    if dati_azienda['logo_path'] and os.path.exists(dati_azienda['logo_path']):
        logo_da_stampare = dati_azienda['logo_path']
    elif os.path.exists("logo.png"): logo_da_stampare = "logo.png"
    elif os.path.exists("logo.jpg"): logo_da_stampare = "logo.jpg"

    if logo_da_stampare:
        try: pdf.image(logo_da_stampare, 10, 8, 30) 
        except: pass

    # INTESTAZIONE
    start_x = 45 
    pdf.set_xy(start_x, 10)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, dati_azienda['nome_azienda'], ln=True)
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"{dati_azienda['indirizzo']} - {dati_azienda['citta']}", ln=True)
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"P.IVA: {dati_azienda['piva']} | Tel: {dati_azienda['telefono']}", ln=True)
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"Email: {dati_azienda['email']}", ln=True)
    
    pdf.ln(10)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(1)
    pdf.line(10, 45, 200, 45)

    # CLIENTE
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, f" Spett.le Cliente: {dati_cliente['nome']}", ln=True, fill=True)
    
    pdf.set_font("Arial", size=10)
    indirizzo_completo = f"{dati_cliente['indirizzo']} - {dati_cliente['cap']} {dati_cliente['citta']}"
    pdf.cell(0, 6, f"Indirizzo: {indirizzo_completo}", ln=True)
    pdf.cell(0, 6, f"C.F./P.IVA: {dati_cliente['cf']}", ln=True)
    if dati_cliente['telefono']:
        pdf.cell(0, 6, f"Recapito: {dati_cliente['telefono']}", ln=True)
    
    pdf.ln(3)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 6, f"Cantiere: {dati_cliente['cantiere']}", ln=True)
    pdf.cell(0, 6, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # TABELLA
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Descrizione", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Quantita'", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Prezzo Unit.", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Totale", 1, 1, 'C', 1)

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    
    for voce in dati_preventivo:
        pdf.cell(90, 10, voce['desc'], 1)
        pdf.cell(30, 10, str(voce['qta']), 1, 0, 'C')
        pdf.cell(30, 10, f"Euro {voce['prezzo']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"Euro {voce['totale']:.2f}", 1, 1, 'R')

    pdf.ln(5)
    
    # TOTALE
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(150, 10, "TOTALE STIMATO:", 0, 0, 'R')
    pdf.cell(40, 10, f"Euro {totali:.2f}", 1, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "I prezzi si intendono IVA esclusa.", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INTERFACCIA ---

st.sidebar.markdown("<p style='text-align:center;'>chiudi menu ➡</p>", unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_column_width=True)
elif os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_column_width=True)

st.sidebar.title("MENU")
menu = st.sidebar.radio("", ["🧮 Calcola", "📂 Archivio"])
st.sidebar.markdown("---")

st.sidebar.header("🛠️ Dati Azienda")
logo_in = st.sidebar.file_uploader("Carica Logo", type=['png','jpg'])
d_nome = st.sidebar.text_input("Nome Ditta", "Edil Rossi")
d_indirizzo = st.sidebar.text_input("Indirizzo", "Via Roma 1")
d_citta = st.sidebar.text_input("Città", "16100 Genova")
d_piva = st.sidebar.text_input("P.IVA", "IT00000000000")
d_tel = st.sidebar.text_input("Tel", "333 1234567")
d_email = st.sidebar.text_input("Email", "info@edilrossi.it")
d_iban = st.sidebar.text_input("IBAN", "")

logo_path = None
if logo_in:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(logo_in.getvalue())
        logo_path = tmp.name

dati_azienda = {
    "nome_azienda": d_nome, "indirizzo": d_indirizzo, "citta": d_citta,
    "piva": d_piva, "telefono": d_tel, "email": d_email, "iban": d_iban, "logo_path": logo_path
}

# === SEZIONE CALCOLA ===
if menu == "🧮 Calcola":
    st.title("Calcola & Posa")

    # DATI CLIENTE
    with st.expander("👤 DATI CLIENTE (Clicca per aprire)", expanded=True):
        st.write("Inserisci i dati qui sotto:")
        # Ho aggiunto placeholder specifici per aiutare la lettura
        c_nome = st.text_input("Nome Cliente / Ditta", placeholder="Es. Mario Rossi")
        c_cantiere = st.text_input("Cantiere / Luogo Lavoro", placeholder="Es. Via Garibaldi 3")
        
        st.write("---")
        st.write("Dati Fiscali (Facoltativi):")
        c_cf = st.text_input("Codice Fiscale / P.IVA", placeholder="CF o Partita IVA")
        c_tel = st.text_input("Telefono Cliente", placeholder="Numero di telefono")
        c_indirizzo = st.text_input("Indirizzo Residenza", placeholder="Indirizzo completo")
        col_cit, col_cap = st.columns(2)
        c_citta = col_cit.text_input("Città", placeholder="Città")
        c_cap = col_cap.text_input("CAP", placeholder="00000")

    st.markdown("---")

    # MISURE
    st.subheader("1. Misure")
    col_m1, col_m2 = st.columns(2)
    lunghezza = col_m1.number_input("Lunghezza (m)", value=None, step=0.1, placeholder="0.0")
    larghezza = col_m2.number_input("Larghezza (m)", value=None, step=0.1, placeholder="0.0")
    
    mq_netti = pulisci_num(lunghezza) * pulisci_num(larghezza)
    st.metric("SUPERFICIE TOTALE", f"{mq_netti:.2f} mq")
    
    st.markdown("---")

    # MATERIALI
    st.subheader("2. Materiali")
    
    if mq_netti > 0:
        st.write("🧱 **Piastrelle**")
        formato = st.selectbox("Formato Piastrella", ["60x60", "30x30", "20x120 (Legno)", "80x80", "120x120", "Altro"])
        
        if formato == "Altro":
            lato_a = st.number_input("Lato A (cm)", value=None, placeholder="0")
            lato_b = st.number_input("Lato B (cm)", value=None, placeholder="0")
        else:
            p = formato.split(" ")[0].split("x")
            lato_a, lato_b = float(p[0]), float(p[1])
        
        tipo_posa = st.radio("Tipo Posa", ["Dritta (10% Sfrido)", "Diagonale (15% Sfrido)"])
        sfrido = 10 if "Dritta" in tipo_posa else 15
        mq_nec = mq_netti + (mq_netti * sfrido / 100)
        
        mq_pacco = st.number_input("Mq in 1 Pacco", value=None, step=0.01, placeholder="Es. 1.44")
        mq_pacco_c = pulisci_num(mq_pacco)
        
        if mq_pacco_c > 0:
            pacchi = math.ceil(mq_nec / mq_pacco_c)
            mq_tot_acquisto = pacchi * mq_pacco_c
            st.info(f"Serve: {mq_nec:.2f} mq")
            st.metric("📦 PACCHI DA ORDINARE", f"{pacchi} pz", f"Totale: {mq_tot_acquisto:.2f} mq")
        else:
            pacchi, mq_tot_acquisto = 0, 0

        st.markdown("") 

        st.write("🧪 **Colla**")
        cons = stima_colla(lato_a, lato_b)
        kg_tot = mq_netti * cons
        sacchi = math.ceil(kg_tot / 25)
        st.metric("SACCHI COLLA (25kg)", f"{sacchi}", f"Totale: {sacchi*25} kg")

        st.markdown("---")

        # COSTI
        st.subheader("3. Costi")
        
        st.write("💰 **Piastrelle**")
        modo_p = st.radio("Prezzo a:", ["Mq", "Pacco"], horizontal=True)
        prezzo_p = st.number_input("Costo Piastrella (€)", value=None, step=1.0, placeholder="0")
        prezzo_p_c = pulisci_num(prezzo_p)
        if modo_p == "Mq":
            tot_p = mq_tot_acquisto * prezzo_p_c
            desc_p = f"Fornitura ({pacchi} pacchi da {mq_pacco_c}mq)"
        else:
            tot_p = pacchi * prezzo_p_c
            desc_p = f"Fornitura ({pacchi} pacchi)"
        
        st.write("🔨 **Manodopera**")
        prezzo_m = st.number_input("Costo Posa al Mq (€)", value=None, step=1.0, placeholder="0")
        prezzo_m_c = pulisci_num(prezzo_m)
        tot_m = mq_netti * prezzo_m_c
        
        st.write("🧪 **Colla**")
        modo_c = st.radio("Prezzo Colla a:", ["Sacco", "Mq"], horizontal=True)
        prezzo_c = st.number_input("Costo Colla (€)", value=None, step=0.5, placeholder="0")
        prezzo_c_c = pulisci_num(prezzo_c)
        if modo_c == "Sacco":
            tot_c = sacchi * prezzo_c_c
            desc_c = f"Colla ({sacchi} sacchi)"
        else:
            tot_c = mq_netti * prezzo_c_c
            desc_c = f"Materiale Consumo (Stima {mq_netti}mq)"

        # BOTTONE FINALE
        if st.button("CALCOLA PREVENTIVO 🚀"):
            if not c_nome:
                st.error("Inserisci almeno il nome del cliente!")
            else:
                tot_gen = tot_p + tot_m + tot_c
                voci = [
                    {"desc": desc_p, "qta": f"{mq_tot_acquisto:.2f} mq" if modo_p=="Mq" else f"{pacchi}", "prezzo": prezzo_p_c, "totale": tot_p},
                    {"desc": f"Posa in opera ({tipo_posa})", "qta": f"{mq_netti:.2f} mq", "prezzo": prezzo_m_c, "totale": tot_m},
                    {"desc": desc_c, "qta": f"{sacchi}" if modo_c=="Sacco" else "1", "prezzo": prezzo_c_c, "totale": tot_c}
                ]
                
                d_cli = {
                    "nome": c_nome, "cf": c_cf, 
                    "indirizzo": c_indirizzo, "citta": c_citta, "cap": c_cap,
                    "telefono": c_tel, "cantiere": c_cantiere
                }
                
                pdf_bytes = crea_pdf(voci, dati_azienda, d_cli, tot_gen)
                
                rec = {"data": datetime.datetime.now().strftime("%d/%m/%Y"), "cliente": c_nome, "totale": tot_gen, "pdf": pdf_bytes}
                st.session_state['archivio_preventivi'].append(rec)
                
                st.balloons()
                st.success(f"TOTALE: € {tot_gen:.2f}")
                st.download_button("📥 SCARICA PDF", pdf_bytes, f"Prev_{c_nome}.pdf", "application/pdf")
    else:
        st.info("Inserisci le misure sopra.")

elif menu == "📂 Archivio":
    st.title("📂 Archivio")
    if not st.session_state['archivio_preventivi']:
        st.write("Nessun preventivo.")
    else:
        for i, doc in enumerate(reversed(st.session_state['archivio_preventivi'])):
            with st.expander(f"{doc['cliente']} - € {doc['totale']:.2f} ({doc['data']})"):
                st.download_button("📥 Scarica", doc['pdf'], key=f"b_{i}")
