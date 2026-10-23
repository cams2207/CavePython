import json
import os
import io
from datetime import datetime
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session

app = Flask(__name__)
app.secret_key = "cave-secret-key-wow"

DATA_FILE = "data_cave.csv"
LOCATIONS_FILE = "locations.json"
HISTORY_FILE = "history_bu.json"
REGIONS_FILE = "regions.json"
DOMAINES_FILE = "domaines.json"

ENABLE_AUTH = False
CREDENTIALS = {"admin": "cave2026"}

DEFAULT_REGIONS = [
    "Bordeaux", "Bourgogne", "Vallée du Rhône", "Alsace", 
    "Champagne", "Loire", "Beaujolais", "Languedoc-Roussillon", "Provence", "Sud-Ouest"
]

DEFAULT_DOMAINES = [
    "Domaine Leflaive", "Château Margaux", "Domaine Guigal", "Château Lynch-Bages",
    "Domaine Dujac", "Château Chalon", "Maison Trimbach", "Domaine Tempier"
]

DEFAULT_LOCATIONS = ["Reste chez Fred", "Reste Appart", "Reste St Yorre"]

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def load_locations():
    return load_json(LOCATIONS_FILE, DEFAULT_LOCATIONS)

def load_regions():
    return load_json(REGIONS_FILE, DEFAULT_REGIONS)

def load_domaines():
    return load_json(DOMAINES_FILE, DEFAULT_DOMAINES)

def load_history():
    return load_json(HISTORY_FILE, [])

