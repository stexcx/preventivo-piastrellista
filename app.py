import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- 1. CONFIGURAZIONE "APP MOBILE" ---
icona_app = "logo.png" if os.path.exists("logo.png") else "logo.jpg"
if not os.path.exists(icona_app): icona_app = None 

# USARE "CENTERED" è il segreto per farla sembrare un'app sul telefono
st.set_page_config(page_title="App Piastrellista", page_icon=icona_app, layout="centered", initial_sidebar_state="collapsed")

# Memoria dell'App
if 'pagina' not in st.session_state: st.session_state['pagina'] = "home"
if 'archivio' not in st.session_state: st.session_state['archivio'] = []
if 'ditta' not in st.session_state:
    st.session_state['ditta'] = { "nome": "La Tua Ditta", "indirizzo": "", "citta": "", "piva": "", "tel": "", "email": "", "iban": "", "logo": None }

# --- 2. GRAFICA "TOTAL BLACK & WHITE BORDER" (Come la tua foto) ---
st.markdown("""
<style>
    /* SFONDO NERO TOTALE */
    .stApp { background-color: #000000 !important; }
    
    /* NASCONDI SIDEBAR E MENU IN ALTO */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    #MainMenu { display: none; }
    footer { display: none; }

    /* TESTI BIANCHI */
    h1, h2, h3, p, div, label, span { 
        color: #ffffff !important; 
        font-family: sans-serif;
    }

    /* PULSANTI MENU PRINCIPALE (Stile della tua foto) */
    .stButton > button {
        width: 100% !important;
        height: 70px !important;
        background-color: #000000 !important; /* Sfondo Nero */
        color: #ffffff !important; /* Scritta Bianca */
        border: 2px solid #ffffff !important; /* BORDO BIANCO */
        border-radius: 15px !important; /* Angoli arrotondati */
        font-size: 22px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .stButton > button:active { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
    }

    /* CASELLE DI TESTO (Input) */
    input[type="text"], input[type="number"] {
        font-size: 20px !important;
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* ETICHETTE SOPRA LE CASELLE */
    label p { font-size: 18px !important; font-weight: normal; margin-bottom: 2px; }

    /* RISULTATI (Metriche) */
    div[data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #ffffff !important;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 30px !important; color: white !important; }

    /* LOGO NON TAGLIATO */
    img { max-width: 100%; object-fit: contain; }

</style>
""", unsafe_allow_html=True)

# --- FUNZIONI ---
def vai(dove):
    st.session_state['pagina'] = dove
    st.rerun()

def pulisci(val): return 0.0 if val is None else val

def stima_colla(a, b):
    mq = (pulisci(a) * pulisci(b)) / 10000
    if mq <= 0: return 0
    elif mq <= 0.12: return 4.5
    elif mq <= 0.36: return 5.5
    else: return 7.0

class PDF(FPDF):
    def header(self): pass

def crea_pdf(preventivo, cliente, totale):
    pdf = PDF()
    pdf.add_page()
    ditta = st.session_state['ditta']
    
    if ditta['logo'] and os.path.exists(ditta['logo']):
        try: pdf.image(ditta['logo'], 10, 8, 30)
        except: pass
    
    pdf.set_xy(45, 10)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, ditta['nome'], ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_x(45)
    pdf.cell(0, 5, f"{ditta['indirizzo']} {ditta['citta']}", ln=True)
    pdf.set_x(45)
    pdf.cell(0, 5, f"P.IVA: {ditta['piva']} | Tel: {ditta['tel']}", ln=True)
    
    pdf.ln(15); pdf.line(10, 35, 200, 35)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Cliente: {cliente['nome']}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"Cantiere: {cliente['cantiere']}", ln=True)
    pdf.cell(0, 5, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True)
    
    pdf.ln(5)
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
    pdf.cell(40, 10, f"E {totali:.2f}", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# =======================================================
# PAGINA 1: HOME (MENU PRINCIPALE)
# =======================================================
if st.session_state['pagina'] == "home":
    
    # LOGO (Se caricato in Dati Ditta, usa quello, altrimenti default)
    if st.session_state['ditta']['logo']:
        st.image(st.session_state['ditta']['logo'], use_column_width=True)
    elif os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_column_width=True)
    
    st.write("") # Spazio vuoto
    st.markdown("<h3 style='text-align: center;'>MENU PRINCIPALE</h3>", unsafe_allow_html=True)
    st.write("") # Spazio vuoto

    # I 3 PULSANTONI
    if st.button("📝 NUOVO PREVENTIVO"): vai("calcola")
    if st.button("📂 ARCHIVIO LAVORI"): vai("archivio")
    if st.button("⚙️ DATI DITTA & LOGO"): vai("settings") 

