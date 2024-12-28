import streamlit as st
import pandas as pd
import sys
import os

# Dynamiskt lägg till "src" i Python-sökvägen
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Importera LTVexploratory från exploratory.py
from exploratory import LTVexploratory

# Funktion för att säkerställa kompatibilitet
def ensure_compatible_dataframe(data):
    """
    Säkerställ att alla kolumner i DataFrame är kompatibla med Streamlit och Arrow.
    """
    for col in data.columns:
        if data[col].dtype == 'O':  # dtype 'O' betyder object
            try:
                data[col] = data[col].astype(str).fillna("")
                st.warning(f"Kolumnen `{col}` konverterades till sträng.")
            except Exception as e:
                st.error(f"Misslyckades med att konvertera `{col}` till sträng: {e}")
        elif pd.api.types.is_numeric_dtype(data[col]) and data[col].isnull().any():
            data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
            st.warning(f"Numeriska nullvärden i `{col}` ersattes med 0.")
        elif pd.api.types.is_datetime64_any_dtype(data[col]) and data[col].isnull().any():
            data[col] = pd.to_datetime(data[col], errors="coerce").fillna(pd.Timestamp("1970-01-01"))
            st.warning(f"Nullvärden i `{col}` ersattes med '1970-01-01'.")
    return data

# Titel och introduktion
st.title("LTVision Streamlit App")
st.write("Analysera kundens livstidsvärde (LTV) med hjälp av LTVexploratory.")

# Steg 1: Ladda upp data
st.header("Steg 1: Ladda upp din data")
uploaded_file = st.file_uploader("Ladda upp en CSV-fil", type=["csv"])

if uploaded_file:
    # Läs in data
    data = pd.read_csv(uploaded_file)
    st.write("Kolumner direkt från filen:", data.columns.tolist())

    # Kontrollera och säkerställ kompatibilitet
    try:
        data = ensure_compatible_dataframe(data)
        st.success("Datan är kompatibel med Streamlit och Arrow!")
    except Exception as e:
        st.error(f"Misslyckades med att säkerställa kompatibilitet: {e}")
        st.stop()

    # Förhandsgranska bearbetad data
    st.write("Kolumner och datatyper efter konvertering:")
    st.write(data.info())  # Logga alla datatyper
    st.write(data.head())  # Visa första raderna av datan

    # Knapp för att fortsätta till analys
    if st.button("Fortsätt till analys"):
        st.header("Steg 2: Generera analys och visualiseringar")

        # Skapa LTVexploratory-objekt
        try:
            ltv = LTVexploratory(
                data_customers=data,
                data_events=data,
                uuid_col="UUID",
                registration_time_col="timestamp_registration",
                event_time_col="timestamp_event",
                event_name_col="event_name",
                value_col="purchase_value",
            )
            st.success("LTVexploratory har initierats framgångsrikt.")
        except KeyError as e:
            st.error(f"Ett fel uppstod vid hantering av kolumner: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Ett oväntat fel inträffade vid initiering: {e}")
            st.stop()

        # Generera analys
        st.subheader("Sammanfattning av data")
        try:
            ltv.summary()
        except Exception as e:
            st.error(f"Ett fel uppstod vid generering av sammanfattning: {e}")
else:
    st.info("Ladda upp en CSV-fil för att börja.")
