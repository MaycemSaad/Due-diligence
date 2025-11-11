import ollama

# Nom du modèle Ollama local
model_name = "mistral"  # ⚡ Attention, ce n'est PAS "mistralai/Mistral-7B-Instruct-v0.1" sur Ollama, juste "mistral"

def generate_response(prompt):
    """
    Envoie un prompt à Ollama en local et retourne la réponse.
    """
    response = ollama.chat(
        model=model_name,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']
