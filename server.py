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


# HTML Dashboard - Enhanced with better UX
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Text Classification Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 30px 80px rgba(0,0,0,0.3); overflow: hidden; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="white" opacity="0.1"/><circle cx="80" cy="80" r="3" fill="white" opacity="0.1"/></svg>');
            opacity: 0.5;
        }
        .header-content { position: relative; z-index: 1; }
        .header h1 { font-size: 3em; margin-bottom: 10px; animation: slideDown 0.6s ease; }
        .header p { font-size: 1.2em; opacity: 0.95; animation: slideUp 0.6s ease 0.2s both; }
        @keyframes slideDown { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0;
            background: linear-gradient(90deg, #f5f5f5 0%, #ffffff 100%);
            padding: 0;
        }
        .status-item {
            text-align: center;
            padding: 25px 20px;
            border-right: 1px solid #eee;
            transition: all 0.3s ease;
        }
        .status-item:last-child { border-right: none; }
        .status-item:hover { background: #f9f9f9; }
        .status-label { font-size: 0.85em; color: #999; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .status-value { font-size: 1.4em; font-weight: bold; color: #667eea; }
        .status-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 25px;
            font-size: 0.8em;
            font-weight: bold;
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        .content { padding: 50px 40px; }
        .section { margin-bottom: 50px; }
        .section h2 {
            color: #667eea;
            margin-bottom: 25px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .info-card {
            background: linear-gradient(135deg, #f9f9f9 0%, #ffffff 100%);
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .info-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.2);
        }
        .info-card h3 { color: #333; margin-bottom: 12px; font-size: 1.2em; }
        .info-card p { color: #666; font-size: 0.95em; line-height: 1.7; }
        .demo-section {
            background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
            padding: 35px;
            border-radius: 15px;
            border: 2px solid #667eea;
        }
        .form-group { margin-bottom: 25px; }
        .form-group label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #333;
            font-size: 1.05em;
        }
        .form-group textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 1em;
            min-height: 120px;
            transition: all 0.3s ease;
            resize: vertical;
        }
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .examples { margin: 20px 0; padding: 15px; background: rgba(255,255,255,0.8); border-radius: 8px; }
        .examples strong { display: block; margin-bottom: 12px; color: #333; }
        .button-group { display: flex; gap: 12px; flex-wrap: wrap; }
        .btn {
            padding: 13px 28px;
            border: none;
            border-radius: 8px;
            font-size: 0.95em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        .btn-secondary:hover {
            background: #f0f4ff;
        }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .response-box {
            background: white;
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 25px;
            margin-top: 25px;
            display: none;
            animation: fadeIn 0.3s ease;
        }
        .response-box.show { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        .response-box h3 { color: #667eea; margin-bottom: 15px; font-size: 1.3em; }
        .response-box pre {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.85em;
            max-height: 400px;
            border-left: 4px solid #667eea;
        }
        .result-item {
            margin: 15px 0;
            padding: 15px;
            background: linear-gradient(135deg, #f9f9f9 0%, #ffffff 100%);
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .confidence-bar {
            width: 100%;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            margin-top: 8px;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #45a049);
            border-radius: 3px;
            transition: width 0.5s ease;
        }
        .result-label { font-weight: 600; color: #667eea; }
        .result-value { color: #333; margin-left: 8px; }
        .error { color: #f44336; font-weight: 600; }
        .success { color: #4caf50; font-weight: 600; }
        .category-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-size: 1.1em;
        }
        .example-btn {
            display: inline-block;
            padding: 8px 16px;
            margin: 5px 5px 5px 0;
            background: white;
            border: 2px solid #667eea;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 500;
            color: #667eea;
            transition: all 0.3s ease;
        }
        .example-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        .endpoints {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .endpoint-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 22px;
            transition: all 0.3s ease;
        }
        .endpoint-card:hover {
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transform: translateY(-5px);
            border-color: #667eea;
        }
        .endpoint-method {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.75em;
            margin-bottom: 12px;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .method-get { background: linear-gradient(135deg, #4caf50, #45a049); }
        .method-post { background: linear-gradient(135deg, #2196f3, #1976d2); }
        .endpoint-path {
            font-family: 'Courier New', monospace;
            font-size: 1em;
            word-break: break-all;
            margin: 12px 0;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 6px;
            font-weight: 600;
        }
        .endpoint-desc { color: #666; font-size: 0.95em; line-height: 1.6; }
        .footer {
            background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #e0e0e0;
        }
        .link-group {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        .github-link, .docs-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        .github-link {
            background: #333;
            color: white;
        }
        .github-link:hover {
            background: #555;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .docs-link {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .docs-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        .copy-btn {
            padding: 4px 8px;
            margin-left: 8px;
            background: #e0e0e0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.2s ease;
        }
        .copy-btn:hover { background: #668eea; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>🤖 ADK Text Classification Agent</h1>
                <p>Powered by Google Gemini | Deployed on Google Cloud Run</p>
            </div>
        </div>
        <div class="status-bar">
            <div class="status-item"><div class="status-label">Status</div><div class="status-value"><span class="status-badge">✓ Healthy</span></div></div>
            <div class="status-item"><div class="status-label">API Status</div><div class="status-value" id="apiStatus"><span class="status-badge" style="background:#f39c12">Checking...</span></div></div>
            <div class="status-item"><div class="status-label">Version</div><div class="status-value">1.0.0</div></div>
            <div class="status-item"><div class="status-label">Model</div><div class="status-value">Gemini</div></div>
            <div class="status-item"><div class="status-label">Categories</div><div class="status-value">5</div></div>
        </div>
        <div class="content">
            <div class="section">
                <h2>📋 What is This?</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>🎯 Purpose</h3>
                        <p>An AI-powered text classification agent that automatically analyzes and categorizes text into 5 distinct categories using advanced machine learning.</p>
                    </div>
                    <div class="info-card">
                        <h3>📂 Categories</h3>
                        <p><strong>NEWS</strong> • <strong>OPINION</strong> • <strong>TECHNICAL</strong> • <strong>MARKETING</strong> • <strong>EDUCATIONAL</strong></p>
                    </div>
                    <div class="info-card">
                        <h3>⚙️ Technology</h3>
                        <p>Python • Flask • Google ADK • Gemini AI • Cloud Run • RESTful API</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🔌 API Endpoints</h2>
                <div class="endpoints">
                    <div class="endpoint-card">
                        <span class="endpoint-method method-get">GET</span>
                        <div class="endpoint-path">/</div>
                        <div class="endpoint-desc">📍 Interactive Dashboard - Try the agent with a web interface (this page)</div>
                    </div>
                    <div class="endpoint-card">
                        <span class="endpoint-method method-get">GET</span>
                        <div class="endpoint-path">/agent/info</div>
                        <div class="endpoint-desc">📊 Agent Metadata - Get categories, models, and available endpoints</div>
                    </div>
                    <div class="endpoint-card">
                        <span class="endpoint-method method-post">POST</span>
                        <div class="endpoint-path">/classify</div>
                        <div class="endpoint-desc">⭐ Classification - Send text to classify {"text": "your text here"}</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 Try It Now</h2>
                <div class="demo-section">
                    <div class="form-group">
                        <label for="textInput">✍️ Enter text to classify:</label>
                        <textarea id="textInput" placeholder="Example: Breaking news about a scientific discovery..."></textarea>
                    </div>
                    <div class="examples">
                        <strong>⚡ Quick Examples:</strong><br>
                        <span class="example-btn" onclick="loadExample('Breaking news: Scientists discover new renewable energy source cheaper than fossil fuels')">📰 News</span>
                        <span class="example-btn" onclick="loadExample('In my strong opinion, this policy is misguided and needs immediate reform from the government')">💬 Opinion</span>
                        <span class="example-btn" onclick="loadExample('REST APIs use HTTP POST with JSON payloads and Bearer token authentication headers')">⚙️ Technical</span>
                        <span class="example-btn" onclick="loadExample('Buy this amazing product today! Get 50% discount. Limited time offer ends soon!')">📢 Marketing</span>
                        <span class="example-btn" onclick="loadExample('Machine learning is a subset of artificial intelligence that learns patterns from data')">📚 Educational</span>
                    </div>
                    <div class="button-group" style="margin-top: 25px;">
                        <button class="btn btn-primary" id="classifyBtn">🚀 Classify Text</button>
                        <button class="btn btn-secondary" id="clearDemoBtn">🗑️ Clear</button>
                    </div>
                    <div class="response-box" id="responseBox">
                        <h3>📊 Classification Results:</h3>
                        <div id="responseContent"></div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📦 Batch Classification</h2>
                <div class="demo-section">
                    <div class="form-group">
                        <label for="batchInput">✍️ Enter texts (one per line):</label>
                        <textarea id="batchInput" placeholder="Line 1: First text&#10;Line 2: Second text&#10;Line 3: Third text"></textarea>
                    </div>
                    <div class="button-group" style="margin-top: 25px;">
                        <button class="btn btn-primary" id="batchBtn">🚀 Classify All</button>
                        <button class="btn btn-secondary" id="clearBatchBtn">🗑️ Clear</button>
                    </div>
                    <div class="response-box" id="batchResponseBox">
                        <h3>📊 Batch Results:</h3>
                        <div id="batchResponseContent"></div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📚 Categories Guide</h2>
                <div id="categoriesContainer" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;"></div>
                <div style="text-align: center; margin-top: 20px;">
                    <button class="btn btn-secondary" onclick="loadCategories()">📖 Load Category Info</button>
                </div>
            </div>

            <div class="section">
                <h2>📋 Classification History</h2>
                <div class="demo-section">
                    <p style="margin-bottom: 15px; color: #666;">Last 5 classifications (stored locally)</p>
                    <div id="historyContainer" style="max-height: 400px; overflow-y: auto;"></div>
                    <div style="margin-top: 15px; text-align: center;">
                        <button class="btn btn-secondary" onclick="clearHistory()">🗑️ Clear History</button>
                    </div>
                </div>
            </div>

            <div class="section" style="text-align: center;">
                <div class="link-group">
                    <a href="https://github.com/shreyansh9026/adk-summarization-agent" class="github-link" target="_blank">🔗 View on GitHub</a>
                    <a href="https://cloud.google.com/run" class="docs-link" target="_blank">📖 Cloud Run Docs</a>
                </div>
            </div>
        </div>
        <div class="footer">
            <p>✨ ADK Text Classification Agent v1.0.0 | Powered by Google Gemini | Google Cloud Run</p>
            <p style="margin-top: 10px; font-size: 0.85em;">Developer: Shreyansh Tripathi | Framework: Google Agent Development Kit</p>
        </div>
    </div>

    <script>
        const HISTORY_KEY = 'adk_classification_history';

        // Immediate diagnostic log
        console.log('=== ADK Dashboard Loading ===');
        console.log('Page URL:', window.location.href);
        console.log('Timestamp:', new Date().toISOString());

        // Initialize history on page load
        window.addEventListener('load', () => {
            console.log('=== Page Load Event Fired ===');
            updateHistoryDisplay();
            loadCategories();
            checkApiStatus();
            registerButtonHandlers();
            console.log('=== Initialization Complete ===');
        });

        function registerButtonHandlers() {
            console.log('=== Registering button handlers ===');
            const clsBtn = document.getElementById('classifyBtn');
            const clearBtn = document.getElementById('clearDemoBtn');
            const batchBtn = document.getElementById('batchBtn');
            const clearBatchBtn = document.getElementById('clearBatchBtn');

            console.log('classifyBtn found:', !!clsBtn);
            console.log('clearDemoBtn found:', !!clearBtn);
            console.log('batchBtn found:', !!batchBtn);
            console.log('clearBatchBtn found:', !!clearBatchBtn);

            if (clsBtn) {
                clsBtn.addEventListener('click', (e) => {
                    console.log('=== CLICKED: classifyBtn ===', e);
                    classifyText();
                });
            } else {
                console.error('ERROR: classifyBtn not found in DOM!');
            }
            if (clearBtn) {
                clearBtn.addEventListener('click', (e) => {
                    console.log('=== CLICKED: clearDemoBtn ===', e);
                    clearDemo();
                });
            } else {
                console.error('ERROR: clearDemoBtn not found in DOM!');
            }
            if (batchBtn) {
                batchBtn.addEventListener('click', (e) => {
                    console.log('=== CLICKED: batchBtn ===', e);
                    classifyBatch();
                });
            } else {
                console.error('ERROR: batchBtn not found in DOM!');
            }
            if (clearBatchBtn) {
                clearBatchBtn.addEventListener('click', (e) => {
                    console.log('=== CLICKED: clearBatchBtn ===', e);
                    clearBatch();
                });
            } else {
                console.error('ERROR: clearBatchBtn not found in DOM!');
            }
        }

        function clearDemo() {
            console.log('clearDemo called');
            document.getElementById('textInput').value = '';
            document.getElementById('responseBox').classList.remove('show');
        }

        function clearBatch() {
            console.log('clearBatch called');
            document.getElementById('batchInput').value = '';
            document.getElementById('batchResponseBox').classList.remove('show');
        }

        window.onerror = function(message, source, lineno, colno, error) {
            console.error('=== GLOBAL JS ERROR ===', {message, source, lineno, colno, error});
            showResponse(`<p class="error">❌ JavaScript error: ${message} at ${source}:${lineno}</p>`);
            return false;
        };

        async function checkApiStatus() {
            console.log('=== Checking API Status ===');
            const statusEl = document.getElementById('apiStatus');
            try {
                const response = await fetch('/agent/info');
                console.log('API /agent/info response:', response.status, response.statusText);
                if (response.ok) {
                    statusEl.innerHTML = '<span class="status-badge">✓ Online</span>';
                    console.log('✓ API is Online');
                } else {
                    statusEl.innerHTML = '<span class="status-badge" style="background:#f44336">✗ Unavailable</span>';
                    const errorText = await response.text();
                    console.error('✗ API returned error:', response.status, errorText);
                    showResponse(`<p class="error">❌ API check failed: ${response.status} ${response.statusText}<br>Response: ${errorText}</p>`);
                }
            } catch (error) {
                console.error('✗ API Connection Error:', error);
                statusEl.innerHTML = '<span class="status-badge" style="background:#f44336">✗ Offline</span>';
                showResponse(`<p class="error">❌ Could not reach API: ${error.message}</p>`);
            }
        }

        function loadExample(text) {
            console.log('loadExample called with:', text.substring(0, 50));
            document.getElementById('textInput').value = text;
            document.getElementById('textInput').focus();
        }

        function saveToHistory(text, result) {
            let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
            history.unshift({
                timestamp: new Date().toLocaleString(),
                text: text.substring(0, 50) + (text.length > 50 ? '...' : ''),
                category: result.classification?.category,
                confidence: result.classification?.confidence
            });
            // Keep only last 5
            history = history.slice(0, 5);
            localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
            updateHistoryDisplay();
        }

        function updateHistoryDisplay() {
            const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
            const container = document.getElementById('historyContainer');

            if (history.length === 0) {
                container.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">No classifications yet</p>';
                return;
            }

            container.innerHTML = history.map(item => `
                <div class="result-item">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <div class="result-label">${item.category}</div>
                            <div style="font-size: 0.85em; color: #999;">${item.text}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #667eea; font-weight: 600;">${(item.confidence * 100).toFixed(0)}%</div>
                            <div style="font-size: 0.8em; color: #999;">${item.timestamp}</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function clearHistory() {
            if (confirm('Clear all history?')) {
                localStorage.removeItem(HISTORY_KEY);
                updateHistoryDisplay();
            }
        }

        async function classifyText() {
            console.log('=== classifyText() CALLED ===');
            const text = document.getElementById('textInput').value.trim();
            console.log('Input text:', text.substring(0, 50));
            if (!text) {
                console.warn('Input text is empty');
                showResponse('<p class="error">❌ Please enter text to classify</p>');
                return;
            }
            const btn = document.getElementById('classifyBtn');
            btn.disabled = true;
            btn.innerHTML = '⏳ Processing...';
            try {
                console.log('Sending POST to /classify with text:', text.substring(0, 50));
                const response = await fetch('/classify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                console.log('Response status:', response.status, response.statusText);
                const data = await response.json();
                console.log('Response data:', data);
                if (data.success) {
                    const result = data.classification;
                    const percentage = (result.confidence * 100).toFixed(1);
                    saveToHistory(text, data);
                    let html = `
                        <div class="result-item">
                            <div class="result-label">✓ Category:</div>
                            <div class="result-value"><span class="category-badge">${result.category}</span></div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">📊 Confidence: ${percentage}%</div>
                            <div class="confidence-bar"><div class="confidence-fill" style="width: ${percentage}%"></div></div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">💬 Reasoning:</div>
                            <div class="result-value">${result.reasoning}</div>
                        </div>
                        <div class="result-item" style="margin-top: 20px;">
                            <div class="result-label">📋 Full Response:</div>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                    showResponse(html);
                    console.log('✓ Classification successful');
                } else {
                    console.error('API returned error:', data.error);
                    showResponse(`<p class="error">❌ Error: ${data.error}</p>`);
                }
            } catch (error) {
                console.error('❌ Exception in classifyText:', error);
                showResponse(`<p class="error">❌ Error: ${error.message}</p>`);
            }
            finally {
                btn.disabled = false;
                btn.innerHTML = '🚀 Classify Text';
            }
        }

        async function classifyBatch() {
            console.log('=== classifyBatch() CALLED ===');
            const input = document.getElementById('batchInput').value.trim();
            if (!input) {
                console.warn('Batch input is empty');
                showBatchResponse('<p class="error">❌ Please enter texts to classify</p>');
                return;
            }

            const texts = input.split('\n').filter(t => t.trim()).map(t => t.trim());
            if (texts.length === 0) {
                console.warn('No valid texts found after splitting');
                showBatchResponse('<p class="error">❌ No valid texts found</p>');
                return;
            }

            console.log('Batch texts to classify:', texts.length);
            const btn = document.getElementById('batchBtn');
            btn.disabled = true;
            btn.innerHTML = `⏳ Processing ${texts.length} texts...`;

            try {
                console.log('Sending POST to /batch/classify with', texts.length, 'texts');
                const response = await fetch('/batch/classify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ texts: texts })
                });
                console.log('Batch response status:', response.status);
                const data = await response.json();
                console.log('Batch response data:', data);

                if (data.success) {
                    const stats = data.statistics;
                    const categoryBars = Object.entries(stats.categories)
                        .map(([cat, count]) => `<div class="result-item"><strong>${cat}:</strong> ${count}</div>`)
                        .join('');

                    let html = `
                        <div class="result-item">
                            <div class="result-label">📊 Statistics:</div>
                            <div style="margin-top: 10px;">
                                <div>✓ Total: ${stats.total}</div>
                                <div>✓ Successful: ${stats.successful}</div>
                                <div>✗ Failed: ${stats.failed}</div>
                            </div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">📈 Category Distribution:</div>
                            <div style="margin-top: 10px;">${categoryBars}</div>
                        </div>
                        <div class="result-item" style="margin-top: 20px;">
                            <div class="result-label">📋 Full Response:</div>
                            <pre style="max-height: 300px;">${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                    showBatchResponse(html);

                    // Save batch results to history
                    data.results.forEach(r => {
                        if (r.success) saveToHistory(r.text, r);
                    });
                    console.log('✓ Batch classification successful');
                } else {
                    console.error('API batch error:', data.error);
                    showBatchResponse(`<p class="error">❌ Error: ${data.error}</p>`);
                }
            } catch (error) {
                console.error('❌ Exception in classifyBatch:', error);
                showBatchResponse(`<p class="error">❌ Error: ${error.message}</p>`);
            }
            finally {
                btn.disabled = false;
                btn.innerHTML = '🚀 Classify All';
            }
        }

        async function loadCategories() {
            console.log('=== loadCategories() CALLED ===');
            try {
                const response = await fetch('/categories');
                const data = await response.json();

                if (data.success) {
                    const container = document.getElementById('categoriesContainer');
                    container.innerHTML = data.categories.map(cat => `
                        <div class="info-card">
                            <h3>${cat}</h3>
                            <p>${data.descriptions[cat] || 'Category information'}</p>
                        </div>
                    `).join('');
                    console.log('✓ Categories loaded');
                } else {
                    console.error('Categories load failed:', data.error);
                }
            } catch (error) {
                console.error('❌ Failed to load categories:', error);
            }
        }

        function showResponse(html) {
            console.log('showResponse called');
            document.getElementById('responseContent').innerHTML = html;
            document.getElementById('responseBox').classList.add('show');
            document.getElementById('responseBox').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        function showBatchResponse(html) {
            console.log('showBatchResponse called');
            document.getElementById('batchResponseContent').innerHTML = html;
            document.getElementById('batchResponseBox').classList.add('show');
            document.getElementById('batchResponseBox').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
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


@app.route("/batch/classify", methods=["POST"])
def batch_classify():
    """
    Batch classify multiple texts

    Expected request body:
    {
        "texts": ["text1", "text2", "text3"]
    }
    """
    if not app.agent:
        return jsonify({
            "success": False,
            "error": "Agent not initialized"
        }), 503

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

    texts = data.get("texts", [])
    if not texts or not isinstance(texts, list):
        return jsonify({
            "success": False,
            "error": "Missing or invalid 'texts' field. Expected list of strings."
        }), 400

    result = app.agent.batch_classify(texts)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/categories", methods=["GET"])
def get_categories():
    """Get all available categories with descriptions"""
    if not app.agent:
        return jsonify({
            "success": False,
            "error": "Agent not initialized"
        }), 503

    descriptions = app.agent.get_category_descriptions()
    return jsonify({
        "success": True,
        "categories": app.agent.categories,
        "descriptions": descriptions
    }), 200


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
                "description": "Classify single text"
            },
            {
                "path": "/batch/classify",
                "method": "POST",
                "description": "Classify multiple texts in batch"
            },
            {
                "path": "/categories",
                "method": "GET",
                "description": "Get category information"
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
