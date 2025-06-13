import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from utils.audio_utils import safe_filename, split_audio
from utils.usage_logger import log_usage
from streamlit_extras.buy_me_a_coffee import button
from utils.pricing_utils import afficher_tarification_estimee

import io

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 FORMAT OPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

format_options = {
    "Résumé synthétique": "Propose un résumé clair et concis de la réunion...",
    "Résumé détaillé": "Rédige un compte-rendu structuré et approfondi...",
    "Actions / Décisions / À faire": "Présente un relevé organisé en 3 sections...",
    "Faits marquants + apprentissages": "Synthétise les temps forts et les apprentissages...",
    "Compte-rendu pour mail ou PV": "Formule un compte-rendu clair et structuré...",
    "Libre (personnalisé)": "Format libre à spécifier ci-dessous.",
}

client = None
full_transcript = None

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 CONFIG + API
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Résumé de réunion", layout="wide")

with st.sidebar:
    st.header("🔐 Paramètres")
    api_key = st.text_input("Clé API OpenAI", type="password", placeholder="sk-...")

    with st.popover("Comment obtenir une clé API OpenAI ?"):
        st.markdown("""

        - *Crée* un compte sur [platform.openai.com](https://platform.openai.com/)
        - *Ajoute* du crédit dans [Billing](https://platform.openai.com/account/billing/overview)
        - *Va* dans **'API keys'** > **'Create new secret key'**
        - *Clique* sur 'Create new secret key' et copie-la dans le champ ci-dessus.

        *Important* : ⚠️ Ne partage jamais ta clé API publiquement
        """)

    st.markdown("---")
    st.markdown("<div style='font-size: 0.85rem;'>Un petit café pour soutenir le projet ☕</div>", unsafe_allow_html=True)
    button(username="mathieubartozzi")

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 INTRO
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Générateur automatique de compte-rendu de réunion")
col1, col2 = st.columns([4,1])
with col1:
    st.info("""
    Ce service s'utilise en **3 étapes obligatoires** :
    1. **Ajoute ta clé API** OpenAI dans la barre latérale.
    2. **Enregistre** ta réunion dans le navigateur.
    3. **Télécharge et dépose** le fichier audio.
    4. **Génère** ton compte-rendu personnalisé.
    """)

with col2:
    st.warning("""
                **🔒 À propos des données traitées**

                Les fichiers sont envoyés aux serveurs d’OpenAI. Évite d’y inclure des contenus sensibles.

                """
    )


st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# 🧱 ZONE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

col1, col2, col3 = st.columns(3)

# 1️⃣ ENREGISTREUR
with col1:
    with st.container(border=True, height=300):
        st.markdown("### Record")
        with open("enregistreur.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=220)

# 2️⃣ UPLOAD
with col2:
    with st.container(border=True, height=300):
        st.markdown("### Drag & Drop")
        audio_file = st.file_uploader("", type=["webm", "mp3", "wav", "ogg", "flac", "mp4", "m4a"])
        if audio_file:
            audio_bytes = audio_file.read()
            file_size_mb = len(audio_bytes) / (1024 * 1024)

            with st.spinner("🔍 Transcription en cours..."):
                client = OpenAI(api_key=api_key)

                # si > 25 Mo on découpe par prudence
                if file_size_mb > 25:
                    st.warning("⚠️ Fichier volumineux : découpé automatiquement")
                    chunks = split_audio(audio_bytes, original_filename=audio_file.name)
                    transcripts = []
                    for i, chunk in enumerate(chunks):
                        with st.spinner(f"⏱ Segment {i+1}/{len(chunks)}..."):
                            result = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=chunk,
                                response_format="text"
                            )
                            transcripts.append(result)
                    full_transcript = "\n\n---\n\n".join(transcripts)
                else:
                    audio_io = io.BytesIO(audio_bytes)
                    audio_io.name = safe_filename(audio_file.name)
                    result = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_io,
                        response_format="text"
                    )
                    full_transcript = result


# 3️⃣ FORMAT
with col3:
    with st.container(border=True, height=300):
        st.markdown("### Summarize")
        choice = st.selectbox("", list(format_options.keys()))
        custom_prompt = ""
        if choice == "Libre (personnalisé)":
            custom_prompt = st.text_area("✏️ Instructions personnalisées", "")
        with st.popover("💸 Combien ?"):
            afficher_tarification_estimee(choice, st)
            st.caption("Ces tarifs sont purement indicatifs. Le coût réel dépend de la taille du fichier et de la réponse générée.")


# ═══════════════════════════════════════════════════════════════════════════════
# ✨ GÉNÉRATION DU COMPTE-RENDU
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)


# Bouton de génération
if st.button("✨ Générer le compte-rendu", type="primary"):

    if client is None or not api_key or not audio_file or full_transcript is None:
        st.error("🚫 Merci de compléter toutes les étapes (clé API, fichier audio, transcription).")

    else:
        with st.spinner("⏳ Génération du résumé..."):
            lang_hint = "La langue du compte-rendu doit être la même que celle utilisée dans la réunion."
            prompt = (custom_prompt if choice == "Libre (personnalisé)" else format_options[choice]) + f"\n\n{lang_hint}"
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui génère des comptes-rendus professionnels à partir de réunions transcrites. Tu dois répondre dans la même langue que celle de la transcription."},
                    {"role": "user", "content": f"Voici la transcription :\n\n{full_transcript}\n\n{prompt}"}
                ],
                temperature=0.5
            )
            summary = response.choices[0].message.content
            st.success("✅ Compte-rendu généré")
            st.markdown("### 📃 Compte-rendu final")
            st.markdown(summary)
            st.download_button("📥 Télécharger", summary, file_name="compte_rendu.txt")

        # Optionnel si tu n’as plus la durée :
        # log_usage(format_choice=choice, duration=estimated_duration)
        log_usage(format_choice=choice, duration=None)
