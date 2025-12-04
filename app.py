import streamlit as st
import datetime

# --- IMPOSTAZIONI INIZIALI ---
st.set_page_config(page_title="Gestionale Piastrellista", page_icon="🏠")

# --- MEMORIA TEMPORANEA (DATABASE) ---
# Questo serve a "ricordare" i dati finché la finestra è aperta
if 'clienti' not in st.session_state:
    st.session_state['clienti'] = ["Cliente Esempio"] # Un cliente di prova
if 'preventivi_salvati' not in st.session_state:
    st.session_state['preventivi_salvati'] = []

# --- MENU LATERALE (Il tuo disegno del menu) ---
st.sidebar.title("Navigazione")
scelta = st.sidebar.radio(
    "Vai a:",
    ["🏠 Home / Calcola", "👥 Clienti", "📂 Archivio Preventivi"]
)

# =======================================================
# PAGINA 1: CALCOLA E POSA (La calcolatrice)
# =======================================================
if scelta == "🏠 Home / Calcola":
    st.title("🧱 Calcola Preventivo")
    
    # Seleziona per quale cliente è il lavoro
    cliente_selezionato = st.selectbox("Seleziona Cliente:", st.session_state['clienti'])
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Misure")
        lunghezza = st.number_input("Lunghezza (m)", 0.0, step=0.1)
        larghezza = st.number_input("Larghezza (m)", 0.0, step=0.1)
        sfrido_perc = st.slider("Sfrido (%)", 0, 20, 10)

    with col2:
        st.subheader("2. Costi")
        costo_piastrelle = st.number_input("Costo Piastrelle (€/mq)", 0.0, step=0.5)
        costo_manodopera = st.number_input("Manodopera (€/mq)", 0.0, step=0.5)
        costo_extra = st.number_input("Colla/Extra (€)", 0.0, step=10.0)

    if st.button("CALCOLA E SALVA 💾"):
        if lunghezza > 0 and larghezza > 0:
            mq_reali = lunghezza * larghezza
            mq_acquisto = mq_reali + (mq_reali * (sfrido_perc / 100))
            totale = (mq_acquisto * costo_piastrelle) + (mq_reali * costo_manodopera) + costo_extra
            
            st.success(f"Preventivo Calcolato: € {totale:.2f}")
            
            # Salviamo il preventivo nella memoria
            nuovo_preventivo = {
                "data": datetime.datetime.now().strftime("%d/%m/%Y"),
                "cliente": cliente_selezionato,
                "totale": totale,
                "mq": mq_reali
            }
            st.session_state['preventivi_salvati'].append(nuovo_preventivo)
            st.info("Preventivo salvato nell'archivio!")
        else:
            st.error("Inserisci le misure!")

# =======================================================
# PAGINA 2: CLIENTI (Il tuo disegno della lista clienti)
# =======================================================
elif scelta == "👥 Clienti":
    st.title("Gestione Clienti")
    
    # Modulo per aggiungere un nuovo cliente
    with st.form("nuovo_cliente"):
        nuovo_nome = st.text_input("Nome e Cognome nuovo cliente")
        bottone_aggiungi = st.form_submit_button("AGGIUNGI CLIENTE ➕")
        
        if bottone_aggiungi and nuovo_nome:
            st.session_state['clienti'].append(nuovo_nome)
            st.success(f"Cliente {nuovo_nome} aggiunto!")
            st.rerun() # Ricarica la pagina per aggiornare la lista

    st.markdown("---")
    st.subheader("Lista Clienti")
    
    # Mostriamo la lista dei clienti
    for cliente in st.session_state['clienti']:
        st.write(f"👤 {cliente}")

# =======================================================
# PAGINA 3: PREVENTIVI (Il tuo disegno dell'archivio)
# =======================================================
elif scelta == "📂 Archivio Preventivi":
    st.title("Preventivi Salvati")
    
    if len(st.session_state['preventivi_salvati']) == 0:
        st.write("Nessun preventivo salvato ancora.")
    else:
        # Tabella riassuntiva
        for prev in st.session_state['preventivi_salvati']:
            with st.expander(f"📄 {prev['cliente']} - € {prev['totale']:.2f} ({prev['data']})"):
                st.write(f"Data: {prev['data']}")
                st.write(f"Cliente: {prev['cliente']}")
                st.write(f"Metri Quadri: {prev['mq']} mq")
                st.write(f"**TOTALE: € {prev['totale']:.2f}**")
