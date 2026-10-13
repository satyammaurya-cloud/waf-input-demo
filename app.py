import os
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

@app.route("/")
def home():
    return """
    <h1>WAF Input Testing Demo</h1>
    <p>Test normal input, XSS-like strings, and SQL injection-like strings.</p>
    <p><a href="/waf-test">Open WAF Test Form</a></p>
    """

WAF_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>WAF Input Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            background: #101218;
            color: white;
        }
        input, textarea, button {
            width: 100%;
            box-sizing: border-box;
            padding: 12px;
            margin: 8px 0 18px;
        }
        .result {
            background: #20232c;
            padding: 15px;
            overflow-wrap: anywhere;
        }
    </style>
</head>
<body>
    <h1>WAF Input Testing Lab</h1>
    <p>Submit input and observe whether the WAF allows or blocks the request.</p>

    <form method="POST" action="/waf-test">
        <label>Name</label>
        <input name="name" maxlength="80" required>

        <label>Message / Test Input</label>
        <textarea name="message" rows="4" maxlength="1000"
                  required></textarea>

        <button type="submit">Submit</button>
    </form>

    {% if submitted %}
        <div class="result">
            <h2>Request reached the application</h2>
            <p><strong>Name:</strong> {{ name }}</p>
            <p><strong>Input received:</strong></p>
            <pre>{{ message }}</pre>
        </div>
    {% endif %}

    <h3>Suggested test inputs</h3>
    <ul>
        <li>Normal: hello team</li>
        <li>XSS-like: &lt;script&gt;alert(1)&lt;/script&gt;</li>
        <li>SQL-like: ' OR '1'='1</li>
    </ul>
    <p>Input is displayed as text. No SQL database is connected.</p>
</body>
</html>
"""

@app.route("/waf-test", methods=["GET", "POST"])
def waf_test():
    name = ""
    message = ""
    submitted = False

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not message:
            return "Name and message are required.", 400

        if len(name) > 80 or len(message) > 1000:
            return "Input too long.", 413

        submitted = True

    # Jinja auto-escapes values; input is not executed as HTML or JavaScript.
    return render_template_string(
        WAF_PAGE,
        name=name,
        message=message,
        submitted=submitted
    )

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
