"""
ADK Agent using Google Gemini for text classification
This agent classifies input text into predefined categories
"""

import google.generativeai as genai
from typing import Any
import json
import os


class TextClassificationAgent:
    """AI Agent for classifying text into categories using Gemini"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the agent with Gemini API key
        
        Args:
            api_key: Google Gemini API key. If None, uses GOOGLE_API_KEY env var
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Try to initialize with the most recent available model
        try:
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        except Exception:
            try:
                self.model = genai.GenerativeModel("gemini-1.5-pro")
            except Exception:
                try:
                    self.model = genai.GenerativeModel("gemini-1.5-flash")
                except Exception:
                    self.model = genai.GenerativeModel("gemini-pro")
        
        self.categories = [
            "NEWS",
            "OPINION",
            "TECHNICAL",
            "MARKETING",
            "EDUCATIONAL"
        ]
    
    def classify(self, text: str) -> dict[str, Any]:
        """
        Classify the given text into one of the predefined categories
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with classification results
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Input text cannot be empty",
                "text": text
            }
        
        # Construct the prompt for Gemini
        prompt = f"""Classify the following text into ONE category from this list: {', '.join(self.categories)}

Text to classify:
"{text}"

Respond in JSON format with the following structure:
{{
    "category": "ONE OF THE CATEGORIES",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of why you chose this category"
}}

Only return valid JSON, no additional text."""
        
        try:
            response = self.model.generate_content(prompt)
            response.resolve()
            
            # Parse the response
            response_text = response.text
            
            # Try to extract JSON from the response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # If response isn't pure JSON, try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {
                        "category": "UNKNOWN",
                        "confidence": 0.0,
                        "reasoning": "Could not extract classification from response"
                    }
            
            # Validate category
            if result.get("category") not in self.categories:
                result["category"] = "UNKNOWN"
                result["confidence"] = 0.0
            
            return {
                "success": True,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "classification": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
    
    def process_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming request and return classification
        
        Args:
            request_data: Request containing 'text' field
            
        Returns:
            Classification result
        """
        text = request_data.get("text", "").strip()
        
        if not text:
            return {
                "success": False,
                "error": "Missing or empty 'text' field in request"
            }
        
        return self.classify(text)


def create_agent(api_key: str = None) -> TextClassificationAgent:
    """Factory function to create agent instance"""
    return TextClassificationAgent(api_key=api_key)
