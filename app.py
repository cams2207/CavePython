import json
import os
import io
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session

app = Flask(__name__)
app.secret_key = "cave-secret-key"

DATA_FILE = "data_cave.csv"
LOCATIONS_FILE = "locations.json"

# AUTHENTIFICATION ACTIVABLE / DÉSACTIVABLE POUR LES TESTS
ENABLE_AUTH = False  # Mettez True pour réactiver l'authentification
CREDENTIALS = {"admin": "cave2026"}

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

def load_data():
    locations = load_locations()
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for loc in locations:
            if loc not in df.columns:
                df[loc] = 0.0
        return df
    else:
        columns = ["Date", "Région", "Domaine", "Vin", "Millesime", "Quantité", "Boire Min", "Boire Max", "PU", "Statut"] + locations
        return pd.DataFrame(columns=columns)

@app.before_request
def check_auth():
    if not ENABLE_AUTH:
        return
    if request.endpoint in ['login', 'static'] or session.get('user_logged_in'):
        return
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in CREDENTIALS and CREDENTIALS[username] == password:
            session['user_logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash("Identifiant ou mot de passe incorrect", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
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

    return render_template('index.html', 
                           total_bouteilles=total_bouteilles, 
                           total_references=total_references,
                           stock_loc=stock_loc,
                           stock_reg=stock_reg,
                           active_tab='dashboard')

@app.route('/stock')
def stock():
    df = load_data()
    locations = load_locations()
    wines = df.to_dict(orient='records')
    return render_template('stock.html', wines=wines, locations=locations, active_tab='stock')

@app.route('/update_stock', methods=['POST'])
def update_stock():
    df = load_data()
    locations = load_locations()
    
    for idx in range(len(df)):
        for loc in locations:
            val = request.form.get(f"loc_{idx}_{loc}")
            if val is not None:
                try:
                    df.loc[idx, loc] = float(val)
                except ValueError:
                    pass
                
    df.to_csv(DATA_FILE, index=False)
    flash("Stock mis à jour avec succès !", "success")
    return redirect(url_for('stock'))

@app.route('/add', methods=['GET', 'POST'])
def add_wine():
    locations = load_locations()
    if request.method == 'POST':
        df = load_data()
        new_row = {
            "Date": request.form.get("date", ""),
            "Région": request.form.get("region", ""),
            "Domaine": request.form.get("domaine", ""),
            "Vin": request.form.get("vin", ""),
            "Millesime": request.form.get("millesime", 2020),
            "Boire Min": request.form.get("boire_min", 2024),
            "Boire Max": request.form.get("boire_max", 2030),
            "PU": request.form.get("pu", ""),
            "Statut": ""
        }
        for loc in locations:
            new_row[loc] = float(request.form.get(f"qty_{loc}", 0))
            
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        flash("Vin ajouté avec succès !", "success")
        return redirect(url_for('stock'))
        
    return render_template('add.html', locations=locations, active_tab='add')

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
                for loc in locations:
                    if loc not in imported_df.columns:
                        imported_df[loc] = 0.0
                imported_df.to_csv(DATA_FILE, index=False)
                flash(f"Import réussi depuis l'onglet '{sheet_name}' !", "success")
            except Exception as e:
                flash(f"Erreur d'import : {e}", "error")
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
    if request.method == 'POST':
        new_locs = request.form.getlist('locations')
        df = load_data()
        for old_l, new_l in zip(locations, new_locs):
            if old_l != new_l and old_l in df.columns:
                df = df.rename(columns={old_l: new_l})
        save_locations(new_locs)
        df.to_csv(DATA_FILE, index=False)
        flash("Emplacements mis à jour !", "success")
        return redirect(url_for('settings'))
    return render_template('settings.html', locations=locations, active_tab='settings')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)
