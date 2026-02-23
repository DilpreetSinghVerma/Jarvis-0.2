from groq import Groq
from decouple import config

def list_groq_models():
    api_key = config("GROQ_API_KEY", default="")
    client = Groq(api_key=api_key)
    try:
        models = client.models.list()
        with open("groq_models.txt", "w") as f:
            for m in models.data:
                f.write(f"{m.id}\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_groq_models()