def init_files():
    if not os.path.exists(LOCATIONS_FILE):
        save_json(LOCATIONS_FILE, DEFAULT_LOCATIONS)
    if not os.path.exists(REGIONS_FILE):
        save_json(REGIONS_FILE, DEFAULT_REGIONS)
    if not os.path.exists(DOMAINES_FILE):
        save_json(DOMAINES_FILE, DEFAULT_DOMAINES)
    if not os.path.exists(HISTORY_FILE):
        save_json(HISTORY_FILE, [])
    if not os.path.exists(DATA_FILE):
        locs = load_locations()
        columns = ["id", "Date", "Région", "Domaine", "Vin", "Millesime", "Boire Min", "Boire Max", "PU", "Statut"] + locs
        sample_data = [
            {
                "id": 1, "Date": "2023-05-10", "Région": "Bordeaux", "Domaine": "Château Lynch-Bages", 
                "Vin": "Pauillac Grand Cru Classé", "Millesime": 2015, "Boire Min": 2022, "Boire Max": 2035, 
                "PU": "120€", "Statut": "Garde", "Reste chez Fred": 2, "Reste Appart": 1, "Reste St Yorre": 0
            },
            {
                "id": 2, "Date": "2024-01-15", "Région": "Bourgogne", "Domaine": "Domaine Dujac", 
                "Vin": "Morey-Saint-Denis", "Millesime": 2018, "Boire Min": 2023, "Boire Max": 2030, 
                "PU": "85€", "Statut": "A boire", "Reste chez Fred": 0, "Reste Appart": 2, "Reste St Yorre": 1
            },
            {
                "id": 3, "Date": "2023-11-20", "Région": "Vallée du Rhône", "Domaine": "Domaine Guigal", 
                "Vin": "Côte-Rôtie Château d'Ampuis", "Millesime": 2017, "Boire Min": 2024, "Boire Max": 2038, 
                "PU": "110€", "Statut": "Apogée", "Reste chez Fred": 3, "Reste Appart": 0, "Reste St Yorre": 2
            }
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(DATA_FILE, index=False)

def load_data():
    init_files()
    locations = load_locations()
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if "id" not in df.columns:
            df.insert(0, "id", range(1, len(df) + 1))
        for loc in locations:
            if loc not in df.columns:
                df[loc] = 0.0
        return df
    return pd.DataFrame()

@app.before_request
def check_auth():
    if not ENABLE_AUTH:
        return
    if request.endpoint in ['login', 'static'] or session.get('user_logged_in'):
        return
    return redirect(url_for('login'))

@app.route('/')
def index():
    df = load_data()
    locations = load_locations()
    
    loc_cols = [c for c in locations if c in df.columns]
    df_locs = df[loc_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    total_bouteilles = int(df_locs.values.sum())
    total_references = len(df)
    
    stock_loc = df_locs.sum().to_dict()
    stock_reg = {}
    if "Région" in df.columns:
        df_reg = df.copy()
        df_reg["Total_Qte"] = df_locs.sum(axis=1)
        stock_reg = df_reg.groupby("Région")["Total_Qte"].sum().to_dict()

    history = load_history()
    recent_bu = history[-4:][::-1]

    return render_template('index.html', 
                           total_bouteilles=total_bouteilles, 
                           total_references=total_references,
                           stock_loc=stock_loc,
                           stock_reg=stock_reg,
                           recent_bu=recent_bu,
                           active_tab='dashboard')

@app.route('/stock')
def stock():
    df = load_data()
    locations = load_locations()
    query = request.args.get('q', '').strip().lower()
    selected_region = request.args.get('region', '').strip()
    selected_statut = request.args.get('statut', '').strip()

    wines = df.to_dict(orient='records')
    
    # Global search and filter
    filtered_wines = []
    for w in wines:
        loc_sum = sum(float(w.get(l, 0) or 0) for l in locations)
        w['total_qty'] = int(loc_sum)
        
        match_query = True
        if query:
            searchable_text = f"{w.get('Région','')} {w.get('Domaine','')} {w.get('Vin','')} {w.get('Millesime','')} {w.get('Statut','')}".lower()
            match_query = query in searchable_text
            
        match_region = True
        if selected_region:
            match_region = (w.get('Région') == selected_region)

        match_statut = True
        if selected_statut:
            match_statut = (w.get('Statut') == selected_statut)

        if match_query and match_region and match_statut:
            filtered_wines.append(w)

    regions = load_regions()
    return render_template('stock.html', 
                           wines=filtered_wines, 
                           locations=locations, 
                           regions=regions,
                           query=query, 
                           selected_region=selected_region,
                           selected_statut=selected_statut,
                           active_tab='stock')

@app.route('/edit_wine/<int:wine_id>', methods=['GET', 'POST'])
def edit_wine(wine_id):
    df = load_data()
    locations = load_locations()
    regions = load_regions()
    domaines = load_domaines()

    wine_row = df[df['id'] == wine_id]
    if wine_row.empty:
        flash("Vin introuvable.", "error")
        return redirect(url_for('stock'))

    idx = wine_row.index[0]

    if request.method == 'POST':
        df.loc[idx, 'Région'] = request.form.get('region', '')
        df.loc[idx, 'Domaine'] = request.form.get('domaine', '')
        df.loc[idx, 'Vin'] = request.form.get('vin', '')
        df.loc[idx, 'Millesime'] = request.form.get('millesime', 2020)
        df.loc[idx, 'Boire Min'] = request.form.get('boire_min', 2024)
        df.loc[idx, 'Boire Max'] = request.form.get('boire_max', 2030)
        df.loc[idx, 'PU'] = request.form.get('pu', '')
        df.loc[idx, 'Statut'] = request.form.get('statut', 'A boire')

        for loc in locations:
            try:
                df.loc[idx, loc] = float(request.form.get(f"qty_{loc}", 0))
            except ValueError:
                df.loc[idx, loc] = 0.0

        df.to_csv(DATA_FILE, index=False)
        flash("Les modifications de la fiche ont été enregistrées !", "success")
        return redirect(url_for('stock'))

    wine_data = wine_row.iloc[0].to_dict()
    return render_template('edit.html', wine=wine_data, locations=locations, regions=regions, domaines=domaines, active_tab='stock')

@app.route('/delete_wine/<int:wine_id>', methods=['POST'])
def delete_wine(wine_id):
    df = load_data()
    df = df[df['id'] != wine_id]
    df.to_csv(DATA_FILE, index=False)
    flash("Fiche de vin supprimée avec succès.", "success")
    return redirect(url_for('stock'))

@app.route('/mark_bu', methods=['POST'])
def mark_bu():
    wine_id = request.form.get("wine_id")
    loc = request.form.get("location")
    rating = request.form.get("rating", "4")
    note = request.form.get("note", "")
    date_bu = request.form.get("date_bu", datetime.now().strftime("%Y-%m-%d"))

    df = load_data()
    wine_row = df[df['id'].astype(str) == str(wine_id)]

    if not wine_row.empty:
        idx = wine_row.index[0]
        current_qty = float(df.loc[idx, loc]) if loc in df.columns else 0
        
        if current_qty > 0:
            df.loc[idx, loc] = current_qty - 1
            df.to_csv(DATA_FILE, index=False)

            history = load_history()
            history_entry = {
                "id": len(history) + 1,
                "date": date_bu,
                "domaine": wine_row.iloc[0].get("Domaine", ""),
                "vin": wine_row.iloc[0].get("Vin", ""),
                "millesime": int(wine_row.iloc[0].get("Millesime", 0)),
                "region": wine_row.iloc[0].get("Région", ""),
                "location": loc,
                "rating": int(rating),
                "note": note
            }
            history.append(history_entry)
            save_json(HISTORY_FILE, history)
            flash(f"🎉 1 bouteille consommée ({loc}) ! Fiche mise à jour & ajoutée au carnet.", "success")
        else:
            flash(f"Aucune bouteille disponible dans l'emplacement {loc}.", "error")
            
    return redirect(url_for('stock'))

@app.route('/history')
def history():
    history_data = load_history()[::-1]
    return render_template('history.html', history=history_data, active_tab='history')

@app.route('/add', methods=['GET', 'POST'])
def add_wine():
    locations = load_locations()
    regions = load_regions()
    domaines = load_domaines()

    if request.method == 'POST':
        df = load_data()
        
        region = request.form.get("region", "")
        domaine = request.form.get("domaine", "")

        if region and region not in regions:
            regions.append(region)
            save_json(REGIONS_FILE, sorted(regions))
        if domaine and domaine not in domaines:
            domaines.append(domaine)
            save_json(DOMAINES_FILE, sorted(domaines))

        new_id = int(df["id"].max() + 1) if not df.empty and "id" in df.columns else 1
        new_row = {
            "id": new_id,
            "Date": request.form.get("date", datetime.now().strftime("%Y-%m-%d")),
            "Région": region,
            "Domaine": domaine,
            "Vin": request.form.get("vin", ""),
            "Millesime": request.form.get("millesime", 2020),
            "Boire Min": request.form.get("boire_min", 2024),
            "Boire Max": request.form.get("boire_max", 2030),
            "PU": request.form.get("pu", ""),
            "Statut": request.form.get("statut", "A boire")
        }
        for loc in locations:
            new_row[loc] = float(request.form.get(f"qty_{loc}", 0))
            
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        flash("Nouveau vin ajouté avec succès !", "success")
        return redirect(url_for('stock'))
        
    return render_template('add.html', locations=locations, regions=regions, domaines=domaines, active_tab='add')

@app.route('/import_export', methods=['GET', 'POST'])
def import_export():
    locations = load_locations()
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith(('.xlsx', '.xls')):
            try:
                xls = pd.ExcelFile(file)
                sheet_name = 'Cave' if 'Cave' in xls.sheet_names else xls.sheet_names[0]
                imported_df = pd.read_excel(xls, sheet_name=sheet_name)
                
                if "id" not in imported_df.columns:
                    imported_df.insert(0, "id", range(1, len(imported_df) + 1))
                    
                for loc in locations:
                    if loc not in imported_df.columns:
                        imported_df[loc] = 0.0
                        
                imported_df.to_csv(DATA_FILE, index=False)
                flash(f"Importation réussie depuis l'onglet '{sheet_name}' !", "success")
            except Exception as e:
                flash(f"Erreur lors de la lecture du fichier : {e}", "error")
    return render_template('import_export.html', active_tab='import')

@app.route('/export_excel')
def export_excel():
    df = load_data()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Cave', index=False)
    output.seek(0)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="Cave.xlsx"
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    locations = load_locations()
    regions = load_regions()
    domaines = load_domaines()

    if request.method == 'POST':
        action = request.form.get("action")

        if action == "update_locations":
            new_locs = [l.strip() for l in request.form.getlist('locations') if l.strip()]
            df = load_data()
            for old_l, new_l in zip(locations, new_locs):
                if old_l != new_l and old_l in df.columns:
                    df = df.rename(columns={old_l: new_l})
            save_json(LOCATIONS_FILE, new_locs)
            df.to_csv(DATA_FILE, index=False)
            flash("Emplacements mis à jour !", "success")

        elif action == "add_region":
            new_reg = request.form.get("new_region", "").strip()
            if new_reg and new_reg not in regions:
                regions.append(new_reg)
                save_json(REGIONS_FILE, sorted(regions))
                flash(f"Région '{new_reg}' ajoutée !", "success")

        elif action == "add_domaine":
            new_dom = request.form.get("new_domaine", "").strip()
            if new_dom and new_dom not in domaines:
                domaines.append(new_dom)
                save_json(DOMAINES_FILE, sorted(domaines))
                flash(f"Domaine '{new_dom}' ajouté !", "success")

        elif action == "delete_region":
            reg_to_del = request.form.get("region_name")
            if reg_to_del in regions:
                regions.remove(reg_to_del)
                save_json(REGIONS_FILE, regions)
                flash(f"Région '{reg_to_del}' supprimée !", "success")

        elif action == "delete_domaine":
            dom_to_del = request.form.get("domaine_name")
            if dom_to_del in domaines:
                domaines.remove(dom_to_del)
                save_json(DOMAINES_FILE, domaines)
                flash(f"Domaine '{dom_to_del}' supprimé !", "success")

        return redirect(url_for('settings'))

    return render_template('settings.html', locations=locations, regions=regions, domaines=domaines, active_tab='settings')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)
