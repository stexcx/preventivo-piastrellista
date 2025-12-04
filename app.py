import streamlit as st
from fpdf import FPDF
import tempfile
import datetime

# --- CONFIGURAZIONE E STILE ---
st.set_page_config(page_title="Preventivi Pro", page_icon="🛠️", layout="wide")

# CSS per Sidebar visibile
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #e3f2fd; /* Azzurro chiaro */
        border-right: 2px solid #2196f3;
    }
    [data-testid="stSidebar"] h1, h2, h3 { color: #0d47a1; }
    /* Titoli sezioni principali */
    h3 { color: #1565c0; border-bottom: 2px solid #eee; padding-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE MEMORIA ARCHIVIO ---
if 'archivio_preventivi' not in st.session_state:
    st.session_state['archivio_preventivi'] = []

# --- FUNZIONI DI CALCOLO E PDF ---
def stima_colla(lato_a, lato_b):
    area_cmq = lato_a * lato_b
    if area_cmq <= 0: return 0
    elif area_cmq <= 1200: return 4.5
    elif area_cmq <= 3600: return 5.5
    else: return 7.0

def crea_pdf(dati_preventivo, dati_azienda, dati_cliente, totali):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione
    pdf.set_font("Arial", 'B', 16)
    if dati_azienda['logo_path']:
        try:
            pdf.image(dati_azienda['logo_path'], 10, 8, 33)
            pdf.cell(40)
        except: pass
            
    pdf.cell(0, 10, f"Preventivo: {dati_azienda['nome_azienda']}", ln=True, align='R')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"P.IVA: {dati_azienda['piva']} | Tel: {dati_azienda['telefono']}", ln=True, align='R')
    pdf.line(10, 30, 200, 30)
    pdf.ln(20)

    # Cliente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Dati Cliente:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Nome: {dati_cliente['nome']}", ln=True)
    pdf.cell(0, 8, f"Cantiere: {dati_cliente['cantiere']}", ln=True)
    pdf.ln(10)

    # Tabella
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Descrizione", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Quantità", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Prezzo Unit.", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Totale", 1, 1, 'C', 1)

    pdf.set_font("Arial", size=10)
    for voce in dati_preventivo:
        pdf.cell(90, 10, voce['desc'], 1)
        pdf.cell(30, 10, str(voce['qta']), 1, 0, 'C')
        pdf.cell(30, 10, f"E {voce['prezzo']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"E {voce['totale']:.2f}", 1, 1, 'R')

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, "TOTALE STIMATO:", 0, 0, 'R')
    pdf.cell(40, 10, f"E {totali:.2f}", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA: BARRA LATERALE ---
st.sidebar.title("NAVIGAZIONE")
menu_scelta = st.sidebar.radio("Vai a:", ["🧮 Calcolatore", "📂 Archivio Preventivi"])
st.sidebar.markdown("---")

st.sidebar.header("🛠️ Dati Azienda")
logo_file = st.sidebar.file_uploader("Carica Logo", type=['png', 'jpg', 'jpeg'])
nome_azienda = st.sidebar.text_input("Nome Ditta", "Edil Rossi")
piva = st.sidebar.text_input("P.IVA", "IT00000000000")
telefono = st.sidebar.text_input("Telefono", "333 0000000")

logo_path = None
if logo_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(logo_file.getvalue())
        logo_path = tmp_file.name
dati_azienda = {"nome_azienda": nome_azienda, "piva": piva, "telefono": telefono, "logo_path": logo_path}

# =======================================================
# PAGINA 1: CALCOLATORE
# =======================================================
if menu_scelta == "🧮 Calcolatore":
    st.title("Nuovo Preventivo")

    # --- 1. DATI CLIENTE ---
    with st.expander("👤 Dati Cliente", expanded=True):
        col_c1, col_c2 = st.columns(2)
        c_nome = col_c1.text_input("Nome Cliente")
        c_cantiere = col_c2.text_input("Indirizzo Cantiere")

    # --- 2. MISURE AMBIENTE (SOLO PERIMETRALI) ---
    st.subheader("1. Misure Ambiente")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        lunghezza = st.number_input("Lunghezza (metri)", 0.0, step=0.1)
    with col_m2:
        larghezza = st.number_input("Larghezza (metri)", 0.0, step=0.1)
    with col_m3:
        # Calcolo immediato dell'area
        mq_netti = lunghezza * larghezza
        st.metric("📏 Superficie Netta", f"{mq_netti:.2f} mq")

    st.markdown("---")

    # --- 3. MATERIALI E POSA (Dipende dai mq sopra) ---
    st.subheader("2. Scelta Materiali & Posa")
    
    if mq_netti > 0:
        col_mat1, col_mat2 = st.columns(2)
        
        with col_mat1:
            st.markdown("##### Piastrelle & Posa")
            # Menu formati
            formato_str = st.selectbox("Formato Piastrella", ["60x60", "30x30", "20x120 (Legno)", "80x80", "120x120", "Altro"])
            if formato_str == "Altro":
                lato_a = st.number_input("Lato A (cm)", 0.0)
                lato_b = st.number_input("Lato B (cm)", 0.0)
            else:
                parti = formato_str.split(" ")[0].split("x")
                lato_a, lato_b = float(parti[0]), float(parti[1])
            
            # Posa e Sfrido
            tipo_posa = st.radio("Tipo Posa", ["Dritta", "Diagonale"], horizontal=True)
            if tipo_posa == "Dritta":
                sfrido_auto = 10
            else:
                sfrido_auto = 15
            st.info(f"Sfrido applicato: **{sfrido_auto}%**")
            
            # Calcolo Mq totali acquisto
            mq_acquisto = mq_netti + (mq_netti * sfrido_auto / 100)
            st.metric("📦 Da Acquistare (Mq)", f"{mq_acquisto:.2f} mq")

        with col_mat2:
            st.markdown("##### Colla (Automatica)")
            consumo = stima_colla(lato_a, lato_b)
            kg_totali = mq_netti * consumo
            sacchi = int(kg_totali / 25) + 1
            
            st.write(f"Formato {lato_a}x{lato_b} → Consumo stimato: **{consumo} kg/mq**")
            st.metric("Sacchi Colla (25kg)", f"{sacchi} pz", f"{kg_totali:.1f} kg tot")

        st.markdown("---")

        # --- 4. COSTI ---
        st.subheader("3. Costi")
        col_p1, col_p2, col_p3 = st.columns(3)
        p_piastrella = col_p1.number_input("Costo Piastrella (€/mq)", 0.0, step=1.0)
        p_manodopera = col_p2.number_input("Costo Manodopera (€/mq)", 0.0, step=1.0)
        p_colla = col_p3.number_input("Costo Colla (€/sacco)", 25.0, step=0.5)

        # --- PULSANTE CALCOLA ---
        if st.button("CALCOLA E SALVA IN ARCHIVIO 💾"):
            # Calcoli finali
            tot_piastrelle = mq_acquisto * p_piastrella
            tot_manodopera = mq_netti * p_manodopera # Manodopera di solito su reale, o su acquisto? Metto reale standard
            tot_colla = sacchi * p_colla
            totale_preventivo = tot_piastrelle + tot_manodopera + tot_colla
            
            # Voci per PDF
            voci = [
                {"desc": f"Piastrelle {formato_str} (inc. {sfrido_auto}% sfrido)", "qta": f"{mq_acquisto:.2f} mq", "prezzo": p_piastrella, "totale": tot_piastrelle},
                {"desc": f"Posa in opera ({tipo_posa})", "qta": f"{mq_netti:.2f} mq", "prezzo": p_manodopera, "totale": tot_manodopera},
                {"desc": f"Colla e materiale consumo ({sacchi} sacchi)", "qta": f"{sacchi} pz", "prezzo": p_colla, "totale": tot_colla}
            ]
            
            # Genera PDF
            pdf_data = crea_pdf(voci, dati_azienda, {"nome": c_nome, "cantiere": c_cantiere}, totale_preventivo)
            
            # Salva in Archivio
            nuovo_record = {
                "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cliente": c_nome,
                "totale": totale_preventivo,
                "pdf": pdf_data
            }
            st.session_state['archivio_preventivi'].append(nuovo_record)
            
            st.success(f"✅ Preventivo di € {totale_preventivo:.2f} salvato in archivio!")
            st.download_button("📥 SCARICA PDF ORA", pdf_data, f"Prev_{c_nome}.pdf", "application/pdf")
            
    else:
        st.warning("Inserisci le misure dell'ambiente per sbloccare i materiali.")

# =======================================================
# PAGINA 2: ARCHIVIO
# =======================================================
elif menu_scelta == "📂 Archivio Preventivi":
    st.title("📂 Archivio Preventivi")
    
    if len(st.session_state['archivio_preventivi']) == 0:
        st.info("L'archivio è vuoto. Vai su 'Calcolatore' per crearne uno.")
    else:
        for i, doc in enumerate(reversed(st.session_state['archivio_preventivi'])):
            with st.expander(f"📄 {doc['cliente']} - € {doc['totale']:.2f} ({doc['data']})"):
                st.write(f"**Cliente:** {doc['cliente']}")
                st.write(f"**Data:** {doc['data']}")
                st.write(f"**Totale:** € {doc['totale']:.2f}")
                
                # Bottone per riscaricare il PDF
                st.download_button(
                    label="📥 Riscarica PDF",
                    data=doc['pdf'],
                    file_name=f"Preventivo_{doc['cliente']}.pdf",
                    mime="application/pdf",
                    key=f"btn_{i}"
                )
