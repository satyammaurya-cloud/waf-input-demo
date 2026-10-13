# Simple WAF Input Demo (No Kubernetes)

A small Python Flask form for demonstrating Azure Application Gateway WAF behavior. It has no database and does not execute submitted content.

## Run on Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8080

## Test strings

Submit these one at a time:

- Normal: `hello team`
- XSS-looking string: `<script>alert(1)</script>`
- SQL-injection-looking string: `' OR '1'='1`

This app displays values as text and never runs SQL. For an Azure WAF demonstration, host it on a reachable VM/web server behind Application Gateway and submit requests through the gateway's public URL. Testing localhost alone does not test Azure WAF.

## Explain to the audience

- **WAF enabled + Prevention mode:** requests matching configured WAF rules can be blocked before they reach the app.
- **WAF enabled + Detection mode:** matching requests are generally logged but allowed through.
- **WAF disabled:** the request is not inspected by that WAF policy, but other network controls may still block it.
- **Important:** this app remains safe because it renders input as text and has no SQL database. A WAF is an extra layer, not a replacement for secure coding.
- Actual blocking depends on the policy, managed rule set, exclusions, and request. Not every suspicious-looking string is guaranteed to be blocked.

Use only your own lab and show the WAF logs in Azure Monitor/Log Analytics alongside the browser result.
