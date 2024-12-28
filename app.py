# Kontrollera kolumnnamn
st.write("Kolumner i datasetet:", data.columns.tolist())

# Validera obligatoriska och valfria kolumner
required_columns = ["UUID", "timestamp_registration"]
optional_columns = ["timestamp_event", "event_name", "purchase_value"]

missing_required = [col for col in required_columns if col not in data.columns]
if missing_required:
    st.error(f"Obligatoriska kolumner saknas: {', '.join(missing_required)}")
    st.stop()

st.write("Valfria kolumner som hittades:", [col for col in optional_columns if col in data.columns])
