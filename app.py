import streamlit as st
from fpdf import FPDF
import tempfile
import datetime
import math # Importante per arrotondare i pacchi

# --- CONFIGURAZIONE E STILE ---
st.set_page_config(page_title="Preventivi Pro", page_icon="🛠️", layout="wide")

# CSS per Sidebar visibile
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #e3f2fd; 
        border-right: 2px solid #2196f3;
    }
    [data-testid="stSidebar"] h1, h2, h3 { color: #0d47a1; }
    h3 { color: #1565c0; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    div.stMetric { background-color: #f9f9f9; padding: 10px; border-radius: 5px; border: 1px solid #eee; }
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

# --- INTERFACCIA ---
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
# PAGINA CALCOLATORE
# =======================================================
if menu_scelta == "🧮 Calcolatore":
    st.title("Nuovo Preventivo")

    # 1. CLIENTE
    with st.expander("👤 Dati Cliente", expanded=True):
        col_c1, col_c2 = st.columns(2)
        c_nome = col_c1.text_input("Nome Cliente")
        c_cantiere = col_c2.text_input("Indirizzo Cantiere")

    # 2. MISURE AMBIENTE
    st.subheader("1. Misure Ambiente")
    col_m1, col_m2, col_m3 = st.columns(3)
    lunghezza = col_m1.number_input("Lunghezza (m)", 0.0, step=0.1)
    larghezza = col_m2.number_input("Larghezza (m)", 0.0, step=0.1)
    mq_netti = lunghezza * larghezza
    col_m3.metric("📏 Superficie Netta", f"{mq_netti:.2f} mq")
    st.markdown("---")

    # 3. MATERIALI
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
            
            # NUOVO: CALCOLO PACCHI
            st.markdown("---")
            mq_pacco = st.number_input("Mq contenuti in 1 Pacco (vedi scatola)", value=1.44, step=0.01)
            
            if mq_pacco > 0:
                pacchi_reali = math.ceil(mq_necessari / mq_pacco) # Arrotonda per eccesso
                mq_totali_acquisto = pacchi_reali * mq_pacco # Mq che compri davvero
                
                st.info(f"Fabbisogno: {mq_necessari:.2f} mq")
                st.metric("📦 Pacchi da Ordinare", f"{pacchi_reali} pz", f"Totale merce: {mq_totali_acquisto:.2f} mq")
            else:
                pacchi_reali = 0
                mq_totali_acquisto = 0

        with col_mat2:
            st.markdown("##### 🧪 Colla")
            consumo = stima_colla(lato_a, lato_b)
            kg_totali = mq_netti * consumo
            sacchi_reali = math.ceil(kg_totali / 25) # Arrotonda sacchi
            
            st.write(f"Consumo stimato: **{consumo} kg/mq**")
            st.metric("Sacchi Colla (25kg)", f"{sacchi_reali} pz", f"Totale: {sacchi_reali*25} kg")

        st.markdown("---")

        # 4. COSTI (FLESSIBILI)
        st.subheader("3. Costi & Preventivo")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        # Costo Piastrelle
        with col_p1:
            st.markdown("**Piastrelle**")
            modo_p = st.radio("Prezzo unitario:", ["Al Mq", "Al Pacco"], key="modo_p")
            prezzo_p = st.number_input(f"Costo (€)", 0.0, step=1.0, key="costo_p")
            
            if modo_p == "Al Mq":
                tot_piastrelle = mq_totali_acquisto * prezzo_p # Paghi i mq totali dei pacchi
                desc_p = f"Fornitura ({pacchi_reali} pacchi da {mq_pacco}mq)"
                unit_p = f"€ {prezzo_p}/mq"
            else:
                tot_piastrelle = pacchi_reali * prezzo_p # Paghi a pacco
                desc_p = f"Fornitura ({pacchi_reali} pacchi)"
                unit_p = f"€ {prezzo_p}/pacco"
                
            st.caption(f"Tot: € {tot_piastrelle:.2f}")

        # Costo Manodopera (Sempre al mq reale o lordo?) Di solito netto calpestabile
        with col_p2:
            st.markdown("**Manodopera**")
            st.write("Calcolata su Mq netti")
            prezzo_m = st.number_input("Costo al Mq (€)", 0.0, step=1.0)
            tot_manodopera = mq_netti * prezzo_m
            st.caption(f"Tot: € {tot_manodopera:.2f}")

        # Costo Colla
        with col_p3:
            st.markdown("**Colla**")
            modo_c = st.radio("Prezzo unitario:", ["Al Sacco", "Al Mq (Stima)"], key="modo_c")
            prezzo_c = st.number_input(f"Costo (€)", 0.0, step=0.5, key="costo_c")
            
            if modo_c == "Al Sacco":
                tot_colla = sacchi_reali * prezzo_c
                desc_c = f"Colla ({sacchi_reali} sacchi)"
                unit_c = f"€ {prezzo_c}/sacco"
            else:
                tot_colla = mq_netti * prezzo_c # Stima al mq
                desc_c = f"Materiale consumo/Colla (Stima su {mq_netti}mq)"
                unit_c = f"€ {prezzo_c}/mq"
                
            st.caption(f"Tot: € {tot_colla:.2f}")

        # CALCOLO FINALE
        if st.button("CALCOLA E SALVA 💾"):
            totale_preventivo = tot_piastrelle + tot_manodopera + tot_colla
            
            voci = [
                {"desc": desc_p, "qta": f"{mq_totali_acquisto:.2f} mq" if modo_p=="Al Mq" else f"{pacchi_reali} pz", "prezzo": prezzo_p, "totale": tot_piastrelle},
                {"desc": f"Posa in opera ({tipo_posa})", "qta": f"{mq_netti:.2f} mq", "prezzo": prezzo_m, "totale": tot_manodopera},
                {"desc": desc_c, "qta": f"{sacchi_reali} pz" if modo_c=="Al Sacco" else "1", "prezzo": prezzo_c, "totale": tot_colla}
            ]
            
            pdf_data = crea_pdf(voci, dati_azienda, {"nome": c_nome, "cantiere": c_cantiere}, totale_preventivo)
            
            nuovo = {
                "data": datetime.datetime.now().strftime("%d/%m/%Y"),
                "cliente": c_nome,
                "totale": totale_preventivo,
                "pdf": pdf_data
            }
            st.session_state['archivio_preventivi'].append(nuovo)
            
            st.success(f"Preventivo salvato! Totale: € {totale_preventivo:.2f}")
            st.download_button("📥 SCARICA PDF", pdf_data, f"Prev_{c_nome}.pdf", "application/pdf")
            
    else:
        st.info("Inserisci le misure per iniziare.")

# =======================================================
# PAGINA ARCHIVIO
# =======================================================
elif menu_scelta == "📂 Archivio Preventivi":
    st.title("📂 Archivio")
    if not st.session_state['archivio_preventivi']:
        st.write("Nessun preventivo.")
    else:
        for i, doc in enumerate(reversed(st.session_state['archivio_preventivi'])):
            with st.expander(f"{doc['cliente']} - € {doc['totale']:.2f} ({doc['data']})"):
                st.download_button("📥 Scarica PDF", doc['pdf'], key=f"b_{i}")
