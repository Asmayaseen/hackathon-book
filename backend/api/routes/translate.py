import os
import re
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# --- CONFIGURATION (SIMULATION) ---
# NOTE: In a real project, replace MOCK_CACHE with a proper async Redis client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "DUMMY_KEY_FOR_SIMULATION")
MOCK_CACHE: Dict[int, Any] = {} # Key is the hash of content
CACHE_TTL = 30 * 24 * 60 * 60 # 30 days

# --- UTILITY FUNCTIONS ---

def protect_code_blocks(content: str) -> tuple[str, Dict[str, str]]:
    """
    Extracts Markdown code blocks (```...```) and specific technical terms, 
    replacing them with placeholders to prevent translation.
    """
    code_blocks = {}
    
    # 1. Protect Markdown Code Blocks (```...```)
    def code_replacer(match):
        placeholder = f"{{{{CODE_{len(code_blocks)}}}}}"
        code_blocks[placeholder] = match.group(0)
        return placeholder
        
    protected_content = re.sub(r'```.*?```', code_replacer, content, flags=re.DOTALL)

    # 2. Protect Common Technical Terms (Add more terms here as needed)
    technical_terms = ['ROS 2', 'URDF', 'Gazebo', 'API', 'Docker', 'Kubernetes']
    
    for i, term in enumerate(technical_terms):
        placeholder = f"{{{{TERM_{i}}}}}"
        # Use simple string replacement for terms
        if term in protected_content:
            protected_content = protected_content.replace(term, placeholder)
            code_blocks[placeholder] = term 
    
    return protected_content, code_blocks

def restore_placeholders(translated_content: str, placeholders: Dict[str, str]) -> str:
    """
    Restores the original code blocks and technical terms back into the translated text.
    """
    # Important: Iterate through placeholders and replace
    for placeholder, original_text in placeholders.items():
        translated_content = translated_content.replace(placeholder, original_text)
    return translated_content

# Mock/Simulated OpenAI Call Function
async def simulate_openai_translation(text: str, target_lang: str) -> str:
    """
    Mocks the asynchronous call to the OpenAI API for translation.
    In production, you would use 'openai.AsyncOpenAI' here.
    """
    if OPENAI_API_KEY == "DUMMY_KEY_FOR_SIMULATION":
        # Simulation: Attempt a simple translation or return a fake response
        urdu_mapping = {
            "Robot Operating System 2": "روبوٹ آپریٹنگ سسٹم 2",
            "This is a test.": "یہ ایک ٹیسٹ ہے۔",
            "The robot is controlled by the API.": "روبوٹ کو API کے ذریعے کنٹرول کیا جاتا ہے۔"
        }
        
        # Simple lookup for demonstration
        if text in urdu_mapping:
            return urdu_mapping[text]
            
        # Fallback simulation
        return f"FAKE_TRANSLATION_TO_URDU: [{text}]" 
    
    # --- REAL OPENAI CALL (If API Key is set, this is where actual call goes) ---
    # Example structure for real call:
    # from openai import AsyncOpenAI
    # client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    #
    # system_prompt = (
    #     f"Translate the following content to {target_lang}. Preserve all tokens "
    #     f"enclosed in {{...}} exactly as they are."
    # )
    # try:
    #     response = await client.chat.completions.create(
    #         model="gpt-4o", 
    #         messages=[
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": text}
    #         ]
    #     )
    #     return response.choices[0].message.content
    # except Exception:
    #     raise HTTPException(status_code=503, detail="OpenAI service is unavailable.")

# --- API ROUTER AND MODELS ---

router = APIRouter()


class TranslateRequest(BaseModel):
    content: str
    target_lang: str = "ur"  # Urdu
    preserve_code: bool = True


class TranslateResponse(BaseModel):
    original: str
    translated: str
    target_lang: str
    cached: bool = False


@router.post("/urdu", response_model=TranslateResponse)
async def translate_to_urdu(request: TranslateRequest):
    """Translate content to Urdu - Alias for /api/translate/urdu"""
    request.target_lang = "ur"
    return await translate_content(request)


@router.post("/", response_model=TranslateResponse)
async def translate_content(request: TranslateRequest):
    """
    Translate Content to Urdu
    - Preserves technical terms (ROS 2, URDF, etc.)
    - Protects code blocks from translation
    - Caches translations (30-day TTL)
    """
    # Use hash of content for caching key
    content_hash = hash(request.content + request.target_lang)
    
    # 1. Check cache for existing translation
    if cached_result := MOCK_CACHE.get(content_hash):
        return TranslateResponse(
            original=request.content,
            translated=cached_result['translated'],
            target_lang=request.target_lang,
            cached=True
        )

    try:
        # 2. Extract and protect code blocks/terms
        if request.preserve_code:
            protected_content, placeholders = protect_code_blocks(request.content)
        else:
            protected_content = request.content
            placeholders = {}

        # 3. Call OpenAI translation API (via simulation or real call)
        translated_text = await simulate_openai_translation(
            text=protected_content,
            target_lang=request.target_lang
        )

        # 4. Restore code blocks/terms
        final_translated_text = restore_placeholders(translated_text, placeholders)

        # 5. Cache result
        MOCK_CACHE[content_hash] = {
            'translated': final_translated_text,
            'timestamp': time.time()
        }

        # 6. Return translation
        return TranslateResponse(
            original=request.content,
            translated=final_translated_text,
            target_lang=request.target_lang,
            cached=False
        )
    
    except HTTPException:
        # Re-raise explicit HTTP exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported": [
            {"code": "en", "name": "English"},
            {"code": "ur", "name": "Urdu"}
        ]
    }