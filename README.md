# Application de Gestion de Cave à Vin 🍷

Application légère sous Streamlit pour gérer sa cave à vin sur Google Cloud Platform (VM Debian).

## Installation rapide sur la VM Debian GCP :

```bash
# 1. Cloner le projet
git clone https://github.com/cams2207/CavePython.git
cd CavePython

# 2. Configurer l'environnement Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```
