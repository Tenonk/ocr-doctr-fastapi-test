# 🔍 OCR & Data Extraction Pipeline (PoC)

> **Module de reconnaissance visuelle et structuration intelligente de données.**

Ce projet est une **Preuve de Concept (PoC)** technique. Il démontre la capacité à extraire des informations textuelles depuis des documents d'identité (CNI) et à les transformer en données structurées exploitables (JSON). 

C'est une brique technologique majeure destinée à être intégrée dans le projet **Eburni-Kan**.

---

## 🛠️ Stack Technique

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Backend** | `FastAPI` | Framework web haute performance pour l'API. |
| **Vision (OCR)** | `docTR` | Détection et reconnaissance de texte par Deep Learning. |
| **Intelligence** | `Groq (Llama 3)` | Structuration sémantique du texte brut en JSON. |
| **Environnement** | `Poetry` | Gestionnaire de dépendances moderne. |
| **Déploiement** | `Docker` | Conteneurisation pour une portabilité totale. |

---

## 🚀 Fonctionnalités Clés

* **Précision Chirurgicale** : Utilisation de modèles de détection (`db_resnet50`) et reconnaissance (`crnn_vgg16_bn`) via **docTR**.
* **Preuve de Traitement** : Génération d'une image de sortie mettant en évidence les zones de texte détectées.
* **Extraction Intelligente** : Nettoyage automatique des bruits de lecture grâce au LLM (Llama 3).
* **Infrastructure Moderne** : Orchestration complète via `docker-compose.yml`.

---

## 📦 Installation et Lancement

### 1. Configuration
Créez un fichier `.env` à la racine du projet pour vos secrets :
```env
GROQ_API_KEY=votre_cle_ici