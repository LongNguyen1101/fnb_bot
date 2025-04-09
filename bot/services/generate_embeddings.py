from google import genai
from dotenv import load_dotenv
from typing import List

load_dotenv()

def generate_embedding(text: str) -> List[float]:
    client = genai.Client()
    
    result = client.models.embed_content(
        model = "models/embedding-001",
        contents = text
    )
    
    return result.embeddings[0].values