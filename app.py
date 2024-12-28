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

    # Ta bort extra mellanslag i kolumnnamn
    data.columns = data.columns.str.strip()
    st.write("Kolumner efter att ha tagit bort mellanslag:", data.columns.tolist())

    # Kontrollera obligatoriska kolumner
    mandatory_columns = ["UUID", "timestamp_registration"]
    if not all(col in data.columns for col in mandatory_columns):
        st.error(f"Saknar obligatoriska kolumner: {', '.join([col for col in mandatory_columns if col not in data.columns])}")
        st.stop()

    # Lägg till valfria kolumner om de saknas
    required_columns = ["timestamp_registration", "timestamp_event", "event_name", "purchase_value"]
    for col in required_columns:
        if col not in data.columns:
            if col == "timestamp_registration":
                data[col] = pd.NaT
            elif col in ["timestamp_event", "purchase_value"]:
                data[col] = 0.0
            elif col == "event_name":
                data[col] = None
            st.warning(f"Kolumnen `{col}` saknades och har lagts till som en placeholder.")

    # Formattera kolumner
    try:
        # UUID: sträng
        data["UUID"] = data["UUID"].astype(str)
        st.success("Kolumnen `UUID` har konverterats till sträng.")

        # timestamp_registration: datetime
        data["timestamp_registration"] = pd.to_datetime(data["timestamp_registration"], errors="coerce")
        if data["timestamp_registration"].isnull().any():
            st.error("Ogiltiga värden i kolumnen `timestamp_registration`. Kontrollera filen.")
            st.stop()
        st.success("Kolumnen `timestamp_registration` har konverterats till datetime.")

        # timestamp_event: datetime
        if "timestamp_event" in data.columns:
            data["timestamp_event"] = pd.to_datetime(data["timestamp_event"], errors="coerce")
            if data["timestamp_event"].isnull().any():
                st.warning("Ogiltiga värden i kolumnen `timestamp_event` har ersatts med NaT.")
            st.success("Kolumnen `timestamp_event` har konverterats till datetime.")

        # event_name: sträng
        if "event_name" in data.columns:
            data["event_name"] = data["event_name"].astype(str)
            st.success("Kolumnen `event_name` har konverterats till sträng.")

        # purchase_value: numerisk
        if "purchase_value" in data.columns:
            data["purchase_value"] = pd.to_numeric(data["purchase_value"], errors="coerce")
            if data["purchase_value"].isnull().any():
                st.warning("Ogiltiga värden i kolumnen `purchase_value` har ersatts med 0.")
            data["purchase_value"] = data["purchase_value"].fillna(0)
            st.success("Kolumnen `purchase_value` har konverterats till numerisk.")

    except Exception as e:
        st.error(f"Ett fel uppstod vid formattering av kolumner: {e}")
        st.stop()

    # Kontrollera att alla kolumner finns och logga datatyper
    st.write("Kolumner och datatyper efter bearbetning:", data.dtypes)

    # Logga data som skickas till LTVexploratory
    st.write("Data som skickas till LTVexploratory:", data.head())

    # Knapp för att gå vidare
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
        except KeyError as e:
            st.error(f"Ett fel uppstod vid hantering av kolumner: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Ett oväntat fel inträffade: {e}")
            st.stop()

        # Generera analys
        st.subheader("Sammanfattning av data")
        try:
            ltv.summary()
        except Exception as e:
            st.error(f"Ett fel uppstod vid generering av sammanfattning: {e}")
else:
    st.info("Ladda upp en CSV-fil för att börja.")
