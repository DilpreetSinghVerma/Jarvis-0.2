import os
import base64
from decouple import config
from groq import Groq
from google import genai
import PIL.Image
import io

def test_groq():
    print("Testing Groq Vision...")
    api_key = config("GROQ_API_KEY", default="")
    if not api_key:
        print("Groq Key missing")
        return
    client = Groq(api_key=api_key)
    try:
        # Create a tiny black dummy image
        img = PIL.Image.new('RGB', (100, 100), color = (0, 0, 0))
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='JPEG')
        base64_image = base64.b64encode(byte_arr.getvalue()).decode('utf-8')
        
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{"role": "user", "content": [{"type": "text", "text": "What is this?"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
            max_tokens=50
        )
        print("Groq Response:", completion.choices[0].message.content)
    except Exception as e:
        print("Groq Error:", e)

def test_gemini():
    print("\nTesting Gemini Vision...")
    api_key = config("GEMINI_API_KEY", default="")
    client = genai.Client(api_key=api_key)
    try:
        img = PIL.Image.new('RGB', (100, 100), color = (0, 0, 0))
        # Use g-1.5-flash
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=["What is this?", img]
        )
        print("Gemini Response:", response.text)
    except Exception as e:
        print("Gemini Error:", e)

if __name__ == "__main__":
    test_groq()
    test_gemini()
