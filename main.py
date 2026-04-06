import os
import json
from notebook.ocr import extraire_texte_et_preuve
from notebook.llm import structurer_avec_llm

# --- CONFIGURATION DES CHEMINS ---
DOSSIER_ENTREE = "data/image_entree"
DOSSIER_SORTIE = "data/sortie"

def traiter_documents():
    # 1. Vérifier si le dossier d'entrée existe
    if not os.path.exists(DOSSIER_ENTREE):
        os.makedirs(DOSSIER_ENTREE)
        print(f"INFO : Dossier '{DOSSIER_ENTREE}' créé. Dépose tes images dedans.")
        return

    # 2. Lister les fichiers (images ou PDF)
    fichiers = [f for f in os.listdir(DOSSIER_ENTREE) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))]

    if not fichiers:
        print("ERREUR : Aucun fichier trouvé dans 'data/image_entrée'.")
        return

    # Pour cet exemple, on traite le premier fichier trouvé
    nom_fichier = fichiers[0]
    chemin_complet = os.path.join(DOSSIER_ENTREE, nom_fichier)
    
    print(f"--- ANALYSE DE : {nom_fichier} ---")

    try:
        # Étape 1 : OCR (Local avec docTR)
        texte_brut = extraire_texte_et_preuve(chemin_complet)
        print("✓ OCR terminé.")

        # Étape 2 : Intelligence (Cloud avec Groq)
        print("✓ Structuration via Groq en cours...")
        resultat_json = structurer_avec_llm(texte_brut)

        # Étape 3 : Sauvegarde
        if not os.path.exists(DOSSIER_SORTIE):
            os.makedirs(DOSSIER_SORTIE)

        nom_sortie = f"{os.path.splitext(nom_fichier)[0]}_structure.json"
        chemin_sortie = os.path.join(DOSSIER_SORTIE, nom_sortie)

        with open(chemin_sortie, "w", encoding="utf-8") as f:
            json.dump(resultat_json, f, ensure_ascii=False, indent=4)

        print(f"--- SUCCÈS : Résultat dans {chemin_sortie} ---")
        print(json.dumps(resultat_json, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"ERREUR lors du traitement : {e}")

if __name__ == "__main__":
    traiter_documents()