"""Prioritization service using Gemini."""
import json
import asyncio
from typing import Dict, Any

from app.config import get_settings
from app.logging_config import get_logger
from app.utils.helpers import clean_json_response
from app.services.sentiment import create_gemini_client_with_tools


logger = get_logger(__name__)
settings = get_settings()


async def perform_prioritization(
    toon_content: str, 
    method: str, 
    duration: int, 
    budget: int, 
    business_goal: str
) -> Dict[str, Any]:
    """
    Uses Gemini to prioritize tasks and returns a JSON dictionary.
    
    Args:
        toon_content: TOON formatted content from sentiment analysis
        method: Prioritization method (MoSCoW or Lean Prioritization)
        duration: Sprint duration in days
        budget: Developer hours budget
        business_goal: Current business goal
    
    Returns:
        Dictionary containing the prioritization plan
    """
    logger.info(f"Starting {method} prioritization. Goal: '{business_goal}', Budget: {budget}hrs")
    
    client, model_name, generate_config = create_gemini_client_with_tools()

    prompt = f"""You are an expert Product Manager.
    
    CONTEXT:
    We have analyzed user feedback and generated a list of issues in TOON format.
    We need to prioritize these tasks for our next sprint.

    INPUTS:
    1. PRIORITIZATION FRAMEWORK: {method}
       - If MoSCoW: Categorize into Must Have, Should Have, Could Have, Won't Have.
       - If Lean: Categorize into High Impact/Low Effort, High Impact/High Effort, Low Impact/Low Effort.
    2. SPRINT DURATION: {duration} Days
    3. RESOURCE BUDGET: {budget} Developer Hours
    4. CURRENT BUSINESS GOAL: "{business_goal}"

    INSTRUCTIONS:
    1. Analyze the TOON data provided below.
    2. Select the most critical items that align with the '{business_goal}' and {method} Framework.
    3. Estimate developer hours for each task based on severity and complexity.
    4. Ensure the total hours of selected 'Must Have' tasks do not exceed the budget of {budget} hours.
    5. Output a structured plan.
    
    CRITICAL - OUTPUT FORMAT:
    - Do NOT include any explanation, reasoning, or text before the JSON
    - Do NOT include markdown code blocks (no ```json or ```)
    - Output ONLY the raw JSON object starting with {{ and ending with }}
    - The response must be valid JSON that can be parsed by json.loads()
    
    JSON SCHEMA:
    {{
      "plan_metadata": {{
        "method": "{method}",
        "goal": "{business_goal}",
        "budget_hours": {budget},
        "sprint_duration_days": {duration}
      }},
      "prioritized_categories": [
        {{
          "category_name": "Name (e.g., Must Have or High Impact)",
          "tasks": [
            {{
              "title": "Task Title",
              "type": "bug/feature/etc",
              "impact_reasoning": "Why this is chosen",
              "estimated_hours": <int>
            }}
          ]
        }}
      ], 
      "summary": {{
        "total_estimated_hours": <int>,
        "budget_utilization_percentage": <float>,
        "key_risks": ["risk 1", "risk 2"]
      }}
    }}

    TOON DATA:
    {toon_content}
    """

    try:
        loop = asyncio.get_event_loop()
        
        def generate_content():
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=generate_config
            )
            return response.text if response else None
        
        response_text = await loop.run_in_executor(None, generate_content)
        
        if not response_text:
            logger.error("Gemini returned empty response for prioritization")
            return {
                "error": "AI returned empty response. Please try again.",
                "raw_response": ""
            }
        
        cleaned_json = clean_json_response(response_text)
        
        if not cleaned_json or cleaned_json == "{}":
            logger.error(f"Failed to extract JSON from response: {response_text[:500]}")
            return {
                "error": "Failed to extract valid JSON from AI response",
                "raw_response": response_text[:500]
            }
        
        try:
            plan_data = json.loads(cleaned_json)
            logger.info(f"Prioritization completed successfully using {method}")
            return plan_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse prioritization response: {e}")
            return {
                "error": f"Failed to parse response: {str(e)}",
                "raw_response": cleaned_json[:500]
            }
            
    except Exception as e:
        logger.error(f"Error during prioritization: {e}", exc_info=True)
        return {"error": f"Error during prioritization: {str(e)}"}
