import urllib.parse
import requests
from core.llm import chat
from core.config import TEXT_MODEL


def expand_prompt(user_prompt: str) -> str:
    msgs = [
        {"role": "system", "content":
         "You are an expert image-prompt engineer. "
         "Rewrite the user's idea into a rich, detailed English image prompt. "
         "Return only the prompt, no quotes, no explanations."},
        {"role": "user", "content": user_prompt},
    ]
    return chat(msgs, TEXT_MODEL, temperature=0.8).strip()


def generate_image(prompt: str, width=768, height=768):
    """Free, key-less image generation via Pollinations."""
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true"
    )
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.content