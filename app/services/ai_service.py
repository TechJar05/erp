from openai import OpenAI
from app.core.config import get_settings
from typing import List, Dict, Any
import json

class AIService:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        json_mode: bool = False
    ) -> str:
        """
        Send a chat completion request to OpenAI
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            json_mode: If True, forces JSON output
            
        Returns:
            Response content as string
        """
        try:
            # Prepend system message if provided
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    *messages
                ]
            
            # Build request params
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Enable JSON mode if requested
            if json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            # Make API call
            response = self.client.chat.completions.create(**request_params)
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Safely parse JSON response from AI
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")