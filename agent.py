"""
ADK Agent using Google Gemini for text classification
This agent classifies input text into predefined categories
"""

import google.generativeai as genai
from typing import Any
import json
import os
import time

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
    
    def batch_classify(self, texts: list[str]) -> dict[str, Any]:
        """
        Classify multiple texts in batch

        Args:
            texts: List of texts to classify

        Returns:
            Dictionary with batch classification results
        """
        if not texts:
            return {
                "success": False,
                "error": "No texts provided for batch classification"
            }

        if not isinstance(texts, list):
            return {
                "success": False,
                "error": "Texts must be a list"
            }

        results = []
        stats = {"total": len(texts), "successful": 0, "failed": 0, "categories": {}}

        for text in texts:
            result = self.classify(text)
            results.append(result)

            if result.get("success"):
                stats["successful"] += 1
                category = result.get("classification", {}).get("category")
                if category:
                    stats["categories"][category] = stats["categories"].get(category, 0) + 1
            else:
                stats["failed"] += 1
                
            # Add a delay between API calls to prevent Gemini Rate Limits (429 errors)
            time.sleep(4)

        return {
            "success": True,
            "results": results,
            "statistics": stats
        }

    def get_category_descriptions(self) -> dict[str, str]:
        """Get descriptions for each category"""
        return {
            "NEWS": "Current events, news articles, press releases",
            "OPINION": "Opinion pieces, editorials, personal views",
            "TECHNICAL": "Technical documentation, code, specifications",
            "MARKETING": "Marketing content, advertisements, promotions",
            "EDUCATIONAL": "Educational materials, tutorials, learning content"
        }

    def process_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming request and return classification

        Args:
            request_data: Request containing 'text' field or 'texts' for batch

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
