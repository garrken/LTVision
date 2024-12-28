import streamlit as st
import pandas as pd
import sys
import os

# Dynamiskt lägg till "src" i Python-sökvägen
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Importera LTVModel från ltvision
from ltvision import LTVModel

# Titel och introduktion
st.title("LTVision Streamlit App")
st.write("Analysera kundens livstidsvärde (LTV) med hjälp av LTVision.")

# Ladda upp en CSV-fil
st.header("Steg 1: Ladda upp din data")
uploaded_file = st.file_uploader("Ladda upp en CSV-fil", type=["csv"])

if uploaded_file:
    # Läs in data
    data = pd.read_csv(uploaded_file)
    st.write("Förhandsgranskning av data:")
    st.write(data.head())

    # Kontrollera att nödvändiga kolumner finns
    required_columns = ["customer_id", "transaction_date", "transaction_amount"]
    if all(col in data.columns for col in required_columns):
        st.success("Datan innehåller alla nödvändiga kolumner!")

        # Träna modellen
        st.header("Steg 2: Träna LTV-modellen")
        model = LTVModel(
            customer_id_col="customer_id",
            transaction_date_col="transaction_date",
            transaction_amount_col="transaction_amount",
        )
        model.fit(data)
        st.write("Modellen är tränad!")

        # Generera prediktioner
        st.header("Steg 3: Generera prediktioner")
        predictions = model.predict(data)
        st.write("Predikterat livstidsvärde (LTV):")
        st.write(predictions)

        # Ladda ner resultat
        st.download_button(
            label="Ladda ner prediktioner som CSV",
            data=predictions.to_csv(index=False),
            file_name="ltv_predictions.csv",
            mime="text/csv",
        )
    else:
        st.error(
            f"Datan saknar en eller flera av följande kolumner: {', '.join(required_columns)}"
        )
