import os
import re
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, tool

# Define our secure password variable
API_KEY_NAME = "X-Comedy-Agent-Auth"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Generate a strong password here or read it from system environment variables
SECRET_TOKEN = os.getenv("AGENT_PASSWORD", "CHANGE_THIS_TO_A_SECRET_PASSWORD")

app = FastAPI(title="Comedy SEO Agent Protected API")
model = LiteLLMModel(model_id="openai/gpt-4o")
search_tool = DuckDuckGoSearchTool()

@tool
def format_youtube_studio_text(text: str) -> str:
    """Cleans up markdown formatting for crisp copy-pasting."""
    cleaned = re.sub(r'###\s*', '', text)
    cleaned = re.sub(r'\*\*(.*?)\*\*:', r'\1:', cleaned)
    divider = "\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
    sections = cleaned.split('\n\n')
    formatted_text = [section.strip() for section in sections if section.strip()]
    return divider.join(formatted_text) + divider

class TranscriptInput(BaseModel):
    transcript: str

# Protection middleware function
async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized access to Comedy Agent Engine.")
    return api_key

@app.post("/optimize-seo")
async def generate_seo(data: TranscriptInput, api_key: str = Depends(verify_api_key)):
    if not data.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is blank")
        
    comedian_dna = """
    You are the ultimate YouTube SEO Agent, Transcript Script Doctor, and Visual Thumbnail Designer for a stand-up comedian. 
    Comedian Profile:
    - Gear: Shoots on a Sony FS5. Edits in DaVinci Resolve.
    - Style: Laid-back, storytelling, sharp one-liners.
    - Themes: Mexican-American experience, growing up broke, economic hypocrisies.
    """
    
    try:
        advanced_comedy_agent = CodeAgent(
            tools=[search_tool, format_youtube_studio_text],
            model=model,
            additional_authorized_imports=["json", "re", "string"]
        )
        raw_output = advanced_comedy_agent.run(f"{comedian_dna}\n\nProcess this stand-up concept:\n'{data.transcript}'")
        formatted_output = format_youtube_studio_text(raw_output)
        
        return {"success": True, "raw_agent_preview": raw_output, "studio_copy_paste": formatted_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
