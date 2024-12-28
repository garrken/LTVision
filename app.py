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

# Information om nödvändiga kolumner
st.header("Steg 1: Ladda upp dina data")
st.subheader("Obligatoriska kolumner")
st.markdown("""
- **Kunddata (obligatorisk):**
  - `UUID`: Kundens unika identifierare.
  - `timestamp_registration`: Tidpunkt för registrering (format: datetime).
- **Händelsedata (valfri):**
  - `UUID`: Kundens unika identifierare.
  - `timestamp_event`: Tidpunkt för händelsen (format: datetime).
  - `event_name`: Typ av händelse.
  - `purchase_value`: Värde av köp (numerisk).
""")

# Ladda upp data
uploaded_customers = st.file_uploader("Ladda upp kunddata (obligatorisk, CSV)", type=["csv"], key="customers")
uploaded_events = st.file_uploader("Ladda upp händelsedata (valfri, CSV)", type=["csv"], key="events")

# Kontrollera om kunddata är uppladdad
if uploaded_customers:
    customers = pd.read_csv(uploaded_customers)
    st.write("Förhandsgranskning av kunddata:")
    st.write(customers.head())

    # Kontrollera om nödvändiga kolumner finns i kunddata
    required_customer_columns = ["UUID", "timestamp_registration"]
    if all(col in customers.columns for col in required_customer_columns):
        st.success("Kunddata är korrekt uppladdad!")
    else:
        st.error(f"Kunddata saknar en eller flera av följande kolumner: {', '.join(required_customer_columns)}")
        st.stop()

# Kontrollera om händelsedata är uppladdad
events = None
if uploaded_events:
    events = pd.read_csv(uploaded_events)
    st.write("Förhandsgranskning av händelsedata:")
    st.write(events.head())

    # Kontrollera om nödvändiga kolumner finns i händelsedata
    required_event_columns = ["UUID", "timestamp_event", "event_name", "purchase_value"]
    if all(col in events.columns for col in required_event_columns):
        st.success("Händelsedata är korrekt uppladdad!")
    else:
        st.warning(f"Händelsedata saknar en eller flera av följande kolumner: {', '.join(required_event_columns)}")

# Knapp för att gå vidare
if st.button("Fortsätt till analys"):
    if uploaded_customers:
        st.header("Steg 2: Generera analys och visualiseringar")

        # Skapa LTVexploratory-objekt
        ltv = LTVexploratory(
            data_customers=customers,
            data_events=events,
            uuid_col="UUID",
            registration_time_col="timestamp_registration",
            event_time_col="timestamp_event" if events is not None else None,
            event_name_col="event_name" if events is not None else None,
            value_col="purchase_value" if events is not None else None,
        )

        # Generera analys
        st.subheader("Sammanfattning av data")
        ltv.summary()

        # Visualisering: Fördelning av köp
        st.subheader("Köpdistribution")
        days_limit = st.slider("Välj tidsfönster (dagar)", min_value=30, max_value=365, value=90)
        if events is not None:
            fig, _ = ltv.plot_purchases_distribution(days_limit=days_limit)
            st.pyplot(fig)
        else:
            st.info("Händelsedata krävs för att generera köpdistribution.")

        # Visualisering: Paretoplot
        st.subheader("Revenue Pareto")
        if events is not None:
            pareto_fig, _ = ltv.plot_revenue_pareto(days_limit=days_limit)
            st.pyplot(pareto_fig)
        else:
            st.info("Händelsedata krävs för att generera Pareto-plot.")
    else:
        st.error("Kunddata är obligatorisk för att gå vidare.")
