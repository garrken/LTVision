import streamlit as st
import pandas as pd
from ltvision import LTVModel

st.title("LTVision Streamlit App")
st.write("Analysera kundens livstidsvärde (LTV) med hjälp av LTVision.")

# Ladda upp fil
uploaded_file = st.file_uploader("Ladda upp en CSV-fil med transaktionsdata", type=["csv"])

if uploaded_file:
    # Läs in datan
    data = pd.read_csv(uploaded_file)
    st.write("Förhandsvisning av data:")
    st.write(data.head())

    # Kontrollera att nödvändiga kolumner finns
    required_columns = ["customer_id", "transaction_date", "transaction_amount"]
    if all(col in data.columns for col in required_columns):
        st.success("Datan är korrekt!")
        
        # Träna modellen
        model = LTVModel(
            customer_id_col="customer_id",
            transaction_date_col="transaction_date",
            transaction_amount_col="transaction_amount"
        )
        model.fit(data)
        st.write("Modellen är tränad!")
        
        # Prediktioner
        predictions = model.predict(data)
        st.write("Predikterade livstidsvärden:")
        st.write(predictions)
        
        # Ladda ner resultat
        st.download_button(
            label="Ladda ner resultat",
            data=predictions.to_csv(index=False),
            file_name="ltv_predictions.csv",
            mime="text/csv"
        )
    else:
        st.error(f"Datan saknar nödvändiga kolumner: {', '.join(required_columns)}")
