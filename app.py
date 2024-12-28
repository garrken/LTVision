import streamlit as st
import pandas as pd
import sys
import os

# Dynamiskt lägg till "src" i Python-sökvägen
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Importera LTVexploratory från exploratory.py
from exploratory import LTVexploratory

# Titel och introduktion
st.title("LTVision Streamlit App")
st.write("Analysera kundens livstidsvärde (LTV) med hjälp av LTVexploratory.")

# Information om obligatoriska och valfria kolumner
st.header("Steg 1: Ladda upp din data")
st.subheader("Kolumner i filen:")
st.markdown("""
- **Obligatoriska:**
  - `UUID`: Kundens unika identifierare.
  - `timestamp_registration`: Tidpunkt för registrering (datetime).
- **Valfria:**
  - `timestamp_event`: Tidpunkt för händelse (datetime).
  - `event_name`: Typ av händelse.
  - `purchase_value`: Värde av köp (numerisk).
""")

# Ladda upp CSV-fil
uploaded_file = st.file_uploader("Ladda upp en CSV-fil", type=["csv"])

if uploaded_file:
    # Läs in data
    data = pd.read_csv(uploaded_file)
    st.write("Förhandsgranskning av data:")
    st.write(data.head())

    # Visa kolumnnamn för felsökning
    st.write("Kolumner i datasetet:", data.columns.tolist())

    # Kontrollera om obligatoriska kolumner finns
    mandatory_columns = ["UUID", "timestamp_registration"]
    optional_columns = ["timestamp_event", "event_name", "purchase_value"]

    # Kontrollera obligatoriska kolumner
    missing_required = [col for col in mandatory_columns if col not in data.columns]
    if missing_required:
        st.error(f"Följande obligatoriska kolumner saknas: {', '.join(missing_required)}")
        st.stop()

    st.success("Alla obligatoriska kolumner finns!")
    missing_optional = [col for col in optional_columns if col not in data.columns]
    if missing_optional:
        st.warning(f"Följande valfria kolumner saknas: {', '.join(missing_optional)}")

    # Konvertera UUID till sträng
    data["UUID"] = data["UUID"].astype(str)

    # Konvertera timestamp_registration till datetime
    data["timestamp_registration"] = pd.to_datetime(data["timestamp_registration"], errors="coerce")
    if data["timestamp_registration"].isnull().any():
        st.error("Kolumnen `timestamp_registration` innehåller ogiltiga värden som inte kunde konverteras till datetime.")
        st.stop()

    # Konvertera timestamp_event till datetime (om den finns)
    if "timestamp_event" in data.columns:
        data["timestamp_event"] = pd.to_datetime(data["timestamp_event"], errors="coerce")
        if data["timestamp_event"].isnull().any():
            st.warning("Kolumnen `timestamp_event` innehåller ogiltiga värden som inte kunde konverteras till datetime.")

    # Knapp för att gå vidare
    if st.button("Fortsätt till analys"):
        st.header("Steg 2: Generera analys och visualiseringar")

        # Hantera valfria kolumner
        event_time_col = "timestamp_event" if "timestamp_event" in data.columns else None
        event_name_col = "event_name" if "event_name" in data.columns else None
        value_col = "purchase_value" if "purchase_value" in data.columns else None

        # Skapa LTVexploratory-objekt
        try:
            ltv = LTVexploratory(
                data_customers=data,
                data_events=data,  # Händelser är samma dataset
                uuid_col="UUID",
                registration_time_col="timestamp_registration",
                event_time_col=event_time_col,
                event_name_col=event_name_col,
                value_col=value_col,
            )
        except KeyError as e:
            st.error(f"Ett fel uppstod vid hantering av kolumner: {e}")
            st.stop()

        # Generera analys
        st.subheader("Sammanfattning av data")
        try:
            ltv.summary()
        except Exception as e:
            st.error(f"Ett fel uppstod vid generering av sammanfattning: {e}")

        # Visualisering: Fördelning av köp
        st.subheader("Köpdistribution")
        days_limit = st.slider("Välj tidsfönster (dagar)", min_value=30, max_value=365, value=90)
        if event_time_col:
            try:
                fig, _ = ltv.plot_purchases_distribution(days_limit=days_limit)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Ett fel uppstod vid generering av köpdistribution: {e}")
        else:
            st.info("Händelsedata krävs för att generera köpdistribution.")

        # Visualisering: Paretoplot
        st.subheader("Revenue Pareto")
        if value_col:
            try:
                pareto_fig, _ = ltv.plot_revenue_pareto(days_limit=days_limit)
                st.pyplot(pareto_fig)
            except Exception as e:
                st.error(f"Ett fel uppstod vid generering av Pareto-plot: {e}")
        else:
            st.info("Köpvärden krävs för att generera Pareto-plot.")
else:
    st.info("Ladda upp en CSV-fil för att börja.")
