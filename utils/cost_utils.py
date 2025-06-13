def estimer_cout_depuis_duree(duree_minutes: float, modele: str = "gpt-4o") -> float:
    """
    Estime le coût total (en dollars) d’un appel OpenAI basé sur :
    - la durée audio (pour Whisper)
    - le modèle texte utilisé

    Par défaut : Whisper à $0.006/min + gpt-4o (texte) à $0.005 par 1000 tokens (approximé à 150 tokens/min)
    """
    whisper_cout = duree_minutes * 0.006
    tokens_estimes = duree_minutes * 150
    if modele == "gpt-4o":
        gpt_cout = (tokens_estimes / 1000) * 0.005
    else:
        gpt_cout = 0  # à adapter si tu veux gérer d'autres modèles

    return round(whisper_cout + gpt_cout, 4)
