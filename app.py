import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- 1. CONFIGURAZIONE MOBILE-FRIENDLY ---
st.set_page_config(page_title="App Piastrellista", layout="centered", initial_sidebar_state="collapsed")

# Inizializza le variabili se non esistono
if 'pagina' not in st.session_state: st.session_state['pagina'] = "home"
if 'archivio' not in st.session_state: st.session_state['archivio'] = []
# Dati ditta di default (modificabili nell'app)
if 'ditta' not in st.session_state:
    st.session_state['ditta'] = {
        "nome": "La Tua Ditta", "indirizzo": "", "citta": "",
        "piva": "", "tel": "", "email": "", "iban": "", "logo": None
    }

# --- 2. CSS PER BLOCCARE LO ZOOM E CENTRARE ---
st.markdown("""
<style>
    /* SFONDO NERO TOTALE */
    .stApp { background-color: #000000; }
    
    /* TESTI BIANCHI */
    h1, h2, h3, p, div, label, span { color: #ffffff !important; font-family: sans-serif; }
    
    /* NASCONDI SIDEBAR (Non serve più) */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    
    /* CONTENITORE CENTRALE BLOCCATO (No scroll orizzontale) */
    .block-container {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    /* PULSANTI MENU (GIGANTI) */
    .stButton > button {
        width: 100%;
        height: 80px;
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 15px;
        font-size: 24px !important;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .stButton > button:active { background-color: #333 !important; }

    /* INPUT (CASELLE) - BIANCO SU NERO */
    input {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-size: 22px !important;
        border: 1px solid #ffffff !important;
    }
    
    /* RISULTATI (BOX) */
    div[data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 2px solid #ffffff !important;
        border-radius: 10px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 35px !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI UTILI ---
def vai(pagina):
    st.session_state['pagina'] = pagina
    st.rerun()

def pulisci(val): return 0.0 if val is None else val

def stima_colla(a, b):
    mq = (pulisci(a) * pulisci(b)) / 10000 # cm2 -> m2
    if mq <= 0: return 0
    elif mq <= 0.12: return 4.5 # Formati piccoli
    elif mq <= 0.36: return 5.5 # Medi
    else: return 7.0 # Grandi

class PDF(FPDF):
    def header(self): pass

def crea_pdf(preventivo, cliente, totale):
    pdf = PDF()
    pdf.add_page()
    ditta = st.session_state['ditta']
    
    # Logo
    if ditta['logo'] and os.path.exists(ditta['logo']):
        try: pdf.image(ditta['logo'], 10, 8, 30)
        except: pass
    
    # Intestazione
    pdf.set_xy(45, 10)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, ditta['nome'], ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_x(45)
    pdf.cell(0, 5, f"{ditta['indirizzo']} {ditta['citta']}", ln=True)
    pdf.set_x(45)
    pdf.cell(0, 5, f"P.IVA: {ditta['piva']} | Tel: {ditta['tel']}", ln=True)
    
    pdf.ln(15)
    pdf.line(10, 35, 200, 35)
    
    # Cliente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Cliente: {cliente['nome']}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"Cantiere: {cliente['cantiere']}", ln=True)
    pdf.cell(0, 5, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True)
    
    pdf.ln(5)
    
    # Tabella
    pdf.set_fill_color(0,0,0); pdf.set_text_color(255,255,255)
    pdf.cell(90, 10, "Descrizione", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Qta", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Prezzo", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Totale", 1, 1, 'C', 1)
    
    pdf.set_text_color(0,0,0)
    for riga in preventivo:
        pdf.cell(90, 10, riga['desc'], 1)
        pdf.cell(30, 10, riga['qta'], 1, 0, 'C')
        pdf.cell(30, 10, f"E {riga['prezzo']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"E {riga['totale']:.2f}", 1, 1, 'R')
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(150, 10, "TOTALE:", 0, 0, 'R')
    pdf.cell(40, 10, f"E {totale:.2f}", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# =======================================================
# PAGINA 1: HOME (MENU PRINCIPALE)
# =======================================================
if st.session_state['pagina'] == "home":
    # Mostra logo se c'è
    if st.session_state['ditta']['logo']:
        st.image(st.session_state['ditta']['logo'], use_column_width=True)
    
    st.title("APP PIASTRELLISTA")
    st.write("---")
    
    if st.button("📝 NUOVO PREVENTIVO"): vai("calcola")
    if st.button("📂 ARCHIVIO LAVORI"): vai("archivio")
    if st.button("⚙️ IMPOSTAZIONI DITTA"): vai("settings") # Qui inserisci i tuoi dati

# =======================================================
# PAGINA 2: IMPOSTAZIONI DITTA (Qui metti il tuo logo)
# =======================================================
elif st.session_state['pagina'] == "settings":
    if st.button("⬅ SALVA E TORNA ALLA HOME"): vai("home")
    
    st.title("DATI DELLA TUA DITTA")
    st.info("Compila qui i dati che appariranno sul PDF.")
    
    d = st.session_state['ditta']
    
    uploaded_logo = st.file_uploader("Carica Logo (PNG/JPG)")
    if uploaded_logo:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(uploaded_logo.getvalue())
            d['logo'] = tmp.name
            
    d['nome'] = st.text_input("Nome Ditta", d['nome'])
    d['indirizzo'] = st.text_input("Indirizzo", d['indirizzo'])
    d['citta'] = st.text_input("Città", d['citta'])
    d['piva'] = st.text_input("P.IVA", d['piva'])
    d['tel'] = st.text_input("Telefono", d['tel'])
    
    st.session_state['ditta'] = d

# =======================================================
# PAGINA 3: CALCOLA
# =======================================================
elif st.session_state['pagina'] == "calcola":
    if st.button("⬅ TORNA ALLA HOME"): vai("home")
    
    st.header("1. CLIENTE")
    c_nome = st.text_input("Nome Cliente")
    c_cantiere = st.text_input("Cantiere")
    
    st.header("2. MISURE")
    # Usa colonne per affiancare solo se c'è spazio, altrimenti impila
    l = st.number_input("Lunghezza (metri)", step=0.1)
    w = st.number_input("Larghezza (metri)", step=0.1)
    mq = l * w
    
    if mq > 0:
        st.metric("SUPERFICIE", f"{mq:.2f} mq")
        
        st.header("3. MATERIALI")
        fmt = st.selectbox("Formato", ["60x60", "30x30", "20x120", "80x80", "Altro"])
        
        if fmt == "Altro":
            la = st.number_input("Lato A (cm)")
            lb = st.number_input("Lato B (cm)")
        else:
            p = fmt.split(" ")[0].split("x")
            la, lb = float(p[0]), float(p[1])
            
        sfrido = 10 if st.radio("Posa", ["Dritta (10%)", "Diagonale (15%)"]) == "Dritta (10%)" else 15
        mq_tot = mq * (1 + sfrido/100)
        
        mq_box = st.number_input("Mq per scatola", value=1.44)
        box = math.ceil(mq_tot / mq_box) if mq_box > 0 else 0
        
        st.info(f"Serve materiale per {mq_tot:.2f} mq")
        st.metric("SCATOLE", f"{box}")
        
        # Colla
        cons = stima_colla(la, lb)
        sacchi = math.ceil((mq * cons) / 25)
        st.metric("SACCHI COLLA", f"{sacchi}")
        
        st.header("4. PREZZI")
        pr_mat = st.number_input("Prezzo Piastrella (€/mq)")
        pr_posa = st.number_input("Prezzo Posa (€/mq)")
        pr_colla = st.number_input("Prezzo Colla (€/sacco)", value=25.0)
        
        if st.button("💾 CREA PDF"):
            tot_mat = (box * mq_box) * pr_mat
            tot_posa = mq * pr_posa
            tot_colla = sacchi * pr_colla
            totale = tot_mat + tot_posa + tot_colla
            
            voci = [
                {"desc": f"Piastrelle ({box} scatole)", "qta": str(box), "prezzo": pr_mat, "totale": tot_mat},
                {"desc": f"Posa ({mq:.2f} mq)", "qta": f"{mq:.1f}", "prezzo": pr_posa, "totale": tot_posa},
                {"desc": f"Colla ({sacchi} sacchi)", "qta": str(sacchi), "prezzo": pr_colla, "totale": tot_colla}
            ]
            
            pdf_data = crea_pdf(voci, {"nome":c_nome, "cantiere":c_cantiere}, totale)
            
            st.session_state['archivio'].append({"cli": c_nome, "tot": totale, "pdf": pdf_data})
            st.success(f"TOTALE: € {totale:.2f}")
            st.download_button("SCARICA PDF", pdf_data, f"{c_nome}.pdf", "application/pdf")

# =======================================================
# PAGINA 4: ARCHIVIO
# =======================================================
elif st.session_state['pagina'] == "archivio":
    if st.button("⬅ TORNA ALLA HOME"): vai("home")
    st.title("ARCHIVIO")
    
    for item in reversed(st.session_state['archivio']):
        st.write("---")
        st.write(item['cli'])
        st.download_button(f"Scarica € {item['tot']:.2f}", item['pdf'], key=str(item))
