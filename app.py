import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Preventivi Pro", page_icon="🛠️", layout="wide")

# --- FUNZIONE PER GENERARE IL PDF ---
def crea_pdf(dati_preventivo, dati_azienda, dati_cliente):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione e Logo
    pdf.set_font("Arial", 'B', 16)
    # Se c'è un logo caricato (è un file temporaneo)
    if dati_azienda['logo_path']:
        try:
            pdf.image(dati_azienda['logo_path'], 10, 8, 33)
            pdf.cell(40) # Sposta a destra dopo il logo
        except:
            pass # Se fallisce ignora il logo
            
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

    # Tabella Dettagli
    pdf.set_fill_color(200, 220, 255)
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
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Preventivo generato automaticamente. I prezzi si intendono IVA esclusa se non specificato.", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA UTENTE ---

# 1. SIDEBAR: DATI AZIENDA (Tuoi dati)
st.sidebar.header("🛠️ I Tuoi Dati (Impostazioni)")
logo_file = st.sidebar.file_uploader("Carica il tuo Logo (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
nome_azienda = st.sidebar.text_input("Nome Ditta / Tuo Nome", "Edil Piastrelle Rossi")
piva = st.sidebar.text_input("Partita IVA", "IT00000000000")
telefono = st.sidebar.text_input("Telefono", "333 1234567")

# Gestione logo temporaneo per il PDF
logo_path = None
if logo_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(logo_file.getvalue())
        logo_path = tmp_file.name

dati_azienda = {"nome_azienda": nome_azienda, "piva": piva, "telefono": telefono, "logo_path": logo_path}

# 2. AREA PRINCIPALE
st.title("📑 Generatore Preventivi & Calcolatore")

tab1, tab2 = st.tabs(["📐 Calcolo & Preventivo", "ℹ️ Istruzioni"])

with tab1:
    # --- SEZIONE A: DATI CLIENTE ---
    st.subheader("1. Dati Cliente & Cantiere")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        c_nome = st.text_input("Nome Cliente")
        c_indirizzo = st.text_input("Indirizzo Residenza")
    with col_c2:
        c_cantiere = st.text_input("Indirizzo Cantiere (se diverso)")
        c_email = st.text_input("Email Cliente")

    st.markdown("---")

    # --- SEZIONE B: MISURE E TECNICA ---
    st.subheader("2. Misure Pavimento")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        lunghezza = st.number_input("Lunghezza Stanza (m)", 0.0, step=0.1)
        larghezza = st.number_input("Larghezza Stanza (m)", 0.0, step=0.1)
    
    with col_m2:
        tipo_posa = st.selectbox("Tipo di Posa (Sfrido)", ["Dritta (10%)", "Diagonale (15%)"])
        percentuale_sfrido = 10 if "Dritta" in tipo_posa else 15
        
    with col_m3:
        mq_netti = lunghezza * larghezza
        mq_calcolati = mq_netti + (mq_netti * percentuale_sfrido / 100)
        st.metric("Mq da Acquistare (con sfrido)", f"{mq_calcolati:.2f} mq", help=f"Base: {mq_netti:.2f}mq + {percentuale_sfrido}%")

    st.markdown("---")

    # --- SEZIONE C: MATERIALI E FORMATI ---
    st.subheader("3. Calcolo Materiali (Automatico)")
    
    tipo_materiale = st.radio("Seleziona Materiale:", ["Piastrelle Standard", "Grandi Formati / Lastre", "Parquet / Legno", "Rivestimento Muro"], horizontal=True)

    col_mat1, col_mat2 = st.columns(2)
    
    with col_mat1:
        st.markdown("**Dimensioni Singola Piastrella (cm)**")
        p_lato_a = st.number_input("Lato A (cm)", value=60)
        p_lato_b = st.number_input("Lato B (cm)", value=60)
        
        # Calcolo pezzi
        if p_lato_a > 0 and p_lato_b > 0 and mq_calcolati > 0:
            area_piastrella_mq = (p_lato_a * p_lato_b) / 10000 # cm2 to m2
            numero_piastrelle = mq_calcolati / area_piastrella_mq
            st.info(f"🧱 Serviranno circa **{int(numero_piastrelle) + 1} piastrelle**")
        
    with col_mat2:
        st.markdown("**Calcolo Colla**")
        consumo_colla = st.slider("Consumo Colla (kg/mq)", 3.0, 10.0, 5.0, help="Standard 5kg, Grandi formati 7-8kg")
        peso_sacco = 25 # Standard
        kg_totali_colla = mq_netti * consumo_colla # La colla si calcola sul netto o lordo? Di solito netto + piccolo margine
        sacchi_colla = (kg_totali_colla / peso_sacco) 
        st.info(f"🧪 Serviranno circa **{int(sacchi_colla) + 1} sacchi** da 25kg ({kg_totali_colla:.1f} kg totali)")

    st.markdown("---")

    # --- SEZIONE D: PREZZI ---
    st.subheader("4. Costi per Preventivo")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        prezzo_mat = st.number_input("Costo Materiale (€/mq)", 0.0, step=1.0)
    with col_p2:
        prezzo_posa = st.number_input("Costo Manodopera (€/mq)", 0.0, step=1.0)
    with col_p3:
        costo_colla_sacco = st.number_input("Costo Colla (€/sacco)", 0.0, value=25.0)

    # --- CALCOLO FINALE ---
    if st.button("CALCOLA TOTALE E GENERA PDF 🚀"):
        if mq_netti > 0:
            # Calcoli economici
            tot_materiale = mq_calcolati * prezzo_mat
            tot_posa = mq_netti * prezzo_posa
            tot_colla = (int(sacchi_colla) + 1) * costo_colla_sacco
            
            # Preparazione dati per PDF
            voci_preventivo = [
                {"desc": f"Fornitura {tipo_materiale} (inc. sfrido {percentuale_sfrido}%)", "qta": f"{mq_calcolati:.2f} mq", "prezzo": prezzo_mat, "totale": tot_materiale},
                {"desc": "Manodopera / Posa in opera", "qta": f"{mq_netti:.2f} mq", "prezzo": prezzo_posa, "totale": tot_posa},
                {"desc": f"Fornitura Colla ({int(sacchi_colla)+1} sacchi)", "qta": f"{int(sacchi_colla)+1} pz", "prezzo": costo_colla_sacco, "totale": tot_colla}
            ]
            
            totale_preventivo = tot_materiale + tot_posa + tot_colla
            
            st.success(f"✅ Preventivo calcolato: € {totale_preventivo:.2f}")
            
            # Generazione PDF
            pdf_bytes = crea_pdf(voci_preventivo, dati_azienda, {"nome": c_nome, "indirizzo": c_indirizzo, "cantiere": c_cantiere})
            
            st.download_button(
                label="📥 SCARICA PREVENTIVO PDF",
                data=pdf_bytes,
                file_name=f"Preventivo_{c_nome.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Inserisci le misure per calcolare!")

with tab2:
    st.write("### Guida all'uso")
    st.write("1. Apri la barra laterale (a sinistra) per inserire il tuo Logo e Nome Ditta.")
    st.write("2. Inserisci i dati del cliente.")
    st.write("3. Inserisci misure e formato piastrella.")
    st.write("4. Clicca su Calcola per vedere il totale e scaricare il PDF.")