# =======================================================
# PAGINA 2: IMPOSTAZIONI (Dati Ditta)
# =======================================================
elif st.session_state['pagina'] == "settings":
    if st.button("⬅ TORNA AL MENU"): vai("home")
    
    st.title("DATI DELLA TUA DITTA")
    st.info("Questi dati e il logo appariranno nell'intestazione del PDF.")
    
    d = st.session_state['ditta']
    
    # Caricamento Logo
    st.write("Carica il tuo logo:")
    uploaded_logo = st.file_uploader("Scegli immagine", label_visibility="collapsed")
    if uploaded_logo:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(uploaded_logo.getvalue())
            d['logo'] = tmp.name
            st.success("Logo caricato!")
    
    # Campi Dati
    d['nome'] = st.text_input("Nome Ditta", d['nome'])
    d['indirizzo'] = st.text_input("Indirizzo Sede", d['indirizzo'])
    d['citta'] = st.text_input("Città", d['citta'])
    d['piva'] = st.text_input("Partita IVA", d['piva'])
    d['tel'] = st.text_input("Telefono", d['tel'])
    d['email'] = st.text_input("Email", d['email'])
    
    if st.button("💾 SALVA DATI"):
        st.session_state['ditta'] = d
        st.success("Dati salvati!")
        vai("home")

# =======================================================
# PAGINA 3: CALCOLA PREVENTIVO
# =======================================================
elif st.session_state['pagina'] == "calcola":
    if st.button("⬅ TORNA AL MENU"): vai("home")
    
    st.title("CALCOLA & POSA")
    
    # Sezione Cliente
    st.subheader("1. CLIENTE")
    c_nome = st.text_input("Nome Cliente")
    c_cantiere = st.text_input("Indirizzo Cantiere")
    
    st.markdown("---")
    
    # Sezione Misure (UNA SOTTO L'ALTRA per evitare zoom)
    st.subheader("2. MISURE")
    l = st.number_input("Lunghezza (metri)", step=0.1)
    w = st.number_input("Larghezza (metri)", step=0.1)
    mq = l * w
    
    if mq > 0:
        st.metric("SUPERFICIE", f"{mq:.2f} mq")
        
        st.markdown("---")
        st.subheader("3. MATERIALI")
        
        st.write("Formato Piastrella:")
        fmt = st.selectbox("Seleziona", ["60x60", "30x30", "20x120", "80x80", "Altro"], label_visibility="collapsed")
        
        if fmt == "Altro":
            la = st.number_input("Lato A (cm)")
            lb = st.number_input("Lato B (cm)")
        else:
            p = fmt.split(" ")[0].split("x")
            la, lb = float(p[0]), float(p[1])
            
        st.write("Tipo di Posa:")
        tipo_posa = st.radio("Scegli", ["Dritta (10% Sfrido)", "Diagonale (15% Sfrido)"], label_visibility="collapsed")
        sfrido = 10 if "Dritta" in tipo_posa else 15
        mq_tot = mq * (1 + sfrido/100)
        
        st.write("Mq in una scatola (vedi pacco):")
        mq_box = st.number_input("Mq Pacco", value=1.44)
        box = math.ceil(mq_tot / mq_box) if mq_box > 0 else 0
        
        st.metric("SCATOLE DA ORDINARE", f"{box}", delta=f"Totale: {mq_tot:.2f} mq")
        
        st.write("---")
        st.subheader("COLLA")
        cons = stima_colla(la, lb)
        sacchi = math.ceil((mq * cons) / 25)
        st.metric("SACCHI (25kg)", f"{sacchi}")
        
        st.markdown("---")
        st.subheader("4. PREZZI (€)")
        
        pr_mat = st.number_input("Prezzo Piastrella (al mq)")
        pr_posa = st.number_input("Prezzo Posa (al mq)")
        pr_colla = st.number_input("Prezzo Colla (al sacco)", value=25.0)
        
        st.write("---")
        
        if st.button("💾 CALCOLA E SALVA"):
            if not c_nome:
                st.error("Inserisci il nome del cliente!")
            else:
                tot_mat = (box * mq_box) * pr_mat
                tot_posa = mq * pr_posa
                tot_colla = sacchi * pr_colla
                totale = tot_mat + tot_posa + tot_colla
                
                voci = [
                    {"desc": f"Piastrelle ({box} sc.)", "qta": str(box), "prezzo": pr_mat, "totale": tot_mat},
                    {"desc": f"Posa ({mq:.2f} mq)", "qta": f"{mq:.1f}", "prezzo": pr_posa, "totale": tot_posa},
                    {"desc": f"Colla ({sacchi} sc.)", "qta": str(sacchi), "prezzo": pr_colla, "totale": tot_colla}
                ]
                
                pdf_data = crea_pdf(voci, st.session_state['ditta'], {"nome":c_nome, "cantiere":c_cantiere}, totale)
                
                st.session_state['archivio'].append({"cli": c_nome, "tot": totale, "pdf": pdf_data})
                
                st.success(f"TOTALE: € {totale:.2f}")
                st.download_button("📥 SCARICA PDF", pdf_data, f"{c_nome}.pdf", "application/pdf")

# =======================================================
# PAGINA 4: ARCHIVIO
# =======================================================
elif st.session_state['pagina'] == "archivio":
    if st.button("⬅ TORNA AL MENU"): vai("home")
    
    st.title("ARCHIVIO LAVORI")
    
    if not st.session_state['archivio']:
        st.write("Nessun preventivo salvato.")
    
    for item in reversed(st.session_state['archivio']):
        st.write("---")
        st.subheader(item['cli'])
        st.write(f"Totale: € {item['tot']:.2f}")
        st.download_button("SCARICA PDF", item['pdf'], key=str(item))
