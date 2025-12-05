import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- CONFIGURAZIONE ---
icona_app = "logo.png" if os.path.exists("logo.png") else "logo.jpg"
if not os.path.exists(icona_app): icona_app = None 

# Layout "centered" per simulare app mobile
st.set_page_config(page_title="Calcola & Posa", page_icon=icona_app, layout="centered", initial_sidebar_state="collapsed")

if 'pagina' not in st.session_state: st.session_state['pagina'] = "home"
if 'archivio_preventivi' not in st.session_state: st.session_state['archivio_preventivi'] = []

# --- CSS "CANTIERE UI" (OTTIMIZZATO PER ESTERNO) ---
st.markdown("""
<style>
    /* 1. SFONDO GRIGIO CHIARO (Anti-riverbero) */
    .stApp {
        background-color: #F2F2F2 !important;
    }
    
    /* 2. TESTI GENERALI (Quasi Neri e SPESSI) */
    html, body, p, div, span {
        color: #111111 !important;
        font-family: sans-serif;
        font-size: 18px !important; /* Minimo richiesto */
        font-weight: 600 !important; /* Grassetto per leggibilità al sole */
    }

    /* 3. TITOLI (Arancione Cantiere o Nero) */
    h1 { 
        color: #E65C00 !important; /* Arancione Cantiere */
        text-align: center; 
        font-size: 28px !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    h2, h3 { 
        color: #111111 !important; 
        font-weight: 700 !important;
        border-bottom: 2px solid #FFD500; /* Riga Gialla */
        padding-bottom: 5px;
        margin-top: 25px;
    }

    /* 4. CASELLE DI INPUT (Grandi e Leggibili) */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important; /* Bianco interno per contrasto */
        border: 2px solid #999999 !important; 
        border-radius: 8px !important;
        padding: 5px !important;
    }
    input[type="text"], input[type="number"] {
        font-size: 20px !important; 
        font-weight: bold !important;
        color: #000000 !important;
        height: 50px !important; /* Area tocco grande */
    }
    /* Etichette sopra le caselle */
    label p {
        font-size: 18px !important;
        color: #333333 !important;
    }

    /* 5. MENU A TENDINA E RADIO */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #999999 !important;
        font-size: 18px !important;
        color: #000000 !important;
        height: 50px !important;
    }
    div[role="radiogroup"] label {
        background-color: #E0E0E0 !important; /* Grigio un po' più scuro */
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #CCCCCC;
    }

    /* 6. PULSANTI (Giallo Sicurezza - ENORMI) */
    .stButton > button {
        width: 100%;
        height: 65px !important; /* Altezza massiccia */
        background-color: #FFD500 !important; /* GIALLO SICUREZZA */
        color: #000000 !important; /* Testo Nero su Giallo */
        border: 2px solid #E6BE00 !important;
        border-radius: 10px;
        font-size: 22px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 0 #CUA000; /* Effetto 3D leggero */
        margin-top: 15px;
    }
    .stButton > button:active {
        box-shadow: none;
        transform: translateY(4px);
    }
    
    /* Pulsante speciale per CALCOLA (Arancione Cantiere) */
    /* Non possiamo targettizzarlo singolarmente facile in CSS puro su Streamlit, 
       quindi usiamo lo stile generale Giallo, ma i box risultati li facciamo Arancioni */

    /* 7. RISULTATI (Metriche) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border-left: 10px solid #E65C00 !important; /* Banda Arancione Cantiere */
        border-radius: 5px;
        padding: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    div[data-testid="stMetricValue"] { 
        font-size: 40px !important; 
        font-weight: 900 !important;
        color: #111111 !important; 
    }
    div[data-testid="stMetricLabel"] { 
        font-size: 18px !important; 
        color: #555555 !important; 
        font-weight: bold !important;
    }

    /* Nascondi elementi inutili */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI CALCOLO E PDF ---
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
    
    # Intestazione Standard (Bianco e Nero per stampa)
    if dati_azienda['logo_path'] and os.path.exists(dati_azienda['logo_path']):
        try: pdf.image(dati_azienda['logo_path'], 10, 8, 30) 
        except: pass
    elif os.path.exists("logo.png"): 
        try: pdf.image("logo.png", 10, 8, 30)
        except: pass

    pdf.set_xy(45, 10)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, dati_azienda['nome_azienda'], ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_x(45)
    pdf.cell(0, 5, f"{dati_azienda['indirizzo']} - {dati_azienda['citta']}", ln=True)
    pdf.set_x(45)
    pdf.cell(0, 5, f"P.IVA: {dati_azienda['piva']} | Tel: {dati_azienda['telefono']}", ln=True)
    
    pdf.ln(10)
    pdf.line(10, 35, 200, 35)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Cliente: {dati_cliente['nome']}", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 6, f"Cantiere: {dati_cliente['cantiere']}", ln=True)
    pdf.cell(0, 6, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # Tabella
    pdf.set_fill_color(240, 240, 240); 
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Descrizione", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Qta", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Unit.", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Totale", 1, 1, 'C', 1)

    pdf.set_font("Arial", size=10)
    for voce in dati_preventivo:
        pdf.cell(90, 10, voce['desc'], 1)
        pdf.cell(30, 10, str(voce['qta']), 1, 0, 'C')
        pdf.cell(30, 10, f"E {voce['prezzo']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"E {voce['totale']:.2f}", 1, 1, 'R')

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(150, 10, "TOTALE:", 0, 0, 'R')
    pdf.cell(40, 10, f"E {totali:.2f}", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- NAVIGAZIONE ---
def vai_a(nome_pagina):
    st.session_state['pagina'] = nome_pagina
    st.rerun()

# DATI AZIENDA (Modifica qui i tuoi dati fissi)
dati_azienda = {
    "nome_azienda": "Edil Rossi", 
    "indirizzo": "Via Roma 1", "citta": "Genova",
    "piva": "IT00000000000", "telefono": "333 1234567",
    "email": "info@edilrossi.it", "iban": "",
    "logo_path": "logo.png" if os.path.exists("logo.png") else "logo.jpg"
}

# =========================================================
#  PAGINA 1: HOME (MENU PRINCIPALE)
# =========================================================
if st.session_state['pagina'] == "home":
    
    # Logo
    if os.path.exists("logo.png"): st.image("logo.png", use_column_width=True)
    elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_column_width=True)
    
    st.title("MENU PRINCIPALE")
    st.write("") 

    if st.button("🧮 NUOVO PREVENTIVO"):
        vai_a("calcola")
        
    if st.button("📂 ARCHIVIO LAVORI"):
        vai_a("archivio")
        
    st.info("👆 Scegli un'opzione")


# =========================================================
#  PAGINA 2: CALCOLATRICE
# =========================================================
elif st.session_state['pagina'] == "calcola":
    
    if st.button("⬅ MENU"):
        vai_a("home")
    
    st.title("CALCOLA & POSA")

    # 1. CLIENTE
    st.header("1. CLIENTE")
    # Placeholder scuro per leggibilità
    c_nome = st.text_input("Nome Cliente", placeholder="Scrivi nome...")
    c_cantiere = st.text_input("Cantiere", placeholder="Indirizzo...")

    # 2. MISURE
    st.header("2. MISURE")
    lunghezza = st.number_input("Lunghezza (metri)", step=0.1, format="%.2f")
    larghezza = st.number_input("Larghezza (metri)", step=0.1, format="%.2f")
    
    mq_netti = lunghezza * larghezza
    
    if mq_netti > 0:
        st.metric("SUPERFICIE", f"{mq_netti:.2f} Mq")
        
        # 3. MATERIALI
        st.header("3. MATERIALI")
        formato = st.selectbox("Formato Piastrella", ["60x60", "30x30", "20x120", "80x80", "120x120", "Altro"])
        
        if formato == "Altro":
            lato_a = st.number_input("Lato A (cm)")
            lato_b = st.number_input("Lato B (cm)")
        else:
            p = formato.split(" ")[0].split("x")
            lato_a, lato_b = float(p[0]), float(p[1])

        tipo_posa = st.radio("Sfrido / Tagli", ["10% (Dritta)", "15% (Diagonale)"])
        sfrido = 10 if "10%" in tipo_posa else 15
        mq_nec = mq_netti + (mq_netti * sfrido / 100)
        
        st.info(f"Fabbisogno tot: {mq_nec:.2f} mq")
        
        mq_pacco = st.number_input("Mq in una scatola", value=1.44, step=0.01)
        if mq_pacco > 0:
            pacchi = math.ceil(mq_nec / mq_pacco)
            st.metric("SCATOLE DA ORDINARE", f"{pacchi}", f"Tot: {pacchi*mq_pacco:.2f} mq")
        else:
            pacchi = 0

        # COLLA
        st.subheader("COLLA")
        cons = stima_colla(lato_a, lato_b)
        kg_tot = mq_netti * cons
        sacchi = math.ceil(kg_tot / 25)
        st.metric("SACCHI (25kg)", f"{sacchi}")
        
        # 4. PREZZI
        st.header("4. PREZZI")
        
        prezzo_p = st.number_input("Prezzo Piastrella (€ al mq)", step=1.0)
        tot_p = (pacchi * mq_pacco) * prezzo_p
        
        prezzo_m = st.number_input("Prezzo Posa (€ al mq)", step=1.0)
        tot_m = mq_netti * prezzo_m
        
        prezzo_c = st.number_input("Prezzo Colla (€ al sacco)", value=25.0, step=0.5)
        tot_c = sacchi * prezzo_c

        st.write("---")
        # Pulsante CALCOLA speciale
        if st.button("💾 CALCOLA E SALVA"):
            if c_nome:
                tot_gen = tot_p + tot_m + tot_c
                voci = [
                    {"desc": f"Piastrelle ({pacchi} pacchi)", "qta": str(pacchi), "prezzo": prezzo_p, "totale": tot_p},
                    {"desc": f"Posa ({mq_netti:.2f} mq)", "qta": f"{mq_netti:.1f}", "prezzo": prezzo_m, "totale": tot_m},
                    {"desc": f"Colla ({sacchi} sacchi)", "qta": str(sacchi), "prezzo": prezzo_c, "totale": tot_c}
                ]
                
                pdf_bytes = crea_pdf(voci, dati_azienda, {"nome":c_nome, "cantiere":c_cantiere}, tot_gen)
                
                st.session_state['archivio_preventivi'].append({
                    "data": datetime.datetime.now().strftime("%d/%m"),
                    "cliente": c_nome,
                    "totale": tot_gen,
                    "pdf": pdf_bytes
                })
                
                st.success(f"SALVATO! TOTALE: € {tot_gen:.2f}")
                st.download_button("SCARICA PDF", pdf_bytes, f"{c_nome}.pdf", "application/pdf")
            else:
                st.error("Scrivi il nome del cliente!")

# =========================================================
#  PAGINA 3: ARCHIVIO
# =========================================================
elif st.session_state['pagina'] == "archivio":
    
    if st.button("⬅ MENU"):
        vai_a("home")
        
    st.title("ARCHIVIO LAVORI")
    
    if not st.session_state['archivio_preventivi']:
        st.write("Nessun lavoro salvato.")
    
    for doc in reversed(st.session_state['archivio_preventivi']):
        st.write("---")
        st.subheader(f"€ {doc['totale']:.2f}")
        st.write(f"📅 {doc['data']} | 👤 {doc['cliente']}")
        st.download_button("SCARICA PDF", doc['pdf'], key=f"d_{doc['cliente']}_{doc['totale']}")
