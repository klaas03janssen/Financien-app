import streamlit as st
import pandas as pd

# Instellingen voor de webpagina
st.set_page_config(page_title="Mijn Financiën", page_icon="💰", layout="wide")

st.title("Mijn Financiële Overzicht 📱")

# --- DEEL 1: BESTAND KIEZEN ---
# Hier kun je straks op je mobiel gewoon je CSV uploaden!
uploaded_file = st.file_uploader("Upload je CSV bestand", type=['csv'])

if uploaded_file is not None:
    # --- DEEL 2: LOGICA (Jouw Code) ---
    try:
        MIJN_SPAARREKENING = "NL33RABO3633840621" 
        
        df = pd.read_csv(uploaded_file, sep=',', encoding='ISO-8859-1')
        
        kolommen = ['Datum', 'Bedrag', 'Naam tegenpartij', 'Tegenrekening IBAN/BBAN', 'Omschrijving-1']
        df = df[kolommen]
        df['Bedrag'] = df['Bedrag'].astype(str).str.replace(',', '.')
        df['Bedrag'] = pd.to_numeric(df['Bedrag'])
        df['Datum'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d')

        def label_transactie(rij):
            omschrijving = str(rij['Omschrijving-1']).lower()
            naam = str(rij['Naam tegenpartij']).lower()
            tegenrekening = str(rij['Tegenrekening IBAN/BBAN']) 
            bedrag = rij['Bedrag']

            if bedrag > 0 and 'alliander' in naam:
                return 'Salaris (Alliander)'
            
            if MIJN_SPAARREKENING in tegenrekening: 
                return 'Intern sparen'
            elif 'degiro' in naam or 'flatex' in naam:
                return 'Beleggen'

            elif 'alliander' in naam or 'essent' in naam or 'vattenfall' in naam:
                return 'Vaste Lasten (Huis)'
            elif 'simple' in naam or 'simpel' in naam:
                return 'Telefoon Abonnement'
            elif 'zilveren kruis' in naam:
                return 'Zorgverzekering'
            elif 'belastingdienst' in naam:
                return 'Belastingdienst'

            elif 'albert heijn' in naam or 'plus' in naam or 'jumbo' in naam or 'lidl' in naam or 'intermarche' in naam:
                return 'Boodschappen'
            elif 'action' in naam or 'bol' in naam or 'intratuin' in naam:
                return 'Benodigdheden'

            elif 'ov-chipkaart' in naam or 'esso' in naam or 'total' in naam or 'arial' in naam:
                return 'Vervoer'

            elif 'zalando' in naam or 'gymshark' in naam or 'h&m' in naam or 'abyl' in naam or 'mango' in naam or 'foot locker' in naam or 'klarna' in naam:
                return 'Kleding'
            elif 'hotel' in naam or 'cafe' in naam or 'grandcafe' in naam or 'palladium' in naam:
                return 'Uitgaan/Vrije tijd'

            elif bedrag > 0 and 'intern' not in naam:
                return 'Overige Inkomsten'
            else:
                return 'Categorie overig'

        df['Categorie'] = df.apply(label_transactie, axis=1)

        # --- DEEL 3: BEREKENINGEN ---
        salaris = df[df['Categorie'] == 'Salaris (Alliander)']['Bedrag'].sum()
        overig_inkomen = df[df['Categorie'] == 'Overige Inkomsten']['Bedrag'].sum()
        totaal_binnen = salaris + overig_inkomen
        
        sparen_flow = df[df['Categorie'] == 'Intern sparen']['Bedrag'].sum()
        netto_spaar_resultaat = sparen_flow * -1
        
        beleggen = df[df['Categorie'] == 'Beleggen']['Bedrag'].sum()

        niet_meerekenen = ['Salaris (Alliander)', 'Overige Inkomsten', 'Intern sparen', 'Beleggen', 'Inkomen']
        masker_echte_uitgaven = ~df['Categorie'].isin(niet_meerekenen)
        totaal_echte_uitgaven = df[masker_echte_uitgaven]['Bedrag'].sum()

        # --- DEEL 4: HET DASHBOARD TONEN ---
        
        st.header("📊 Maand Overzicht")

        # Kolommen voor de metrics (Ziet eruit als blokken op je scherm)
        col1, col2, col3 = st.columns(3)
        col1.metric("Inkomen", f"€ {totaal_binnen:,.2f}")
        col2.metric("Echte Uitgaven", f"€ {abs(totaal_echte_uitgaven):,.2f}", delta_color="inverse")
        col3.metric("Spaarpot Groei", f"€ {netto_spaar_resultaat:,.2f}", delta=f"{netto_spaar_resultaat:,.2f}")

        st.divider()

        col4, col5 = st.columns(2)
        col4.metric("Naar Beleggen", f"€ {abs(beleggen):,.2f}")
        col5.metric("Salaris deel", f"€ {salaris:,.2f}")

        st.header("💸 Waar gaat het geld heen?")
        
        # Data klaarmaken voor de grafiek
        chart_data = df[masker_echte_uitgaven].groupby('Categorie')['Bedrag'].sum().abs().sort_values(ascending=False)
        
        # De grafiek tekenen
        st.bar_chart(chart_data)

        # De tabel tonen (optioneel, kan je uitklappen)
        with st.expander("Bekijk alle transacties"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Er ging iets mis bij het inladen: {e}")

else:
    st.info("Upload een CSV bestand om te beginnen.")