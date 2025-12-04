import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math
import os

# --- CONFIGURAZIONE E STILE (Colori del Logo) ---
st.set_page_config(page_title="Calcola & Posa", page_icon="logo.jpg", layout="wide")

# CSS PERSONALIZZATO: Blu scuro e Arancione
st.markdown("""
<style>
    /* Sfondo Sidebar Blu Scuro */
    [data-testid="stSidebar"] {
        background-color: #0e2b48; /* Blu scuro del logo */
        color: white;
    }
    /* Testi nella Sidebar bianchi */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
        color: white !important;
    }
    /* Titoli principali Arancioni */
    h1, h2, h3 {
        color: #e67e22; /* Arancione del logo */
    }
    /* Metriche con bordo arancione */
    div.stMetric {
        background-color: #fcfcfc;
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #e67e22;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    /* Bottone Arancione */
    div.stButton > button {
        background-color: #e67e22;
        color: white;
        border: none;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

if 'archivio_preventivi' not in st.session_state:
    st.session_state['archivio_preventivi'] = []

# --- FUNZIONI ---
def stima_colla(lato_a, lato_b):
    area_cmq = lato_a * lato_b
    if area_cmq <= 0: return 0
    elif area_cmq <= 1200: return 4.5
    elif area_cmq <= 3600: return 5.5
    else: return 7.0

# Funzione PDF con gestione Simbolo Euro
class PDF(FPDF):
    def header(self):
        # Niente header automatico, lo facciamo manuale
        pass

def crea_pdf(dati_preventivo, dati_azienda, dati_cliente, totali):
    pdf = PDF()
    pdf.add_page()
    
    # --- LOGO E INTESTAZIONE ---
    # Carica logo caricato dall'utente O quello di default del sistema
    if dati_azienda['logo_path'] and os.path.exists(dati_azienda['logo_path']):
        try:
            # Logo a sinistra
            pdf.image(dati_azienda['logo_path'], 10, 8, 30) 
        except: pass
    elif os.path.exists("logo.jpg"):
         try:
            pdf.image("logo.jpg", 10, 8, 30)
         except: pass

    # Titolo Azienda (Spostato a destra del logo)
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(14, 43, 72) # Blu scuro
    pdf.cell(40) # Spazio per il logo
    pdf.cell(0, 10, dati_azienda['nome_azienda'], ln=True)
    
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40)
    pdf.cell(0, 6, f"P.IVA: {dati_azienda['piva']} | Tel: {dati_azienda['telefono']}", ln=True)
    pdf.ln(15)
    
    # Linea divisoria Arancione
    pdf.set_draw_color(230, 126, 34) # Arancione
    pdf.set_line_width(1)
    pdf.line(10, 35, 200, 35)
    pdf.set_text_color(0, 0, 0) # Reset nero

    # --- DATI CLIENTE ---
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, f"Preventivo per: {dati_cliente['nome']}", ln=True, fill=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 6, f"Cantiere: {dati_cliente['cantiere']}", ln=True)
    pdf.cell(0, 6, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)

    # --- TABELLA ---
    # Intestazione tabella Blu
    pdf.set_fill_color(14, 43, 72) 
    pdf.set_text_color(255, 255, 255) # Bianco
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Descrizione", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Quantita'", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Prezzo Unit.", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Totale", 1, 1, 'C', 1)

    # Righe Tabella
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0) # Nero
    
    for voce in dati_preventivo:
        pdf.cell(90, 10, voce['desc'], 1)
        pdf.cell(30, 10, str(voce['qta']), 1, 0, 'C')
        # Usiamo "EUR" o "E" perché il simbolo € in FPDF standard a volte rompe la codifica
        # Ma proviamo il trucco del chr(128) per Windows-1252
        pdf.cell(30, 10, f"Euro {voce['prezzo']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"Euro {voce['totale']:.2f}", 1, 1, 'R')

    pdf.ln(5)
    
    # --- TOTALE ---
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(230, 126, 34) # Arancione
    pdf.cell(150, 10, "TOTALE STIMATO:", 0, 0, 'R')
    pdf.cell(40, 10, f"Euro {totali:.2f}", 1, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "I prezzi si intendono IVA esclusa. Preventivo valido 30 giorni.", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INTERFACCIA ---
# Mostriamo il logo nella Sidebar
st.sidebar.image("logo.jpg", use_column_width=True)
st.sidebar.title("NAVIGAZIONE")
menu_scelta = st.sidebar.radio("Vai a:", ["🧮 Calcolatore", "📂 Archivio"])
st.sidebar.markdown("---")

st.sidebar.header("🛠️ Dati Azienda")
logo_file = st.sidebar.file_uploader("Carica altro Logo", type=['png', 'jpg', 'jpeg'])
nome_azienda = st.sidebar.text_input("Nome Ditta", "Edil Rossi", help="Apparirà sul PDF")
piva = st.sidebar.text_input("P.IVA", "IT00000000000")
telefono = st.sidebar.text_input("Telefono", "333 0000000")

logo_path = None
if logo_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(logo_file.getvalue())
        logo_path = tmp_file.name
dati_azienda = {"nome_azienda": nome_azienda, "piva": piva, "telefono": telefono, "logo_path": logo_path}

# =======================================================
# CALCOLATORE
# =======================================================
if menu_scelta == "🧮 Calcolatore":
    st.title("Nuovo Preventivo")

    with st.expander("👤 Dati Cliente", expanded=True):
        col_c1, col_c2 = st.columns(2)
        c_nome = col_c1.text_input("Nome Cliente")
        c_cantiere = col_c2.text_input("Indirizzo Cantiere")

    st.subheader("1. Misure Ambiente")
    col_m1, col_m2, col_m3 = st.columns(3)
    lunghezza = col_m1.number_input("Lunghezza (m)", 0.0, step=0.1)
    larghezza = col_m2.number_input("Larghezza (m)", 0.0, step=0.1)
    mq_netti = lunghezza * larghezza
    col_m3.metric("📏 Superficie Netta", f"{mq_netti:.2f} mq")
    st.markdown("---")

    st.subheader("2. Materiali & Pacchi")
    
    if mq_netti > 0:
        col_mat1, col_mat2 = st.columns(2)
        
        with col_mat1:
            st.markdown("##### 🧱 Piastrelle")
            formato_str = st.selectbox("Formato", ["60x60", "30x30", "20x120 (Legno)", "80x80", "120x120", "Altro"])
            if formato_str == "Altro":
                lato_a = st.number_input("Lato A (cm)", 0.0)
                lato_b = st.number_input("Lato B (cm)", 0.0)
            else:
                parti = formato_str.split(" ")[0].split("x")
                lato_a, lato_b = float(parti[0]), float(parti[1])
            
            tipo_posa = st.radio("Posa", ["Dritta (Sfrido 10%)", "Diagonale (Sfrido 15%)"], horizontal=True)
            sfrido_perc = 10 if "Dritta" in tipo_posa else 15
            mq_necessari = mq_netti + (mq_netti * sfrido_perc / 100)
            
            st.markdown("---")
            mq_pacco = st.number_input("Mq in 1 Pacco", value=1.44, step=0.01)
            
            if mq_pacco > 0:
                pacchi_reali = math.ceil(mq_necessari / mq_pacco)
                mq_totali_acquisto = pacchi_reali * mq_pacco
                st.info(f"Fabbisogno con sfrido: {mq_necessari:.2f} mq")
                st.metric("📦 Pacchi da Ordinare", f"{pacchi_reali} pz", f"Totale merce: {mq_totali_acquisto:.2f} mq")
            else:
                pacchi_reali = 0
                mq_totali_acquisto = 0

        with col_mat2:
            st.markdown("##### 🧪 Colla")
            consumo = stima_colla(lato_a, lato_b)
            kg_totali = mq_netti * consumo
            sacchi_reali = math.ceil(kg_totali / 25)
            st.write(f"Consumo stimato: **{consumo} kg/mq**")
            st.metric("Sacchi Colla (25kg)", f"{sacchi_reali} pz", f"Totale: {sacchi_reali*25} kg")

        st.markdown("---")

        st.subheader("3. Costi & Preventivo")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            st.markdown("**Piastrelle**")
            modo_p = st.radio("Prezzo unitario:", ["Al Mq", "Al Pacco"], key="modo_p")
            prezzo_p = st.number_input(f"Costo (€)", 0.0, step=1.0, key="costo_p")
            if modo_p == "Al Mq":
                tot_piastrelle = mq_totali_acquisto * prezzo_p
                desc_p = f"Fornitura ({pacchi_reali} pacchi da {mq_pacco}mq)"
            else:
                tot_piastrelle = pacchi_reali * prezzo_p
                desc_p = f"Fornitura ({pacchi_reali} pacchi)"
            st.caption(f"Tot: € {tot_piastrelle:.2f}")

        with col_p2:
            st.markdown("**Manodopera**")
            st.write("Su Mq netti")
            prezzo_m = st.number_input("Costo al Mq (€)", 0.0, step=1.0)
            tot_manodopera = mq_netti * prezzo_m
            st.caption(f"Tot: € {tot_manodopera:.2f}")

        with col_p3:
            st.markdown("**Colla**")
            modo_c = st.radio("Calcolo:", ["Al Sacco", "Al Mq (Stima)"], key="modo_c")
            prezzo_c = st.number_input(f"Costo (€)", 0.0, step=0.5, key="costo_c")
            if modo_c == "Al Sacco":
                tot_colla = sacchi_reali * prezzo_c
                desc_c = f"Colla ({sacchi_reali} sacchi)"
            else:
                tot_colla = mq_netti * prezzo_c
                desc_c = f"Colla (Stima su {mq_netti}mq)"
            st.caption(f"Tot: € {tot_colla:.2f}")

        if st.button("CALCOLA E SALVA 💾"):
            totale_preventivo = tot_piastrelle + tot_manodopera + tot_colla
            
            voci = [
                {"desc": desc_p, "qta": f"{mq_totali_acquisto:.2f} mq" if modo_p=="Al Mq" else f"{pacchi_reali} pz", "prezzo": prezzo_p, "totale": tot_piastrelle},
                {"desc": f"Posa in opera ({tipo_posa})", "qta": f"{mq_netti:.2f} mq", "prezzo": prezzo_m, "totale": tot_manodopera},
                {"desc": desc_c, "qta": f"{sacchi_reali} pz" if modo_c=="Al Sacco" else "1", "prezzo": prezzo_c, "totale": tot_colla}
            ]
            
            # Generazione PDF
            pdf_data = crea_pdf(voci, dati_azienda, {"nome": c_nome, "cantiere": c_cantiere}, totale_preventivo)
            
            nuovo = {
                "data": datetime.datetime.now().strftime("%d/%m/%Y"),
                "cliente": c_nome,
                "totale": totale_preventivo,
                "pdf": pdf_data
            }
            st.session_state['archivio_preventivi'].append(nuovo)
            
            st.success(f"Preventivo salvato! Totale: € {totale_preventivo:.2f}")
            st.download_button("📥 SCARICA PDF CON LOGO", pdf_data, f"Prev_{c_nome}.pdf", "application/pdf")
            
    else:
        st.info("Inserisci le misure per iniziare.")

elif menu_scelta == "📂 Archivio":
    st.title("📂 Archivio")
    if not st.session_state['archivio_preventivi']:
        st.write("Nessun preventivo.")
    else:
        for i, doc in enumerate(reversed(st.session_state['archivio_preventivi'])):
            with st.expander(f"{doc['cliente']} - € {doc['totale']:.2f} ({doc['data']})"):
                st.download_button("📥 Scarica PDF", doc['pdf'], key=f"b_{i}")
