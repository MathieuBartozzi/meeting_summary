# 📝 Meeting Summary App

Une application Streamlit simple et efficace pour :

- Enregistrer une réunion directement depuis le navigateur
- Transcrire automatiquement l’audio grâce à l’API OpenAI (Whisper)
- Générer un compte-rendu structuré selon plusieurs formats (synthétique, détaillé, actions à faire, etc.)

---

## 🚀 Utilisation

1. Clone le repo :
   ```bash
   git clone https://github.com/MathieuBartozzi/meeting_summary.git
   cd meeting_summary
   ```

2. Installe les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lance l’application :
   ```bash
   streamlit run app.py
   ```

4. Renseigne ta clé OpenAI dans l’interface, puis :
   - Enregistre ta réunion (ou dépose un fichier audio `.mp3`, `.wav`, etc.)
   - Choisis un format de synthèse
   - Clique sur **Générer** pour obtenir ton compte-rendu

---

## ⚠️ Confidentialité

Les fichiers audio sont envoyés à l’API OpenAI pour transcription.  
**N’utilise pas cette application pour des données sensibles ou confidentielles.**

---

## ☕ Soutenir le projet

Tu peux soutenir ce travail ici :  
👉 [https://www.buymeacoffee.com/mathieubartozzi](https://www.buymeacoffee.com/mathieubartozzi)

---

## 📦 Fonctionnalités à venir

- Export PDF du compte-rendu
- Interface multi-utilisateur
- Historique des réunions

---

## ✨ Crédits

Développé par [Mathieu Bartozzi](https://github.com/MathieuBartozzi)  
Licencié sous MIT.
