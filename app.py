import streamlit as st

st.set_page_config(page_title="Preventivo Piastrellista", page_icon="🏠")

st.title("🏠 Calcolatore Preventivi")
st.write("Inserisci le misure e i costi per generare un preventivo rapido.")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("1. Misure")
    lunghezza = st.number_input("Lunghezza stanza (m)", min_value=0.0, step=0.1)
    larghezza = st.number_input("Larghezza stanza (m)", min_value=0.0, step=0.1)
    sfrido_perc = st.slider("Sfrido (%)", min_value=0, max_value=20, value=10)

with col2:
    st.header("2. Costi")
    costo_piastrelle = st.number_input("Costo Piastrelle (€/mq)", min_value=0.0, step=0.5)
    costo_manodopera = st.number_input("Costo Manodopera (€/mq)", min_value=0.0, step=0.5)
    costo_colla = st.number_input("Costo Colla/Stucco (forfait €)", min_value=0.0, step=10.0)

if st.button("CALCOLA PREVENTIVO 🚀"):
    if lunghezza > 0 and larghezza > 0:
        mq_reali = lunghezza * larghezza
        mq_acquisto = mq_reali + (mq_reali * (sfrido_perc / 100))
        totale_materiale = (mq_acquisto * costo_piastrelle) + costo_colla
        totale_manodopera = mq_reali * costo_manodopera
        totale_finale = totale_materiale + totale_manodopera
        
        st.markdown("---")
        st.success(f"Totale Preventivo: € {totale_finale:.2f}")
        st.write(f"📏 Superficie Reale: {mq_reali:.2f} mq")
        st.write(f"📦 Da Acquistare: {mq_acquisto:.2f} mq")
    else:
        st.error("Inserisci le misure!")
