from flask import Flask, request, render_template_string
import os
import json
from dotenv import load_dotenv
from perplexity import Perplexity

# Load environment variables
load_dotenv()
api_key = os.getenv('PERPLEXITY_API_KEY')

app = Flask(__name__)

# Initialize Perplexity Client
client = None
if api_key:
    client = Perplexity(api_key=api_key)
else:
    print("Warning: PERPLEXITY_API_KEY not found in .env")

# HTML Template with Loading Animation
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TruthLense AI Detector</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 20px; background-color: #1a1a2e; color: #e0e0e0; }
        .container { background: #16213e; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid #0f3460; }
        h1 { color: #fff; text-align: center; margin-bottom: 30px; font-weight: 300; letter-spacing: 2px; }
        h1 span { color: #e94560; font-weight: 600; }
        textarea { width: 100%; height: 120px; padding: 15px; margin: 10px 0; border: 2px solid #0f3460; border-radius: 8px; font-size: 16px; background-color: #0f3460; color: white; resize: vertical; box-sizing: border-box; }
        textarea:focus { outline: none; border-color: #e94560; }
        button { background-color: #e94560; color: white; padding: 15px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; width: 100%; transition: background 0.3s; font-weight: 600; }
        button:hover { background-color: #c12c45; }
        
        .result-box { margin-top: 30px; animation: fadeIn 0.5s; }
        .verdict-badge { display: inline-block; padding: 8px 16px; border-radius: 50px; font-weight: bold; text-transform: uppercase; font-size: 1.2em; margin-bottom: 15px; }
        .verdict-TRUE { background-color: #28a745; color: white; box-shadow: 0 0 10px rgba(40, 167, 69, 0.5); }
        .verdict-FALSE { background-color: #dc3545; color: white; box-shadow: 0 0 10px rgba(220, 53, 69, 0.5); }
        .verdict-MIXED { background-color: #ffc107; color: #1a1a2e; box-shadow: 0 0 10px rgba(255, 193, 7, 0.5); }
        .verdict-UNVERIFIABLE { background-color: #6c757d; color: white; }
        
        .card { background: #0f3460; border-radius: 8px; padding: 20px; margin-bottom: 20px; border-left: 4px solid #e94560; }
        .card h3 { margin-top: 0; color: #e94560; font-size: 1.1em; text-transform: uppercase; letter-spacing: 1px; }
        .card p { line-height: 1.6; color: #ccc; margin-bottom: 0; }
        
        .meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .meta-item { background: #1a1a2e; padding: 10px 15px; border-radius: 6px; border: 1px solid #2a2a40; }
        .meta-label { font-size: 0.8em; color: #888; text-transform: uppercase; display: block; margin-bottom: 5px; }
        .meta-value { font-weight: bold; color: #fff; }
        
        .sources-list { list-style: none; padding: 0; margin: 0; }
        .sources-list li { margin-bottom: 8px; padding-left: 20px; position: relative; }
        .sources-list li:before { content: "•"; color: #e94560; position: absolute; left: 0; }
        
        /* Loading Animation */
        .loader-container { display: none; text-align: center; margin-top: 40px; }
        .loader { display: inline-block; width: 50px; height: 50px; border: 3px solid rgba(255,255,255,.1); border-radius: 50%; border-top-color: #e94560; animation: spin 1s ease-in-out infinite; }
        .loading-text { margin-top: 15px; color: #888; font-size: 0.9em; letter-spacing: 1px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    <script>
        function showLoader() {
            document.getElementById('loader-container').style.display = 'block';
            var resultBox = document.getElementById('result-box');
            if (resultBox) {
                resultBox.style.display = 'none';
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>TruthLense <span>AI</span></h1>
        <p style="text-align: center; color: #888; margin-bottom: 30px;">Universal Fact-Checking Assistant</p>
        
        <form method="post" onsubmit="showLoader()">
            <textarea name="text" placeholder="Enter a claim to verify (e.g., historical events, scientific facts, news)..." required>{{ text }}</textarea>
            <button type="submit">Verify Claim</button>
        </form>

        <div id="loader-container" class="loader-container">
            <div class="loader"></div>
            <p class="loading-text">SEARCHING HISTORICAL ARCHIVES & DATABASES...</p>
        </div>

        {% if result %}
            <div id="result-box" class="result-box">
                <div style="text-align: center; margin-bottom: 30px;">
                    <span class="verdict-badge verdict-{{ result.verdict }}">{{ result.verdict }}</span>
                    <div style="color: #888; margin-top: 10px;">Confidence Score: <span style="color: #fff;">{{ result.confidence }}</span></div>
                </div>

                <div class="meta-grid">
                    <div class="meta-item">
                        <span class="meta-label">First Verified</span>
                        <span class="meta-value">{{ result.first_verified }}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Last Updated</span>
                        <span class="meta-value">{{ result.last_updated }}</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Explanation</h3>
                    <p>{{ result.explanation }}</p>
                </div>

                <div class="card">
                    <h3>Historical Context</h3>
                    <p>{{ result.historical_context }}</p>
                </div>

                <div class="card" style="border-left-color: #4a4a6a;">
                    <h3>Sources</h3>
                    <ul class="sources-list">
                        {% for source in result.sources %}
                            <li>{{ source }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        {% endif %}
        
        {% if error %}
            <div class="result-box" style="color: #dc3545; text-align: center; padding: 20px;">
                {{ error }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    text = ""

    if request.method == 'POST':
        text = request.form['text']
        if client:
            try:
                prompt = (
                    "Act as a universal fact-checking assistant with access to historical records dating back to the 1800s and 1900s. "
                    "For the following statement, provide a verdict (TRUE, FALSE, MIXED, UNVERIFIABLE), confidence score (0-100%), "
                    "and a concise but thorough explanation including relevant historical evidence, scientific findings, and authoritative references. "
                    "Crucially, investigate historical context to see if this claim has roots in the 19th or 20th centuries. "
                    "List sources and indicate the first time the claim was verified or disproven in history, plus the last update.\n\n"
                    f"Statement: '{text}'\n\n"
                    "Respond ONLY in valid JSON format with the following keys: "
                    "'verdict' (enum: TRUE, FALSE, MIXED, UNVERIFIABLE), "
                    "'confidence' (string, e.g. '95%'), "
                    "'explanation' (string), "
                    "'historical_context' (string), "
                    "'first_verified' (string, date or era), "
                    "'last_updated' (string, date or era), "
                    "'sources' (list of strings)."
                )
                
                response = client.chat.completions.create(
                    model="sonar-pro",
                    messages=[
                        {"role": "system", "content": "You are a rigorous fact-checking AI that outputs only valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                content = response.choices[0].message.content
                # Clean up code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                result = json.loads(content.strip())
                
            except json.JSONDecodeError:
                error = "Error: Failed to parse AI response. Please try again."
            except Exception as e:
                error = f"Error calling AI API: {str(e)}"
        else:
            error = "Error: Perplexity API Key not configured."

    return render_template_string(HTML_TEMPLATE, result=result, error=error, text=text)

if __name__ == '__main__':
    print("Starting TruthLense AI App...")
    print("Go to http://127.0.0.1:5000 in your browser.")
    app.run(debug=True, port=5000)
