import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from utils.audio_utils import safe_filename, get_audio_duration, split_audio
from utils.usage_logger import log_usage
import io
from streamlit_extras.buy_me_a_coffee import button




format_options = {
    "Résumé synthétique": (
        "Propose un résumé clair et concis de la réunion. "
        "Identifie les principaux sujets abordés et synthétise les échanges en quelques paragraphes, sans entrer dans les détails opérationnels. "
        "Le texte doit permettre une compréhension rapide des enjeux discutés."
    ),
    "Résumé détaillé": (
        "Rédige un compte-rendu structuré et approfondi de la réunion. "
        "Organise le contenu par thématiques ou suivant la chronologie des interventions. "
        "Expose les idées clés, les débats, les prises de position et les décisions éventuelles. "
        "Le style doit rester professionnel, fluide et facile à lire."
    ),
    "Actions / Décisions / À faire": (
        "Présente un relevé d’informations organisé en trois sections distinctes :\n"
        "1. **Décisions prises** : ce qui a été validé ou tranché ;\n"
        "2. **Actions à mettre en œuvre** : tâches, responsables, échéances ;\n"
        "3. **Points en suspens** : éléments à clarifier, sujets à reporter ou approfondir."
    ),
    "Faits marquants + apprentissages": (
        "Synthétise les temps forts de la réunion en mettant en lumière les éléments marquants, les tournants décisifs ou les moments de consensus. "
        "Ajoute les enseignements à tirer, y compris ceux qui ne sont pas explicitement formulés mais perceptibles (retours d’expérience, bonnes pratiques, changements de posture)."
    ),
    "Compte-rendu pour mail ou PV": (
        "Formule un compte-rendu clair, structuré et directement exploitable dans un email ou pour un procès-verbal. "
        "Utilise un style neutre et professionnel, avec des paragraphes courts ou des listes à puces si nécessaire, facilitant la lecture rapide."
    ),
    "Libre (personnalisé)": (
        "Format libre : spécifie ci-dessous le type de restitution souhaité. "
        "Tu peux décrire le ton, la structure ou les éléments à inclure de manière personnalisée."
    )
}



# ─────────────────────────────────────────────────────────────────────
# 🧭 EN-TÊTE + CLÉ API
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Résumé de réunion", layout="wide")

# ─────────────────────────────────────────────────────────────────────
# 🔐 SIDEBAR : CLÉ API
# ─────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("🔐 Paramètres")
    api_key = st.text_input("Clé API OpenAI", type="password", placeholder="sk-...")

    with st.popover("Comment obtenir une clé API OpenAI ?"):
        st.markdown("""
            - Crée un compte sur [platform.openai.com](https://platform.openai.com/)
            - Ajoute du crédit** dans l’onglet [Billing](https://platform.openai.com/account/billing/overview) pour accéder aux modèles.
            - Va dans **'API keys'** via le menu en haut à droite.
            - Clique sur **'Create new secret key'** et copie-la dans le champ ci-dessus.
            - **Important** : ⚠️ Ne partage jamais ta clé API publiquement
            """)
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("---")

    st.sidebar.markdown(
    "<div style='font-size: 0.85rem; margin-top: 0.5rem;'>Un petit café pour soutenir le projet ☕</div>",
    unsafe_allow_html=True)
    button(username="mathieubartozzi")








# ─────────────────────────────────────────────────────────────────────
# 🧭 INTRO + GUIDE
# ─────────────────────────────────────────────────────────────────────
st.markdown("## 📝 Générateur de compte-rendu de réunion")

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


# ─────────────────────────────────────────────────────────────────────
# 🧱 3 COLONNES PRINCIPALES
# ─────────────────────────────────────────────────────────────────────
st.markdown("---")

col1, col2, col3 = st.columns(3)

# 1️⃣ ENREGISTREUR

with col1:
    with st.container(border=True, height=300):
        st.markdown("### Record")
        st.write("")
        with open("enregistreur.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=220)

# ─────────────────────────────────────────────────────────────────────

# 2️⃣ UPLOAD
with col2:
    with st.container(border=True, height=300):
        st.markdown("### Upload")
        audio_file = st.file_uploader("", type=["webm", "mp3", "wav", "ogg", "flac", "mp4", "m4a"])
        full_transcript = None
        if audio_file and api_key:
            client = OpenAI(api_key=api_key)
            audio_bytes = audio_file.read()
            duration_min = get_audio_duration(audio_bytes)
            st.info(f"⏱ Durée détectée : {duration_min:.1f} min")

            with st.spinner("🔍 Transcription en cours..."):
                if duration_min > 60:
                    st.warning("⚠️ Fichier long : découpé automatiquement (30 min max/segment).")
                    chunks = split_audio(audio_bytes, original_filename=audio_file.name)
                    transcripts = []
                    for i, chunk in enumerate(chunks):
                        with st.spinner(f"Segment {i+1}/{len(chunks)}..."):
                            transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=chunk,
                                response_format="text"
                            )
                            transcripts.append(transcript)
                    full_transcript = "\n\n---\n\n".join(transcripts)
                else:
                    audio_io = io.BytesIO(audio_bytes)
                    audio_io.name = safe_filename(audio_file.name)
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_io,
                        response_format="text"
                    )
                    full_transcript = transcript

            st.success("✅ Transcription terminée")
            st.text_area("📝 Transcript brut", full_transcript, height=200)

        elif audio_file and not api_key:
            st.warning("💡 Clé API requise pour générer la transcription.")

# 3️⃣ FORMAT
with col3:
    with st.container(border=True, height=300):
        st.markdown("### Summarize")
        choice = st.selectbox("", list(format_options.keys()))
        if choice == "Libre (personnalisé)":
            custom_prompt = st.text_area("✏️ Instructions personnalisées :", value="")

# ─────────────────────────────────────────────────────────────────────
# 🔴 BOUTON GÉNÉRATION
# ─────────────────────────────────────────────────────────────────────

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

if st.button("✨ Générer le compte-rendu", type="primary"):
    if full_transcript and api_key:
        log_usage(format_choice=choice, duration=duration_min)
        with st.spinner("✍️ Génération en cours..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui génère des comptes-rendus professionnels à partir de réunions transcrites."},
                    {"role": "user", "content": f"Voici la transcription de la réunion :\n\n{full_transcript}\n\n{custom_prompt}"}
                ],
                temperature=0.5
            )
            summary = response.choices[0].message.content
            st.success("✅ Compte-rendu généré")
            st.markdown("📃 Compte-rendu final", summary, height=300)
            st.download_button("📥 Télécharger", summary, file_name="compte_rendu.txt")
    else:
        st.error("🚫 Il faut d'abord importer un fichier audio ET saisir une clé API.")
