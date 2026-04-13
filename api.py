import os
import shutil
import re
import torch
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException

# Importation de tes modules
from notebook.ocr import extraire_texte_et_preuve
from notebook.llm import structurer_avec_llm

# --- GESTION DU CYCLE DE VIE (LIFESPAN) ---
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Charge les modèles lourds une seule fois au démarrage du serveur.
    """
    print("⏳ Initialisation du pipeline IA (Eburni-Kan)...")
    
    # Configuration forcée pour docTR/PyTorch
    os.environ['USE_TF'] = '0'
    os.environ['USE_TORCH'] = '1'
    
    from doctr.models import ocr_predictor
    
    try:
        # Chargement du prédicteur
        predictor = ocr_predictor(pretrained=True)
        
        # Transfert sur GPU si disponible
        if torch.cuda.is_available():
            predictor.cuda()
            print("✅ GPU Tesla T4 activé pour l'OCR.")
        else:
            print("⚠️ GPU non détecté, utilisation du CPU.")
            
        models["ocr"] = predictor
        print("🚀 Pipeline prêt à l'emploi !")
        
    except Exception as e:
        print(f"❌ Erreur critique au chargement des modèles : {e}")
        raise e

    yield
    # Nettoyage à la fermeture
    models.clear()
    print("🛑 Serveur arrêté et mémoire libérée.")

# --- INITIALISATION DE L'APP ---
app = FastAPI(
    title="Eburni-Kan API",
    description="Extraction IA de CNI Ivoirienne - Projet ESATIC",
    version="2.2.0",
    lifespan=lifespan
)

# Configuration des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "image_entree")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sortie")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/", tags=["Système"])
async def root():
    return {
        "projet": "Eburni-Kan", 
        "statut": "En ligne", 
        "device": "GPU" if torch.cuda.is_available() else "CPU"
    }

@app.post("/extract-cni", tags=["Intelligence Artificielle"])
async def extract_cni(file: UploadFile = File(...)):
    
    # 1. Validation du format
    formats_acceptes = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in formats_acceptes:
        raise HTTPException(status_code=400, detail="Format non supporté (JPG, PNG, PDF uniquement).")

    # 2. Nettoyage et enregistrement sécurisé
    nom_propre = re.sub(r'[^a-zA-Z0-9.]', '_', file.filename)
    file_path = os.path.join(UPLOAD_DIR, nom_propre)
    
    try:
        await file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture disque : {e}")

    # 3. Pipeline IA
    try:
        # Note : Pense à modifier ta fonction extraire_texte_et_preuve dans ocr.py
        # pour qu'elle accepte l'argument 'model' au lieu de le recréer.
        texte_brut = extraire_texte_et_preuve(file_path, OUTPUT_DIR, model=models["ocr"])
        
        # Structuration par LLM
        donnees_json = structurer_avec_llm(texte_brut)

        # 4. Vérification des résultats
        if not donnees_json.get("nom") and not donnees_json.get("nni"):
            return {
                "statut": "attention",
                "message": "Données incomplètes. La qualité de l'image est peut-être insuffisante.",
                "donnees_extraites": donnees_json
            }

        # 5. Réponse finale
        return {
            "statut": "succès",
            "donnees": donnees_json,
            "fichiers": {
                "original": file.filename,
                "preuve_ocr": f"verif_page_0_{nom_propre}.png"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement IA : {str(e)}")