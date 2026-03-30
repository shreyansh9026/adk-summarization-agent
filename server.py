"""
Flask server for ADK Agent
Exposes the text classification agent via HTTP endpoints
"""

import os
import json
from flask import Flask, request, jsonify
from agent import create_agent

app = Flask(__name__)

# Initialize the agent on startup
try:
    agent = create_agent()
    app.agent = agent
except Exception as e:
    print(f"Warning: Could not initialize agent - {e}")
    app.agent = None


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ADK Text Classification Agent",
        "version": "1.0.0"
    }), 200


@app.route("/classify", methods=["POST"])
def classify():
    """
    Main endpoint for text classification
    
    Expected request body:
    {
        "text": "Input text to classify"
    }
    
    Response:
    {
        "success": true,
        "text": "Input text preview",
        "classification": {
            "category": "NEWS|OPINION|TECHNICAL|MARKETING|EDUCATIONAL",
            "confidence": 0.0-1.0,
            "reasoning": "Explanation"
        }
    }
    """
    if not app.agent:
        return jsonify({
            "success": False,
            "error": "Agent not initialized. Check GOOGLE_API_KEY environment variable."
        }), 503
    
    # Parse request
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be valid JSON"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Invalid JSON: {str(e)}"
        }), 400
    
    # Process with agent
    result = app.agent.process_request(data)
    
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/agent/info", methods=["GET"])
def agent_info():
    """Get information about the agent"""
    if not app.agent:
        categories = []
    else:
        categories = app.agent.categories
    
    return jsonify({
        "agent_type": "TextClassificationAgent",
        "capability": "Classify text into predefined categories",
        "categories": categories,
        "models_used": ["gemini-pro"],
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Health check"},
            {"path": "/classify", "method": "POST", "description": "Classify text"},
            {"path": "/agent/info", "method": "GET", "description": "Get agent info"}
        ]
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/classify", "/agent/info"]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    # Get port from environment or default to 8080 (Cloud Run standard)
    port = int(os.environ.get("PORT", 8080))
    
    # Run the app
    # In production (Cloud Run), use gunicorn instead
    app.run(host="0.0.0.0", port=port, debug=False)
