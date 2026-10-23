import io
import json
import os
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Gestion de Cave à Vin",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DESIGN & CSS "VRAIE APPLICATION" ---
st.markdown(
    """
    <style>
    /* Masquer le menu Streamlit et le footer par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Style global de l'application */
    .main {
        background-color: #f4f6f8;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* En-têtes de page */
    h1, h2, h3 {
        color: #4A0E17;
        font-weight: 700;
    }

    /* Cartes de statistiques / métriques */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #7D1242;
        margin-bottom: 15px;
    }

    /* Boutons personnalisés */
    .stButton>button {
        background-color: #7D1242;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #5A0D30;
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    /* Style de la sidebar */
    section[data-testid="stSidebar"] {
        background-color: #2C0B14;
        color: white;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: white !important;
        font-size: 16px;
        padding: 5px 0;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] span {
        color: #E6C280 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "data_cave.csv"
LOCATIONS_FILE = "locations.json"
CREDENTIALS = {"admin": "cave2026"}  # Identifiants modifiables ici

# --- AUTHENTIFICATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown(
        "<br><br><h1 style='text-align: center; color: #4A0E17;'>🍷 Ma Cave à Vin</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #666; font-size: 18px;'>Espace de gestion sécurisé</p><br>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Identifiant", placeholder="Entrez votre ID")
            password = st.text_input(
                "Mot de passe", type="password", placeholder="••••••••"
            )
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
            if submitted:
                if (
                    username in CREDENTIALS
                    and CREDENTIALS[username] == password
                ):
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
            "Date",
            "Région",
            "Domaine",
            "Vin",
            "Millesime",
            "Quantité",
            "Boire Min",
            "Boire Max",
            "PU",
            "Statut",
        ] + locations
        return pd.DataFrame(columns=columns)


df = load_data()

# --- BARRE LATÉRALE DE NAVIGATION (DESIGN APP) ---
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #E6C280;'>🍾 Mon Chai</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Tableau de bord",
        "📥 Gestion du Stock",
        "➕ Ajouter / Importer",
        "⚙️ Paramètres",
    ],
)

st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
if st.sidebar.button("🔓 Déconnexion", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()


# --- 1. TABLEAU DE BORD & STATS ---
if menu == "📊 Tableau de bord":
    st.title("📊 Tableau de Bord")
    st.write("Indicateurs clés et synthèse de votre cave.")

    loc_cols = [c for c in locations if c in df.columns]
    df_locs = df[loc_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    total_bouteilles = int(df_locs.values.sum())
    total_references = len(df)

    # Cartes métriques épurées
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin:0; color:#555; font-size:16px;">Références de Vins</h3>
                <p style="margin:5px 0 0 0; font-size:32px; font-weight:bold; color:#7D1242;">{total_references}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin:0; color:#555; font-size:16px;">Total Bouteilles en Stock</h3>
                <p style="margin:5px 0 0 0; font-size:32px; font-weight:bold; color:#7D1242;">{total_bouteilles}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📍 Stock par Emplacement")
        loc_totals = df_locs.sum()
        if not loc_totals.empty and loc_totals.sum() > 0:
            st.bar_chart(loc_totals)
        else:
            st.info("Aucune donnée d'emplacement.")

    with col_b:
        st.subheader("🌍 Stock par Région")
        if "Région" in df.columns and not df["Région"].isna().all():
            df_reg = df.copy()
            df_reg["Total_Qte"] = df_locs.sum(axis=1)
            reg_totals = df_reg.groupby("Région")["Total_Qte"].sum()
            st.bar_chart(reg_totals)
        else:
            st.info("Aucune donnée de région.")

    st.markdown("---")
    st.subheader("📅 Stock par Millésime")
    if "Millesime" in df.columns and not df["Millesime"].isna().all():
        df_mill = df.copy()
        df_mill["Total_Qte"] = df_locs.sum(axis=1)
        mill_totals = df_mill.groupby("Millesime")["Total_Qte"].sum()
        st.line_chart(mill_totals)
    else:
        st.info("Aucune donnée de millésime.")


# --- 2. GESTION DE LA CAVE ---
elif menu == "📥 Gestion du Stock":
    st.title("📥 Gestion du Stock & Dégustations")
    st.write(
        "Modifiez vos stocks directement dans le tableau (pour marquer comme bu ou ajuster les quantités), puis enregistrez."
    )

    edited_df = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, height=520
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("💾 Enregistrer", use_container_width=True):
            edited_df.to_csv(DATA_FILE, index=False)
            st.success("Modifications enregistrées avec succès !")

    st.markdown("---")
    st.subheader("📤 Export des données")
    st.write("Téléchargez votre cave au format Excel (.xlsx).")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        edited_df.to_excel(writer, sheet_name="Cave", index=False)
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Télécharger le fichier Excel",
        data=excel_data,
        file_name="Cave.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# --- 3. AJOUTER / IMPORTER ---
elif menu == "➕ Ajouter / Importer":
    st.title("➕ Ajout et Import de Données")
    tab1, tab2 = st.tabs(["➕ Ajout Unitaire", "📥 Import Fichier Excel"])

    with tab1:
        with st.form("add_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                region = st.text_input("Région")
                domaine = st.text_input("Domaine")
                vin = st.text_input("Nom du Vin")
            with col2:
                millesime = st.number_input(
                    "Millésime", min_value=1900, max_value=2030, value=2020
                )
                boire_min = st.number_input(
                    "Boire Min", min_value=1900, max_value=2050, value=2024
                )
                boire_max = st.number_input(
                    "Boire Max", min_value=1900, max_value=2050, value=2030
                )
            with col3:
                pu = st.text_input("Prix Unitaire (PU)")
                date_ajout = st.text_input("Date d'achat")

            st.markdown("### 📍 Répartition par emplacement")
            loc_inputs = {}
            cols = (
                st.columns(len(locations))
                if len(locations) > 0
                else [st.container()]
            )
            for i, loc in enumerate(locations):
                with cols[i % len(cols)]:
                    loc_inputs[loc] = st.number_input(
                        loc, min_value=0.0, value=0.0, step=1.0
                    )

            submitted = st.form_submit_button("Ajouter à la cave")
            if submitted:
                new_row = {
                    "Date": date_ajout,
                    "Région": region,
                    "Domaine": domaine,
                    "Vin": vin,
                    "Millesime": millesime,
                    "Boire Min": boire_min,
                    "Boire Max": boire_max,
                    "PU": pu,
                    "Statut": "",
                }
                new_row.update(loc_inputs)
                new_df = pd.concat(
                    [df, pd.DataFrame([new_row])], ignore_index=True
                )
                new_df.to_csv(DATA_FILE, index=False)
                st.success("Bouteille ajoutée avec succès !")

    with tab2:
        st.write(
            "Importez votre fichier Excel (`.xlsx`). L'application ciblera automatiquement l'onglet **Cave**."
        )
        uploaded_excel = st.file_uploader(
            "Sélectionner le fichier Excel", type=["xlsx", "xls"]
        )
        if uploaded_excel is not None:
            try:
                xls = pd.ExcelFile(uploaded_excel)
                sheet_to_load = (
                    "Cave" if "Cave" in xls.sheet_names else xls.sheet_names[0]
                )
                imported_df = pd.read_excel(xls, sheet_name=sheet_to_load)

                st.success(
                    f"Fichier chargé (onglet sélectionné : '{sheet_to_load}')"
                )
                st.dataframe(imported_df.head(), use_container_width=True)

                if st.button("Valider et remplacer le stock actuel"):
                    for loc in locations:
                        if loc not in imported_df.columns:
                            imported_df[loc] = 0.0
                    imported_df.to_csv(DATA_FILE, index=False)
                    st.success("Import réussi ! Le stock a été mis à jour.")
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier Excel : {e}")


# --- 4. PARAMÈTRES & EMPLACEMENTS ---
elif menu == "⚙️ Paramètres":
    st.title("⚙️ Paramètres des Emplacements")
    st.write(
        "Personnalisez les noms de vos caves ou ajoutez de nouveaux emplacements de stockage."
    )

    new_locs = []
    for i, loc in enumerate(locations):
        updated_name = st.text_input(
            f"Emplacement {i+1}", value=loc, key=f"loc_{i}"
        )
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
