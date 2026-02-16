import os
from google import genai
from dotenv import load_dotenv

#List of possible fruits the AI can choose from.
#For demo purposes no database is used.
from labels import possiblefruits

load_dotenv()
api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)

def fruit_agent(image_path: str) -> str:
    fruit_image = client.files.upload(file=f"{image_path}")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[fruit_image,
                f"""You are a fruit classification AI.
                The uploaded image contains exactly one type of fruit.
                Only choose from this list: {', '.join(possiblefruits)}.
                Reply with exactly ONE fruit name from the list.
                Do NOT invent or add any other fruit names. If it is not on the list, it is unknown"""]
        )
    
    #Check for hallucinations, e.g. chosen fruit not in list
    imageresult = response.text.strip().lower()
    if imageresult in possiblefruits:
        return imageresult
    else:
        return "unknown"

    