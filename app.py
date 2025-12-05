import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- CONFIGURAZIONE ---
# Gestione icona app
icona_app = "logo.png" if os.path.exists("logo.png") else "logo.jpg"
if not os.path.exists(icona_app): icona_app = None 

st.set_page_config(page_title="Calcola & Posa", page_icon=icona_app, layout="wide")

if 'archivio_preventivi' not in st.session_state:
    st.session_state['archivio_preventivi'] = []

# --- CSS PERFEZIONATO PER MOBILE E VISIBILITÀ ---
st.markdown("""
<style>
    /* 1. BARRA LATERALE (SIDEBAR) */
    [data-testid="stSidebar"] { 
        background-color: #0e2b48; 
    }
    
    /* Testi bianchi nella sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: white !important;
        font-size: 16px;
    }

    /* 2. MENU DI NAVIGAZIONE PIÙ GRANDE */
    div[role="radiogroup"] label {
        padding: 15px 10px; /* Più spazio per il dito */
        background-color: rgba(255,255,255,0.1); /* Leggero sfondo ai bottoni */
        margin-bottom: 5px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    div[role="radiogroup"] label p {
        font-size: 22px !important; /* Testo Molto Grande */
        font-weight: bold;
    }

    /* 3. RISULTATI (METRICHE) - FIX BIANCO SU BIANCO */
    div[data-testid="stMetric"] {
        background-color: #fff8e1 !important; /* Giallo chiarissimo */
        border: 2px solid #ffb300; /* Bordo Arancione */
        border-radius: 10px;
        padding: 15px;
        color: black !important; /* Forza testo nero */
    }
    
    /* Il numero del risultato (es. 25 mq) */
    div[data-testid="stMetricValue"] {
        color: #000000 !important; /* NERO ASSOLUTO */
        font-size: 28px !important;
        font-weight: bold;
    }
    
    /* L'etichetta (es. Superficie) */
    div[data-testid="stMetricLabel"] {
        color: #e65100 !important; /* Arancione scuro */
        font-weight: bold;
    }

    /* 4. TITOLI E BOTTONI */
    h1, h2, h3 { color: #e67e22; }
    
    div.stButton > button { 
        background-color: #e67e22; 
        color: white; 
        border: none; 
        font-weight: bold; 
        width: 100%; 
        padding: 15px; 
        font-size: 20px; /* Bottone calcola grande */
        border-radius: 12px;
    }
    div.stButton > button:hover { background-color: #d35400; color: white; }

    /* Logo centrato */
    [data-testid="stSidebar"] img {
        display: block; margin-left: auto; margin-right: auto; max-width: 90%;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI UTILI ---
def pulisci_num(valore):
    return 0.0 if valore is None else valore

def stima_colla(lato_a, lato_b):
    lato_a, lato_b = pulisci_num(lato_a), pulisci_num(lato_b)
    area_cmq = lato_a * lato_b
    if area_cmq <= 0: return 0
    elif area_cmq <= 1200: return 4.5
    elif area_cmq <= 3600: return 5.5
    else: return 7.0

# --- CLASSE PDF ---
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
    pdf.set_text_color(14, 43, 72) 
    pdf.cell(0, 8, dati_azienda['nome_azienda'], ln=True)
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(50, 50, 50) 
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"{dati_azienda['indirizzo']} - {dati_azienda['citta']}", ln=True)
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"P.IVA: {dati_azienda['piva']} | Tel: {dati_azienda['telefono']}", ln=True)
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"Email: {dati_azienda['email']}", ln=True)
    
    pdf.ln(10)
    pdf.set_draw_color(230, 126, 34) 
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
    pdf.set_fill_color(14, 43, 72) 
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
    pdf.set_text_color(230, 126, 34)
    pdf.cell(150, 10, "TOTALE STIMATO:", 0, 0, 'R')
    pdf.cell(40, 10, f"Euro {totali:.2f}", 1, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "I prezzi si intendono IVA esclusa.", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INTERFACCIA ---

# 1. MOSTRA LOGO
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_column_width=True)
elif os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_column_width=True)

st.sidebar.title("NAVIGAZIONE")

# 2. MENU RINOMINATO E GRANDI ICONE (Grazie al CSS sopra)
menu = st.sidebar.radio("Vai a:", ["🧮 Calcola", "📂 Archivio"])
st.sidebar.markdown("---")

st.sidebar.header("🛠️ Dati Azienda")
logo_in = st.sidebar.file_uploader("Carica Logo (PNG/JPG)", type=['png','jpg'])
d_nome = st.sidebar.text_input("Nome Ditta", "Edil Rossi")
d_indirizzo = st.sidebar.text_input("Indirizzo Sede", "Via Roma 1")
d_citta = st.sidebar.text_input("Città e CAP", "16100 Genova (GE)")
d_piva = st.sidebar.text_input("P.IVA / C.F.", "IT00000000000")
d_tel = st.sidebar.text_input("Telefono", "333 1234567")
d_email = st.sidebar.text_input("Email", "info@edilrossi.it")
d_iban = st.sidebar.text_input("IBAN (Opzionale)", "")

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
    st.title("Nuovo Preventivo")

    # DATI CLIENTE (Tastiera lettere)
    with st.expander("👤 Dati Cliente Completi", expanded=True):
        col_a1, col_a2 = st.columns(2)
        c_nome = col_a1.text_input("Nome/Ragione Sociale")
        c_cf = col_a2.text_input("Codice Fiscale / P.IVA")
        
        col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
        c_indirizzo = col_b1.text_input("Indirizzo")
        c_citta = col_b2.text_input("Città")
        c_cap = col_b3.text_input("CAP")
        
        col_c1, col_c2 = st.columns(2)
        c_tel = col_c1.text_input("Telefono")
        c_cantiere = col_c2.text_input("Cantiere (se diverso)")
        if not c_cantiere: c_cantiere = f"{c_indirizzo}, {c_citta}"

    # MISURE (Tastiera Numerica Automatica su Mobile)
    st.subheader("1. Misure Ambiente")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    # st.number_input apre automaticamente il tastierino numerico sul telefono
    lunghezza = col_m1.number_input("Lunghezza (m)", value=None, step=0.1, placeholder="0.00")
    larghezza = col_m2.number_input("Larghezza (m)", value=None, step=0.1, placeholder="0.00")
    
    mq_netti = pulisci_num(lunghezza) * pulisci_num(larghezza)
    
    # Questo risultato ora sarà GIALLO/ARANCIONE e ben visibile
    col_m3.metric("📏 Superficie", f"{mq_netti:.2f} mq")
    
    st.markdown("---")

    # MATERIALI
    st.subheader("2. Materiali")
    if mq_netti > 0:
        col_mat1, col_mat2 = st.columns(2)
        with col_mat1:
            st.markdown("**Piastrelle**")
            formato = st.selectbox("Formato", ["60x60", "30x30", "20x120 (Legno)", "80x80", "120x120", "Altro"])
            if formato == "Altro":
                lato_a = st.number_input("Lato A (cm)", value=None, placeholder="0")
                lato_b = st.number_input("Lato B (cm)", value=None, placeholder="0")
            else:
                p = formato.split(" ")[0].split("x")
                lato_a, lato_b = float(p[0]), float(p[1])
            
            tipo_posa = st.radio("Posa", ["Dritta (Sfrido 10%)", "Diagonale (Sfrido 15%)"], horizontal=True)
            sfrido = 10 if "Dritta" in tipo_posa else 15
            mq_nec = mq_netti + (mq_netti * sfrido / 100)
            
            mq_pacco = st.number_input("Mq in 1 Pacco", value=None, step=0.01, placeholder="Es. 1.44")
            mq_pacco_c = pulisci_num(mq_pacco)
            
            if mq_pacco_c > 0:
                pacchi = math.ceil(mq_nec / mq_pacco_c)
                mq_tot_acquisto = pacchi * mq_pacco_c
                st.info(f"Fabbisogno: {mq_nec:.2f} mq")
                st.metric("📦 Pacchi", f"{pacchi}", f"Tot: {mq_tot_acquisto:.2f} mq")
            else:
                pacchi, mq_tot_acquisto = 0, 0

        with col_mat2:
            st.markdown("**Colla**")
            cons = stima_colla(lato_a, lato_b)
            kg_tot = mq_netti * cons
            sacchi = math.ceil(kg_tot / 25)
            st.write(f"Consumo: **{cons} kg/mq**")
            st.metric("Sacchi (25kg)", f"{sacchi}", f"Tot: {sacchi*25} kg")

        st.markdown("---")

        # COSTI
        st.subheader("3. Costi")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Piastrelle**")
            modo_p = st.radio("Prezzo:", ["Al Mq", "Al Pacco"])
            prezzo_p = st.number_input("Costo Piastrella (€)", value=None, step=1.0, placeholder="0.00")
            prezzo_p_c = pulisci_num(prezzo_p)
            if modo_p == "Al Mq":
                tot_p = mq_tot_acquisto * prezzo_p_c
                desc_p = f"Fornitura ({pacchi} pacchi da {mq_pacco_c}mq)"
            else:
                tot_p = pacchi * prezzo_p_c
                desc_p = f"Fornitura ({pacchi} pacchi)"
            st.caption(f"Tot: € {tot_p:.2f}")

        with c2:
            st.markdown("**Manodopera**")
            prezzo_m = st.number_input("Costo Posa al Mq (€)", value=None, step=1.0, placeholder="0.00")
            prezzo_m_c = pulisci_num(prezzo_m)
            tot_m = mq_netti * prezzo_m_c
            st.caption(f"Tot: € {tot_m:.2f}")

        with c3:
            st.markdown("**Colla**")
            modo_c = st.radio("Prezzo:", ["Al Sacco", "Al Mq"])
            prezzo_c = st.number_input("Costo Colla (€)", value=None, step=0.5, placeholder="0.00")
            prezzo_c_c = pulisci_num(prezzo_c)
            if modo_c == "Al Sacco":
                tot_c = sacchi * prezzo_c_c
                desc_c = f"Colla ({sacchi} sacchi)"
            else:
                tot_c = mq_netti * prezzo_c_c
                desc_c = f"Materiale Consumo (Stima {mq_netti}mq)"
            st.caption(f"Tot: € {tot_c:.2f}")

        # CALCOLA
        if st.button("CALCOLA E GENERA PREVENTIVO 🚀"):
            if not c_nome:
                st.error("Inserisci il nome del cliente!")
            else:
                tot_gen = tot_p + tot_m + tot_c
                voci = [
                    {"desc": desc_p, "qta": f"{mq_tot_acquisto:.2f} mq" if modo_p=="Al Mq" else f"{pacchi}", "prezzo": prezzo_p_c, "totale": tot_p},
                    {"desc": f"Posa in opera ({tipo_posa})", "qta": f"{mq_netti:.2f} mq", "prezzo": prezzo_m_c, "totale": tot_m},
                    {"desc": desc_c, "qta": f"{sacchi}" if modo_c=="Al Sacco" else "1", "prezzo": prezzo_c_c, "totale": tot_c}
                ]
                
                d_cli = {
                    "nome": c_nome, "cf": c_cf, 
                    "indirizzo": c_indirizzo, "citta": c_citta, "cap": c_cap,
                    "telefono": c_tel, "cantiere": c_cantiere
                }
                
                pdf_bytes = crea_pdf(voci, dati_azienda, d_cli, tot_gen)
                
                rec = {"data": datetime.datetime.now().strftime("%d/%m/%Y"), "cliente": c_nome, "totale": tot_gen, "pdf": pdf_bytes}
                st.session_state['archivio_preventivi'].append(rec)
                
                st.success(f"Totale: € {tot_gen:.2f}")
                st.download_button("📥 SCARICA PDF", pdf_bytes, f"Prev_{c_nome}.pdf", "application/pdf")
    else:
        st.info("Inserisci le misure per iniziare.")

elif menu == "📂 Archivio":
    st.title("📂 Archivio")
    if not st.session_state['archivio_preventivi']:
        st.write("Nessun preventivo.")
    else:
        for i, doc in enumerate(reversed(st.session_state['archivio_preventivi'])):
            with st.expander(f"{doc['cliente']} - € {doc['totale']:.2f} ({doc['data']})"):
                st.download_button("📥 Scarica", doc['pdf'], key=f"b_{i}")
