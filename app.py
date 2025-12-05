import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Calcola & Posa", page_icon="logo.jpg", layout="wide")

# CSS: Stile Blu/Arancione
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0e2b48; color: white; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] span { color: white !important; }
    [data-testid="stSidebar"] input { color: #333 !important; }
    h1, h2, h3 { color: #e67e22; }
    div.stMetric { background-color: #fcfcfc; padding: 10px; border-radius: 8px; border-left: 5px solid #e67e22; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    div.stButton > button { background-color: #e67e22; color: white; border: none; font-weight: bold; width: 100%; padding: 10px; font-size: 18px;}
    div.stButton > button:hover { background-color: #d35400; color: white; }
</style>
""", unsafe_allow_html=True)

if 'archivio_preventivi' not in st.session_state:
    st.session_state['archivio_preventivi'] = []

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
    
    # --- 1. INTESTAZIONE AZIENDA COMPLETA ---
    # Logo
    if dati_azienda['logo_path'] and os.path.exists(dati_azienda['logo_path']):
        try: pdf.image(dati_azienda['logo_path'], 10, 8, 30) 
        except: pass
    elif os.path.exists("logo.jpg"):
         try: pdf.image("logo.jpg", 10, 8, 30)
         except: pass

    # Dati Testuali (Allineati a destra del logo)
    start_x = 45 # Punto di inizio testo dopo il logo
    
    pdf.set_xy(start_x, 10)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(14, 43, 72) # Blu
    pdf.cell(0, 8, dati_azienda['nome_azienda'], ln=True)
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(50, 50, 50) # Grigio scuro
    
    # Indirizzo
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"{dati_azienda['indirizzo']} - {dati_azienda['citta']}", ln=True)
    
    # Piva e Tel
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"P.IVA: {dati_azienda['piva']} | Tel: {dati_azienda['telefono']}", ln=True)
    
    # Email e IBAN
    pdf.set_x(start_x)
    pdf.cell(0, 5, f"Email: {dati_azienda['email']}", ln=True)
    
    if dati_azienda['iban']:
        pdf.set_x(start_x)
        pdf.cell(0, 5, f"IBAN: {dati_azienda['iban']}", ln=True)

    pdf.ln(10)
    pdf.set_draw_color(230, 126, 34) # Arancione
    pdf.set_line_width(1)
    pdf.line(10, 45, 200, 45)

    # --- 2. DATI CLIENTE ---
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

    # --- 3. TABELLA ---
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
    
    # --- 4. TOTALE ---
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

# QUI C'ERA L'ERRORE: Ora è corretto!
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_column_width=True)

st.sidebar.title("NAVIGAZIONE")
menu = st.sidebar.radio("Vai a:", ["🧮 Calcolatore", "📂 Archivio"])
st.sidebar.markdown("---")

# --- NUOVA SIDEBAR CON DATI COMPLETI ---
st.sidebar.header("🛠️ Dati Azienda (Completi)")
st.sidebar.info("Questi dati appariranno nell'intestazione del PDF")

logo_in = st.sidebar.file_uploader("Carica Logo", type=['png','jpg'])
d_nome = st.sidebar.text_input("Nome Ditta / Ragione Sociale", "Edil Rossi")
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

# Raccogliamo tutti i dati in un dizionario
dati_azienda = {
    "nome_azienda": d_nome, 
    "indirizzo": d_indirizzo,
    "citta": d_citta,
    "piva": d_piva, 
    "telefono": d_tel, 
    "email": d_email,
    "iban": d_iban,
    "logo_path": logo_path
}

# === CALCOLATORE ===
if menu == "🧮 Calcolatore":
    st.title("Nuovo Preventivo")

    # 1. CLIENTE (Form Completo)
    with st.expander("👤 Dati Cliente Completi", expanded=True):
        col_a1, col_a2 = st.columns(2)
        c_nome = col_a1.text_input("Nome/Ragione Sociale Cliente")
        c_cf = col_a2.text_input("Codice Fiscale / P.IVA")
        
        col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
        c_indirizzo = col_b1.text_input("Via e N. Civico")
        c_citta = col_b2.text_input("Città")
        c_cap = col_b3.text_input("CAP")
        
        col_c1, col_c2 = st.columns(2)
        c_tel = col_c1.text_input("Telefono")
        c_cantiere = col_c2.text_input("Indirizzo Cantiere (se diverso)")
        if not c_cantiere: c_cantiere = f"{c_indirizzo}, {c_citta}"

    # 2. MISURE (Input Smart)
    st.subheader("1. Misure Ambiente")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    lunghezza = col_m1.number_input("Lunghezza (m)", value=None, step=0.1, placeholder="0.00")
    larghezza = col_m2.number_input("Larghezza (m)", value=None, step=0.1, placeholder="0.00")
    
    l_calc = pulisci_num(lunghezza)
    w_calc = pulisci_num(larghezza)
    mq_netti = l_calc * w_calc
    col_m3.metric("📏 Superficie", f"{mq_netti:.2f} mq")
    st.markdown("---")

    # 3. MATERIALI
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

        # 4. COSTI
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
                st.error("Manca il nome del cliente!")
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
