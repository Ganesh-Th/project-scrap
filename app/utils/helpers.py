"""Helper functions."""
import re


def clean_json_response(response_text: str) -> str:
    """Extract JSON from response, removing markdown blocks, control characters, and surrounding text."""
    if not response_text:
        return "{}"
    
    # Remove control characters except newline, tab, carriage return
    response_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', response_text)
    
    # Remove markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        response_text = json_match.group(1)
    
    # Extract JSON object
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        response_text = response_text[start_idx:end_idx + 1]
        
    return response_text.strip()


def sanitize_pipe_text(text: str) -> str:
    """Replace pipe characters and newlines for TOON format."""
    if not text:
        return ""
    return str(text).replace("|", " ").replace("\n", " ").replace("\r", " ")
