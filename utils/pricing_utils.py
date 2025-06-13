def afficher_tarification_estimee(format_choisi, st):
    """
    Affiche une table Streamlit estimant les coûts en fonction du format choisi.
    """
    if format_choisi == "Résumé synthétique":
        factor = 1.0
    elif format_choisi == "Résumé détaillé":
        factor = 1.5
    elif format_choisi == "Actions / Décisions / À faire":
        factor = 1.2
    elif format_choisi == "Faits marquants + apprentissages":
        factor = 1.3
    elif format_choisi == "Compte-rendu pour mail ou PV":
        factor = 1.1
    elif format_choisi == "Libre (personnalisé)":
        factor = 1.4
    else:
        factor = 1.0  # fallback

    whisper_rates = {
        1: 0.006,
        5: 0.030,
        10: 0.060,
        20: 0.120,
        30: 0.180,
    }

    markdown_table = """
| Durée (min) | Coût transcription (Whisper) | Coût résumé (GPT-4o) | Total estimé |
|-------------|-------------------------------|------------------------|---------------|
"""

    for dur, t_cost in whisper_rates.items():
        gpt_cost = round(0.005 * (dur / 1.0) * factor, 3)
        total = round(t_cost + gpt_cost, 3)
        markdown_table += f"| {dur} min | ${t_cost:.3f} | ~ ${gpt_cost:.3f} | ~ ${total:.3f} |\n"

    st.markdown("### Tarification indicative")
    st.markdown(markdown_table)
    st.caption(f"Adapté pour le format **{format_choisi}** (coût résumé ×{factor})")
