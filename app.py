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

# Steg 1: Ladda upp data
st.header("Steg 1: Ladda upp din data")
uploaded_file = st.file_uploader("Ladda upp en CSV-fil", type=["csv"])

if uploaded_file:
    # Läs in data
    data = pd.read_csv(uploaded_file)
    st.write("Kolumner direkt från filen:", data.columns.tolist())

    # Hantera datatyper manuellt
    try:
        # UUID som sträng
        if "UUID" in data.columns:
            data["UUID"] = data["UUID"].astype(str)

        # timestamp_registration som datetime
        if "timestamp_registration" in data.columns:
            data["timestamp_registration"] = pd.to_datetime(data["timestamp_registration"], errors="coerce")
            if data["timestamp_registration"].isnull().any():
                st.warning("Ogiltiga värden i `timestamp_registration` har ersatts med NaT.")

        # timestamp_event som datetime
        if "timestamp_event" in data.columns:
            data["timestamp_event"] = pd.to_datetime(data["timestamp_event"], errors="coerce")
            if data["timestamp_event"].isnull().any():
                st.warning("Ogiltiga värden i `timestamp_event` har ersatts med NaT.")

        # event_name som sträng
        if "event_name" in data.columns:
            data["event_name"] = data["event_name"].astype(str)

        # purchase_value som numerisk
        if "purchase_value" in data.columns:
            data["purchase_value"] = pd.to_numeric(data["purchase_value"], errors="coerce").fillna(0)

        st.success("Datan har formatterats framgångsrikt.")
    except Exception as e:
        st.error(f"Fel vid hantering av datatyper: {e}")
        st.stop()

    # Förhandsgranska bearbetad data
    st.write("Kolumner och datatyper efter konvertering:")
    st.write(data.dtypes)
    st.write("Förhandsgranskning av data:")
    st.write(data.head())

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
