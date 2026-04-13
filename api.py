import os
import shutil
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
# Importation de tes modules
from notebook.ocr import extraire_texte_et_preuve
from notebook.llm import structurer_avec_llm

# 1. Initialisation
app = FastAPI(
    title="Eburni-Kan API",
    description="Extraction IA de CNI Ivoirienne - Projet ESATIC",
    version="2.2.0"
)

# 2. Configuration des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "image_entree")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sortie")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/", tags=["Système"])
async def root():
    return {"message": "Serveur Eburni-Kan en ligne", "statut": "Prêt"}

@app.post("/extract-cni", tags=["Intelligence Artificielle"])
async def extract_cni(file: UploadFile = File(...)):
    
    # ÉTAPE 1 : Validation du format

    formats_acceptes = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in formats_acceptes:
        raise HTTPException(status_code=400, detail="Format non supporté.")
    

    # ÉTAPE 2 : Nettoyage du nom de fichier (CRUCIAL pour Windows)
    # On remplace tout ce qui n'est pas lettre/chiffre par un underscore

    nom_propre = re.sub(r'[^a-zA-Z0-9.]', '_', file.filename)
    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, nom_propre))
    
    try:
        # Rembobinage du curseur
        await file.seek(0)
        
        # Écriture forcée sur le disque
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            buffer.flush()
            os.fsync(buffer.fileno()) # On s'assure que le fichier est réellement écrit

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture : {e}")

    # ÉTAPE 3 : Pipeline IA
    
    try:
        # On passe le chemin nettoyé à l'OCR
        texte_brut = extraire_texte_et_preuve(file_path, OUTPUT_DIR)
        
        # Structuration LLM
        donnees_json = structurer_avec_llm(texte_brut)

        # ÉTAPE 4 : Vérification
        if not donnees_json.get("nom") and not donnees_json.get("nni"):
            return {
                "statut": "attention",
                "message": "Aucune donnée d'identité détectée.",
                "texte_extrait": texte_brut,
                "analyse_partielle": donnees_json
            }

        # ÉTAPE 5 : Succès
        return {
            "statut": "succès",
            "fichier_original": file.filename,
            "fichier_traite": nom_propre,
            "donnees": donnees_json,
            "preuve": f"verif_page_0_{nom_propre}.png" 
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")