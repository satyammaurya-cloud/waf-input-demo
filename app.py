from flask import Flask, request, render_template_string

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WAF Input Demo</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; }
    input, textarea, button { display: block; width: 100%; box-sizing: border-box; padding: 10px; margin: 8px 0 18px; font: inherit; }
    .note { background: #f2f4f7; padding: 12px; border-radius: 6px; }
    .result { border: 1px solid #bbb; padding: 12px; border-radius: 6px; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; }
  </style>
</head>
<body>
  <h1>WAF Input Testing Demo</h1>
  <p class="note">Submit normal text or test strings. Input is displayed as text; this demo does not execute JavaScript or run SQL.</p>
  <form method="post" action="/submit">
    <label for="name">Name</label>
    <input id="name" name="name" maxlength="80" required>
    <label for="message">Message / test input</label>
    <textarea id="message" name="message" rows="4" maxlength="1000" required></textarea>
    <button type="submit">Submit</button>
  </form>
  {% if result %}
    <h2>Request reached the application</h2>
    <div class="result">
      <p><strong>Name:</strong> {{ result.name }}</p>
      <p><strong>Input received:</strong></p>
      <pre>{{ result.message }}</pre>
    </div>
  {% endif %}
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(PAGE, result=None)

@app.post("/submit")
def submit():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not message:
        return "Name and message are required.", 400
    if len(name) > 80 or len(message) > 1000:
        return "Input too long.", 413

    # Jinja auto-escapes template values, so input is shown as text.
    # No database is connected and no submitted input is executed.
    return render_template_string(PAGE, result={"name": name, "message": message})

@app.get("/health"):
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
