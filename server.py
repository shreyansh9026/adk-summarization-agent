"""
Flask server for ADK Agent with Interactive Dashboard
Exposes the text classification agent via HTTP endpoints
"""

import os
import json
from flask import Flask, request, jsonify, render_template_string
from agent import create_agent

app = Flask(__name__)

# Initialize the agent on startup
try:
    agent = create_agent()
    app.agent = agent
except Exception as e:
    print(f"Warning: Could not initialize agent - {e}")
    app.agent = None


# HTML Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Text Classification Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .status-bar { display: flex; justify-content: space-around; background: #f5f5f5; padding: 20px; border-bottom: 1px solid #ddd; }
        .status-item { text-align: center; }
        .status-label { font-size: 0.9em; color: #666; margin-bottom: 5px; }
        .status-value { font-size: 1.3em; font-weight: bold; color: #667eea; }
        .status-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 0.85em; font-weight: bold; background: #4caf50; color: white; }
        .content { padding: 40px; }
        .section { margin-bottom: 40px; }
        .section h2 { color: #667eea; margin-bottom: 20px; font-size: 1.5em; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .info-card { background: #f9f9f9; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea; }
        .info-card h3 { color: #333; margin-bottom: 10px; font-size: 1.1em; }
        .info-card p { color: #666; font-size: 0.95em; line-height: 1.6; }
        .demo-section { background: #f0f4ff; padding: 30px; border-radius: 10px; border: 2px solid #667eea; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
        .form-group textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-family: 'Segoe UI', sans-serif; font-size: 1em; min-height: 100px; }
        .form-group textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 5px rgba(102, 126, 234, 0.3); }
        .button-group { display: flex; gap: 10px; }
        .btn { padding: 12px 30px; border: none; border-radius: 5px; font-size: 1em; font-weight: bold; cursor: pointer; transition: all 0.3s ease; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        .btn-secondary { background: #f5f5f5; color: #333; border: 1px solid #ddd; }
        .btn-secondary:hover { background: #eeeeee; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .response-box { background: white; border: 1px solid #ddd; border-radius: 5px; padding: 20px; margin-top: 20px; display: none; }
        .response-box.show { display: block; }
        .response-box pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 0.9em; max-height: 400px; }
        .result-item { margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; }
        .result-label { font-weight: bold; color: #667eea; }
        .result-value { color: #333; margin-left: 5px; }
        .error { color: #f44336; font-weight: bold; }
        .success { color: #4caf50; font-weight: bold; }
        .example-btn { display: inline-block; padding: 8px 15px; margin: 5px; background: #e3f2fd; border: 1px solid #667eea; border-radius: 20px; cursor: pointer; font-size: 0.9em; transition: all 0.3s ease; }
        .example-btn:hover { background: #667eea; color: white; }
        .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .endpoint-card { background: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; transition: all 0.3s ease; }
        .endpoint-card:hover { box-shadow: 0 10px 20px rgba(0,0,0,0.1); transform: translateY(-5px); }
        .endpoint-method { display: inline-block; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 0.85em; margin-bottom: 10px; color: white; }
        .method-get { background: #4caf50; }
        .method-post { background: #2196f3; }
        .endpoint-path { font-family: 'Courier New', monospace; font-size: 0.95em; word-break: break-all; margin: 10px 0; }
        .endpoint-desc { color: #666; font-size: 0.95em; line-height: 1.6; }
        .footer { background: #f5f5f5; padding: 20px; text-align: center; color: #666; font-size: 0.9em; border-top: 1px solid #ddd; }
        .github-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #333; color: white; text-decoration: none; border-radius: 5px; transition: all 0.3s ease; }
        .github-link:hover { background: #555; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ADK Text Classification Agent</h1>
            <p>Powered by Google Gemini | Deployed on Cloud Run</p>
        </div>
        <div class="status-bar">
            <div class="status-item"><div class="status-label">Status</div><div class="status-value"><span class="status-badge">✓ Healthy</span></div></div>
            <div class="status-item"><div class="status-label">Version</div><div class="status-value">1.0.0</div></div>
            <div class="status-item"><div class="status-label">Model</div><div class="status-value">Gemini</div></div>
            <div class="status-item"><div class="status-label">Categories</div><div class="status-value">5</div></div>
        </div>
        <div class="content">
            <div class="section">
                <h2>📋 Overview</h2>
                <div class="info-grid">
                    <div class="info-card"><h3>What is This?</h3><p>An AI agent that classifies text into 5 categories using Google's Gemini model, deployed on Cloud Run.</p></div>
                    <div class="info-card"><h3>Categories</h3><p>NEWS • OPINION • TECHNICAL • MARKETING • EDUCATIONAL</p></div>
                    <div class="info-card"><h3>Technology</h3><p>Python • Flask • Google ADK • Gemini API • Cloud Run</p></div>
                </div>
            </div>
            <div class="section">
                <h2>🔌 API Endpoints</h2>
                <div class="endpoints">
                    <div class="endpoint-card"><span class="endpoint-method method-get">GET</span><div class="endpoint-path">/</div><div class="endpoint-desc">Interactive dashboard (this page)</div></div>
                    <div class="endpoint-card"><span class="endpoint-method method-get">GET</span><div class="endpoint-path">/agent/info</div><div class="endpoint-desc">Get agent info, categories, endpoints</div></div>
                    <div class="endpoint-card"><span class="endpoint-method method-post">POST</span><div class="endpoint-path">/classify</div><div class="endpoint-desc">Classify text into categories</div></div>
                </div>
            </div>
            <div class="section">
                <h2>🎯 Try It Now</h2>
                <div class="demo-section">
                    <div class="form-group">
                        <label for="textInput">Enter text to classify:</label>
                        <textarea id="textInput" placeholder="Example: Breaking news about a new discovery..."></textarea>
                    </div>
                    <div class="examples">
                        <strong>Quick Examples:</strong><br>
                        <span class="example-btn" onclick="loadExample('Breaking news: Scientists discover new renewable energy source')">📰 News</span>
                        <span class="example-btn" onclick="loadExample('In my opinion, this policy is misguided')">💬 Opinion</span>
                        <span class="example-btn" onclick="loadExample('The API uses HTTP POST with JSON payload and Bearer authentication')">⚙️ Technical</span>
                        <span class="example-btn" onclick="loadExample('Buy this product today! Limited 50% discount')">📢 Marketing</span>
                        <span class="example-btn" onclick="loadExample('Machine learning is a subset of artificial intelligence that learns from data')">📚 Educational</span>
                    </div>
                    <div class="button-group" style="margin-top: 20px;">
                        <button class="btn btn-primary" onclick="classifyText()" id="classifyBtn">Classify Text</button>
                        <button class="btn btn-secondary" onclick="clearDemo()">Clear</button>
                    </div>
                    <div class="response-box" id="responseBox"><h3>Results:</h3><div id="responseContent"></div></div>
                </div>
            </div>
            <div class="section" style="text-align: center;">
                <a href="https://github.com/shreyansh9026/adk-summarization-agent" class="github-link" target="_blank">🔗 View on GitHub</a>
            </div>
        </div>
        <div class="footer">
            <p>ADK Text Classification Agent v1.0.0 | Powered by Google Gemini | Google Cloud Run</p>
        </div>
    </div>
    <script>
        function loadExample(text) { document.getElementById('textInput').value = text; }
        function clearDemo() { document.getElementById('textInput').value = ''; document.getElementById('responseBox').classList.remove('show'); }
        async function classifyText() {
            const text = document.getElementById('textInput').value.trim();
            if (!text) { showResponse('<p class="error">❌ Please enter text</p>'); return; }
            const btn = document.getElementById('classifyBtn');
            btn.disabled = true; btn.innerHTML = '⏳ Processing...';
            try {
                const response = await fetch('/classify', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: text }) });
                const data = await response.json();
                if (data.success) {
                    const result = data.classification;
                    let html = `<div class="result-item"><div class="result-label">✓ Category:</div><div class="result-value"><strong>${result.category}</strong></div></div>
                        <div class="result-item"><div class="result-label">Confidence:</div><div class="result-value">${(result.confidence * 100).toFixed(1)}%</div></div>
                        <div class="result-item"><div class="result-label">Reasoning:</div><div class="result-value">${result.reasoning}</div></div>
                        <div class="result-item" style="margin-top: 15px;"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
                    showResponse(html);
                } else { showResponse(`<p class="error">❌ Error: ${data.error}</p>`); }
            } catch (error) { showResponse(`<p class="error">❌ Error: ${error.message}</p>`); }
            finally { btn.disabled = false; btn.innerHTML = 'Classify Text'; }
        }
        function showResponse(html) { document.getElementById('responseContent').innerHTML = html; document.getElementById('responseBox').classList.add('show'); }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def dashboard():
    """Serve interactive dashboard"""
    return render_template_string(DASHBOARD_HTML)


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
        "models_used": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "Interactive dashboard"
            },
            {
                "path": "/classify",
                "method": "POST",
                "description": "Classify text"
            },
            {
                "path": "/agent/info",
                "method": "GET",
                "description": "Get agent info"
            }
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
