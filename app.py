import os
import json
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Gestion de Cave à Vin",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "data_cave.csv"
LOCATIONS_FILE = "locations.json"
CREDENTIALS = {"admin": "cave2026"}  # Vous pourrez modifier le mot de passe ici

# --- AUTHENTIFICATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center;'>🍷 Connexion à votre Cave</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
    st.stop()

# --- GESTION DES LOCALISATIONS & DONNÉES ---
def load_locations():
    default_locs = ["Reste chez Fred", "Reste Appart", "Reste St Yorre"]
    if os.path.exists(LOCATIONS_FILE):
        try:
            with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_locs
    return default_locs

def save_locations(locs):
    with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(locs, f, ensure_ascii=False, indent=2)

locations = load_locations()

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for loc in locations:
            if loc not in df.columns:
                df[loc] = 0.0
        return df
    else:
        columns = [
            "Date", "Région", "Domaine", "Vin", "Millesime",
            "Quantité", "Boire Min", "Boire Max", "PU", "Statut"
        ] + locations
        return pd.DataFrame(columns=columns)

df = load_data()

# --- NAVIGATION ---
st.sidebar.title("🍾 Ma Cave à Vin")
menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Tableau de bord & Stats",
        "📥 Gestion de la Cave",
        "➕ Ajouter / Importer",
        "⚙️ Paramètres & Emplacements",
    ],
)

if st.sidebar.button("Déconnexion"):
    st.session_state["authenticated"] = False
    st.rerun()

# --- 1. TABLEAU DE BORD & STATS ---
if menu == "📊 Tableau de bord & Stats":
    st.title("📊 Tableau de Bord et Statistiques")

    # Calcul des quantités
    loc_cols = [c for c in locations if c in df.columns]
    df_locs = df[loc_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    total_bouteilles = df_locs.values.sum()
    total_references = len(df)

    col1, col2 = st.columns(2)
    col1.metric("Références de vins", total_references)
    col2.metric("Total des bouteilles en stock", int(total_bouteilles))

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📍 Stock par Emplacement (Cave)")
        loc_totals = df_locs.sum()
        st.bar_chart(loc_totals)

    with col_b:
        st.subheader("🌍 Stock par Région")
        if "Région" in df.columns:
            df_reg = df.copy()
            df_reg["Total_Qte"] = df_locs.sum(axis=1)
            reg_totals = df_reg.groupby("Région")["Total_Qte"].sum()
            st.bar_chart(reg_totals)
        else:
            st.info("Aucune donnée de région.")

    st.markdown("---")
    st.subheader("📅 Stock par Millésime")
    if "Millesime" in df.columns:
        df_mill = df.copy()
        df_mill["Total_Qte"] = df_locs.sum(axis=1)
        mill_totals = df_mill.groupby("Millesime")["Total_Qte"].sum()
        st.line_chart(mill_totals)

# --- 2. GESTION DE LA CAVE ---
elif menu == "📥 Gestion de la Cave":
    st.title("📥 Consultation, Modification et Dégustation")
    st.write("Modifiez le tableau ci-dessous en direct puis sauvegardez.")

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Enregistrer les modifications"):
        edited_df.to_csv(DATA_FILE, index=False)
        st.success("Modifications enregistrées avec succès !")

    st.markdown("---")
    st.subheader("📤 Export de la cave")
    st.download_button(
        label="Télécharger la cave (CSV)",
        data=edited_df.to_csv(index=False).encode("utf-8"),
        file_name="export_cave.csv",
        mime="text/csv",
    )

# --- 3. AJOUTER / IMPORTER ---
elif menu == "➕ Ajouter / Importer":
    st.title("➕ Ajouter un vin ou Importer votre fichier")
    tab1, tab2 = st.tabs(["Ajout unitaire", "Importer un fichier CSV"])

    with tab1:
        with st.form("add_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                region = st.text_input("Région")
                domaine = st.text_input("Domaine")
                vin = st.text_input("Nom du Vin")
            with col2:
                millesime = st.number_input("Millésime", min_value=1900, max_value=2030, value=2020)
                boire_min = st.number_input("Boire Min", min_value=1900, max_value=2050, value=2024)
                boire_max = st.number_input("Boire Max", min_value=1900, max_value=2050, value=2030)
            with col3:
                pu = st.text_input("Prix Unitaire (PU)")
                date_ajout = st.text_input("Date d'achat")

            st.markdown("### Répartition par emplacement")
            loc_inputs = {}
            cols = st.columns(len(locations)) if len(locations) > 0 else [st.container()]
            for i, loc in enumerate(locations):
                with cols[i % len(cols)]:
                    loc_inputs[loc] = st.number_input(loc, min_value=0.0, value=0.0, step=1.0)

            submitted = st.form_submit_button("Ajouter à la cave")
            if submitted:
                new_row = {
                    "Date": date_ajout, "Région": region, "Domaine": domaine,
                    "Vin": vin, "Millesime": millesime, "Boire Min": boire_min,
                    "Boire Max": boire_max, "PU": pu, "Statut": ""
                }
                new_row.update(loc_inputs)
                new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                new_df.to_csv(DATA_FILE, index=False)
                st.success("Bouteille ajoutée avec succès ! Rafraîchissez la page.")

    with tab2:
        st.write("Importez votre fichier CSV (au format exact de l'onglet Cave).")
        uploaded_file = st.file_uploader("Choisissez votre fichier CSV", type=["csv"])
        if uploaded_file is not None:
            imported_df = pd.read_csv(uploaded_file)
            st.write("Aperçu :", imported_df.head())
            if st.button("Valider et remplacer la cave actuelle"):
                imported_df.to_csv(DATA_FILE, index=False)
                st.success("Import réussi ! Le stock a été mis à jour.")

# --- 4. PARAMÈTRES & EMPLACEMENTS ---
elif menu == "⚙️ Paramètres & Emplacements":
    st.title("⚙️ Gestion des Emplacements")
    st.write("Renommez ou ajoutez vos emplacements de stockage.")

    new_locs = []
    for i, loc in enumerate(locations):
        updated_name = st.text_input(f"Emplacement {i+1}", value=loc, key=f"loc_{i}")
        if updated_name:
            new_locs.append(updated_name)

    add_new = st.text_input("➕ Ajouter un nouvel emplacement")
    if add_new and add_new not in new_locs:
        new_locs.append(add_new)

    if st.button("Mettre à jour les emplacements"):
        for old_l, new_l in zip(locations, new_locs):
            if old_l != new_l and old_l in df.columns:
                df = df.rename(columns={old_l: new_l})
        locations = new_locs
        save_locations(locations)
        df.to_csv(DATA_FILE, index=False)
        st.success("Emplacements mis à jour avec succès !")
        st.rerun()
