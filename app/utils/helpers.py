"""Helper functions."""

def clean_json_response(response_text: str) -> str:
    """Extract JSON from response, removing markdown blocks and surrounding text."""
    # Remove markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        parts = response_text.split("```")
        if len(parts) > 1:
            response_text = parts[1]
    
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
