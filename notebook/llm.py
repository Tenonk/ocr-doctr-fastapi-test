import os
import json
from groq import Groq
from dotenv import load_dotenv

# 1. Charge les variables du fichier .env dans l'environnement système
load_dotenv()

# 2. Récupère la clé via os.getenv (plus sécurisé)
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("ERREUR : La clé GROQ_API_KEY est introuvable dans le fichier .env")

client = Groq(api_key=api_key)

def structurer_avec_llm(texte_brut):
    """Extrait les données de la CNI en utilisant Groq Cloud."""
    
    prompt_system = (
        "Tu es un expert en documents d'identité de Côte d'Ivoire. "
        "Réponds EXCLUSIVEMENT au format JSON. Si une info manque, mets null."
    )

    try:
        completion = client.chat.completions.create(
            # On utilise le modèle Llama 3.3 70B pour sa précision sur le français
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": texte_brut}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"erreur": f"Problème d'API : {str(e)}"}