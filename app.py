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

# Ladda upp två CSV-filer: en för kunder och en för events
st.header("Steg 1: Ladda upp dina data")
uploaded_customers = st.file_uploader("Ladda upp kunddata (CSV)", type=["csv"], key="customers")
uploaded_events = st.file_uploader("Ladda upp händelsedata (CSV)", type=["csv"], key="events")

if uploaded_customers and uploaded_events:
    # Läs in data
    customers = pd.read_csv(uploaded_customers)
    events = pd.read_csv(uploaded_events)
    
    st.write("Förhandsgranskning av kunddata:")
    st.write(customers.head())
    st.write("Förhandsgranskning av händelsedata:")
    st.write(events.head())

    # Kontrollera om nödvändiga kolumner finns
    required_customer_columns = ["UUID", "timestamp_registration"]
    required_event_columns = ["UUID", "timestamp_event", "event_name", "purchase_value"]

    if all(col in customers.columns for col in required_customer_columns) and all(col in events.columns for col in required_event_columns):
        st.success("Alla nödvändiga kolumner finns!")

        # Skapa LTVexploratory-objekt
        ltv = LTVexploratory(
            data_customers=customers,
            data_events=events,
            uuid_col="UUID",
            registration_time_col="timestamp_registration",
            event_time_col="timestamp_event",
            event_name_col="event_name",
            value_col="purchase_value",
        )

        # Generera analys och visualiseringar
        st.header("Steg 2: Generera analys och visualiseringar")

        # Sammanfattning av data
        st.subheader("Sammanfattning av data")
        ltv.summary()

        # Visualisering: Fördelning av köp
        st.subheader("Köpdistribution")
        days_limit = st.slider("Välj tidsfönster (dagar)", min_value=30, max_value=365, value=90)
        fig, _ = ltv.plot_purchases_distribution(days_limit=days_limit)
        st.pyplot(fig)

        # Visualisering: Paretoplot
        st.subheader("Revenue Pareto")
        pareto_fig, _ = ltv.plot_revenue_pareto(days_limit=days_limit)
        st.pyplot(pareto_fig)
    else:
        st.error("Datafilerna saknar en eller flera nödvändiga kolumner.")
else:
    st.info("Ladda upp både kunddata och händelsedata för att börja.")
