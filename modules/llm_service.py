import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

def fetch_llm_response(prompt: str) -> str:
    """
    Sends the prompt to the gemini-3.6-flash model via Google AI Studio
    and returns the raw JSON string response.
    """
    # 1. Load environment variables from the .env file
    load_dotenv()

    # 2. Securely fetch the Google API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("No GOOGLE_API_KEY found. Please check your .env file.")

    # 3. Initialize the Gemini client
    client = genai.Client(api_key=api_key)

    # 4. Set up system instructions and generation parameters
    config = types.GenerateContentConfig(
        system_instruction="You are a Senior Data Analyst who outputs structural analysis exclusively in JSON format.",
        response_mime_type="application/json", 
        temperature=0.7,
        max_output_tokens=2000,
    )

    # 5. Make the generation call using Gemini 3.6 Flash model
    response = client.models.generate_content(
    model="gemini-3.6-flash", 
    contents=prompt,
    config=config,
    )

    return response.text
