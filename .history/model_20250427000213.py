from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Charger le modèle Mistral
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Si tu es sur GPU :
device = "cuda" if torch.cuda.is_available() else "cpu"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto"  # Pas de quantization
)