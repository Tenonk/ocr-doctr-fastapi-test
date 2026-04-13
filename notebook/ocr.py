import os
import matplotlib.pyplot as plt
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.utils.visualization import visualize_page
from PIL import Image
import torch

# On ne force plus .cpu() ici globalement pour laisser l'API décider
def extraire_texte_et_preuve(chemin_fichier, dossier_sortie, model=None):
    """
    OCR robuste : Gère les PDF, les photos et les captures d'écran.
    Accepte un modèle déjà chargé pour éviter les fuites de mémoire.
    """
    try:
        # 1. Gestion du modèle (Singleton pattern)
        if model is None:
            # Cas de secours pour les tests unitaires
            model = ocr_predictor(pretrained=True)
            if torch.cuda.is_available():
                model.cuda()
            else:
                model.cpu()

        extension = os.path.splitext(chemin_fichier)[1].lower()
        
        # 2. Pré-traitement de l'image
        if extension == ".pdf":
            doc = DocumentFile.from_pdf(chemin_fichier)
        else:
            # Sécurité Alpha/RGBA : Vital pour les captures d'écran Android/iOS
            with Image.open(chemin_fichier) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    img.save(chemin_fichier) 
            
            doc = DocumentFile.from_images(chemin_fichier)

        # 3. Analyse OCR (utilise le modèle passé en argument)
        result = model(doc)

        # 4. Extraction et génération des preuves
        texte_brut_complet = ""
        nom_base = os.path.basename(chemin_fichier)

        for page_idx, page in enumerate(result.pages):
            # --- SAUVEGARDE DE LA PREUVE VISUELLE ---
            page_dict = page.export()
            
            # Note: doc[page_idx] fonctionne car doc est une liste de pages (NDArray)
            fig = visualize_page(page_dict, doc[page_idx], interactive=False)
            
            nom_preuve = f"verif_page_{page_idx}_{nom_base}.png"
            chemin_preuve = os.path.join(dossier_sortie, nom_preuve)
            
            fig.savefig(chemin_preuve, bbox_inches='tight', dpi=200)
            plt.close(fig) # TRÈS IMPORTANT : évite de saturer la RAM sur Colab

            # --- ACCUMULATION DU TEXTE ---
            for block in page.blocks:
                for line in block.lines:
                    texte_ligne = " ".join([word.value for word in line.words])
                    texte_brut_complet += texte_ligne + "\n"
        
        return texte_brut_complet.strip()

    except Exception as e:
        print(f"DEBUG OCR ERROR: {str(e)}")
        raise Exception(f"Erreur lors de l'OCR : {e}")