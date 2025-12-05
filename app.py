import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- 1. CONFIGURAZIONE ---
icona_app = "logo.png" if os.path.exists("logo.png") else "logo.jpg"
if not os.path.exists(icona_app): icona_app = None 

st.set_page_config(page_title="App Piastrellista", page_icon=icona_app, layout="wide", initial_sidebar_state="collapsed")

# Gestione Stato
if 'pagina' not in st.session_state: st.session_state['pagina'] = "home"
if 'archivio' not in st.session_state: st.session_state['archivio'] = []
if 'ditta' not in st.session_state:
    st.session_state['ditta'] = { "nome": "La Tua Ditta", "indirizzo": "", "citta": "", "piva": "", "tel": "", "email": "", "iban": "", "logo": None }

# --- 2. CARICAMENTO CSS ESTERNO (Nuova Funzione) ---
def carica_css(nome_file):
    with open(nome_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Se il file style.css esiste su GitHub/Server, caricalo
if os.path.exists("style.css"):
    carica_css("style.css")

# --- FUNZIONI ---
def vai(pagina):
    st.session_state['pagina'] = pagina
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
# PAGINA 1: HOME (MENU A CUBI)
# =======================================================
if st.session_state['pagina'] == "home":
    
    if st.session_state['ditta']['logo']:
        st.image(st.session_state['ditta']['logo'], use_column_width=True)
    elif os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    
    st.title("MENU PRINCIPALE")
    
    if st.button("📝 NUOVO PREVENTIVO"): vai("calcola")
    if st.button("📂 ARCHIVIO LAVORI"): vai("archivio")
    if st.button("⚙️ DATI DITTA"): vai("settings") 

# =======================================================
# PAGINA 2: CALCOLA (TUTTO VERTICALE)
# =======================================================
elif st.session_state['pagina'] == "calcola":
    if st.button("⬅ HOME"): vai("home")
    
    st.header("1. CLIENTE")
    c_nome = st.text_input("Nome Cliente")
    c_cantiere = st.text_input("Indirizzo Cantiere")
    
    st.header("2. MISURE STANZA")
    l = st.number_input("Lunghezza (metri)", step=0.1)
    w = st.number_input("Larghezza (metri)", step=0.1)
    
    mq = l * w
    if mq > 0:
        st.metric("SUPERFICIE", f"{mq:.2f} mq")
        
        st.header("3. MATERIALI")
        st.write("Formato Piastrella:")
        fmt = st.selectbox("Seleziona", ["60x60", "30x30", "20x120", "80x80", "Altro"], label_visibility="collapsed")
        
        if fmt == "Altro":
            la = st.number_input("Lato A (cm)")
            lb = st.number_input("Lato B (cm)")
        else:
            p = fmt.split(" ")[0].split("x")
            la, lb = float(p[0]), float(p[1])
            
        st.write("Sfrido / Posa:")
        tipo_posa = st.radio("Scegli:", ["Dritta (10%)", "Diagonale (15%)"], label_visibility="collapsed")
        sfrido = 10 if "Dritta" in tipo_posa else 15
        
        mq_tot = mq * (1 + sfrido/100)
        
        mq_box = st.number_input("Mq per scatola (vedi confezione)", value=1.44)
        box = math.ceil(mq_tot / mq_box) if mq_box > 0 else 0
        
        st.metric("SCATOLE DA ORDINARE", f"{box}", f"Totale: {mq_tot:.2f} mq")
        
        st.write("---")
        st.write("Colla:")
        cons = stima_colla(la, lb)
        sacchi = math.ceil((mq * cons) / 25)
        st.metric("SACCHI COLLA (25kg)", f"{sacchi}")
        
        st.header("4. PREZZI (€)")
        pr_mat = st.number_input("Prezzo Piastrella (al mq)")
        pr_posa = st.number_input("Prezzo Posa (al mq)")
        pr_colla = st.number_input("Prezzo Colla (al sacco)", value=25.0)
        
        st.write("---")
        if st.button("💾 CALCOLA E SALVA"):
            if not c_nome:
                st.error("Manca nome cliente!")
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
                
                pdf_data = crea_pdf(voci, {"nome":c_nome, "cantiere":c_cantiere}, totale)
                
                st.session_state['archivio'].append({"cli": c_nome, "tot": totale, "pdf": pdf_data})
                st.success(f"TOTALE: € {totale:.2f}")
                st.download_button("SCARICA PDF", pdf_data, f"{c_nome}.pdf", "application/pdf")

# =======================================================
# PAGINA 3: ARCHIVIO
# =======================================================
elif st.session_state['pagina'] == "archivio":
    if st.button("⬅ HOME"): vai("home")
    st.title("ARCHIVIO")
    
    if not st.session_state['archivio']:
        st.write("Nessun preventivo.")
    
    for item in reversed(st.session_state['archivio']):
        st.write("---")
        st.subheader(item['cli'])
        st.write(f"Totale: € {item['tot']:.2f}")
        st.download_button("SCARICA", item['pdf'], key=str(item))

# =======================================================
# PAGINA 4: SETTINGS
# =======================================================
elif st.session_state['pagina'] == "settings":
    if st.button("⬅ SALVA E ESCI"): vai("home")
    
    st.title("DATI DITTA")
    st.info("Inserisci qui i tuoi dati per l'intestazione")
    
    d = st.session_state['ditta']
    
    new_logo = st.file_uploader("Logo")
    if new_logo:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(new_logo.getvalue())
            d['logo'] = tmp.name
            
    d['nome'] = st.text_input("Nome Ditta", d['nome'])
    d['indirizzo'] = st.text_input("Indirizzo", d['indirizzo'])
    d['citta'] = st.text_input("Città", d['citta'])
    d['piva'] = st.text_input("P.IVA", d['piva'])
    d['tel'] = st.text_input("Telefono", d['tel'])
    st.session_state['ditta'] = d
