import google.generativeai as genai
from decouple import config

api_key = config("GEMINI_API_KEY")
genai.configure(api_key=api_key)

with open("available_models.txt", "w") as f:
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(m.name + "\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
