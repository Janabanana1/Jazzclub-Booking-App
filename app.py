import streamlit as st
import pandas as pd
import openpyxl

# WICHTIG: Diese Zeile MUSS ganz oben stehen!
st.set_page_config(page_title="Jazzclub Booking Tool", layout="wide")

# Datei-Pfad zur Excel-Datei (Passe diesen ggf. an)
EXCEL_FILE = "Jazzclub_Booking_Tool_Optimized.xlsx"

# Lade die Excel-Datei
@st.cache_data
def load_excel():
    return pd.read_excel(EXCEL_FILE, sheet_name=None)

# Speichert die Daten zurück in die Excel-Datei
def save_to_excel(data):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

# Lade alle Tabellen aus der Excel-Datei
data = load_excel()

# Titel
st.title("🎷 Jazzclub Booking Tool")

# Menü-Optionen
menu = ["📅 Buchungsübersicht", "🎤 Künstler & Bands", "💰 Finanzen", "➕ Neue Buchung"]
choice = st.sidebar.radio("Menü", menu)

# --- 📅 BUCHUNGSÜBERSICHT ---
if choice == "📅 Buchungsübersicht":
    st.subheader("📅 Buchungsübersicht")

    df_booking = data["Booking-Kalender"]

    # Dropdown-Filter
    genre_filter = st.selectbox("🎼 Genre filtern:", ["Alle"] + df_booking["Genre"].dropna().unique().tolist())
    status_filter = st.selectbox("📌 Status filtern:", ["Alle", "Bestätigt", "Angefragt", "Abgesagt"])

    # Filter anwenden
    if genre_filter != "Alle":
        df_booking = df_booking[df_booking["Genre"] == genre_filter]
    if status_filter != "Alle":
        df_booking = df_booking[df_booking["Status"] == status_filter]

    st.dataframe(df_booking, height=400, use_container_width=True)

# --- 🎤 KÜNSTLER & BANDS ---
elif choice == "🎤 Künstler & Bands":
    st.subheader("🎤 Künstler & Bands")

    df_artists = data["Bands-Künstler"]
    st.dataframe(df_artists, height=400, use_container_width=True)

# --- 💰 FINANZEN ---
elif choice == "💰 Finanzen":
    st.subheader("💰 Finanzübersicht")

    df_finances = data["Verträge & Gagen"]

    # Berechnungen
    df_finances["Einnahmen aus Tickets"] = df_finances["Einnahmen aus Tickets"].replace("€", "", regex=True).astype(float)
    df_finances["Kosten (Hotel, Technik)"] = df_finances["Kosten (Hotel, Technik)"].replace("€", "", regex=True).astype(float)
    df_finances["Gage"] = df_finances["Gage"].replace("€", "", regex=True).astype(float)

    df_finances["Gewinn/Verlust"] = df_finances["Einnahmen aus Tickets"] - df_finances["Gage"] - df_finances["Kosten (Hotel, Technik)"]

    st.dataframe(df_finances, height=400, use_container_width=True)

# --- ➕ NEUE BUCHUNG ---
elif choice == "➕ Neue Buchung":
    st.subheader("➕ Neue Buchung hinzufügen")

    with st.form("add_booking"):
        col1, col2 = st.columns(2)

        with col1:
            datum = st.date_input("📅 Datum")
            band = st.text_input("🎤 Band/Künstler")
            genre = st.text_input("🎼 Genre")
            gage = st.number_input("💰 Gage (€)", min_value=0, step=50)

        with col2:
            status = st.selectbox("📌 Status", ["Bestätigt", "Angefragt", "Abgesagt"])
            ticketpreis = st.number_input("🎟️ Ticketpreis (€)", min_value=0, step=5)
            erwartete_besucher = st.number_input("👥 Erwartete Besucher", min_value=0, step=10)
            vertrag = st.selectbox("📜 Vertrag vorhanden?", ["Ja", "Nein"])

        submit = st.form_submit_button("✅ Buchung hinzufügen")

    if submit:
        new_entry = {
            "Datum": datum.strftime("%d.%m.%Y"),
            "Wochentag": datum.strftime("%A"),
            "Band/Künstler": band,
            "Genre": genre,
            "Status": status,
            "Gage": f"{gage} €",
            "Ticketpreis": f"{ticketpreis} €",
            "Erwartete Besucher": erwartete_besucher,
            "Ansprechpartner Band": "",
            "Vertrag vorhanden?": vertrag
        }

        # Füge die neue Buchung hinzu
        df_booking = data["Booking-Kalender"]
        df_booking = pd.concat([df_booking, pd.DataFrame([new_entry])], ignore_index=True)
        data["Booking-Kalender"] = df_booking

        # Speichere die Daten
        save_to_excel(data)

        st.success(f"✅ Buchung für {band} wurde hinzugefügt!")
