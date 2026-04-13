import os
import matplotlib.pyplot as plt
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.utils.visualization import visualize_page
from PIL import Image

# Initialisation unique du modèle
model = ocr_predictor(pretrained=True).cpu()

def extraire_texte_et_preuve(chemin_fichier, dossier_sortie):
    """
    OCR robuste : Gère les PDF, les photos et les captures d'écran (conversion RGB).
    """
    try:
        extension = os.path.splitext(chemin_fichier)[1].lower()
        
        # 1. Traitement spécifique selon le type
        if extension == ".pdf":
            doc = DocumentFile.from_pdf(chemin_fichier)
        else:
            # Sécurité pour les captures d'écran : Conversion en RGB pur
            # Cela enlève le canal Alpha (transparence) qui fait souvent planter docTR
            with Image.open(chemin_fichier) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    img.save(chemin_fichier) # On écrase avec la version propre
            
            doc = DocumentFile.from_images(chemin_fichier)

        # 2. Analyse OCR par docTR
        result = model(doc)

        # 3. Extraction et génération des preuves
        texte_brut_complet = ""
        nom_base = os.path.basename(chemin_fichier)

        for page_idx, page in enumerate(result.pages):
            # --- SAUVEGARDE DE LA PREUVE VISUELLE ---
            page_dict = page.export()
            fig = visualize_page(page_dict, doc[page_idx], interactive=False)
            
            nom_preuve = f"verif_page_{page_idx}_{nom_base}.png"
            chemin_preuve = os.path.join(dossier_sortie, nom_preuve)
            
            fig.savefig(chemin_preuve, bbox_inches='tight', dpi=200)
            plt.close(fig) # Libère la mémoire vive

            # --- ACCUMULATION DU TEXTE ---
            for block in page.blocks:
                for line in block.lines:
                    texte_ligne = " ".join([word.value for word in line.words])
                    texte_brut_complet += texte_ligne + "\n"
        
        return texte_brut_complet.strip()

    except Exception as e:
        # On affiche l'erreur réelle dans le terminal pour le dev
        print(f"DEBUG OCR ERROR: {str(e)}")
        raise Exception(f"Erreur lors de l'OCR : {e}")