# WAF Input Demo — Azure App Service

Simple Flask form for an Azure Application Gateway WAF demonstration. No Kubernetes, VM, or database required.

## App files
- `app.py`: Flask application.
- `application.py`: compatibility entry point for the App Service startup command seen in the supplied logs (`gunicorn application:app`).
- `requirements.txt`: Flask and Gunicorn dependencies.

## Deploy from GitHub
1. Push the contents of this folder to the root of your GitHub repository.
2. In Azure App Service > Deployment Center, connect that repository and the `main` branch, and choose GitHub Actions as the build provider.
3. If GitHub Actions is already configured, pushing to `main` should trigger deployment. Watch the Actions tab and App Service Deployment Center logs.
4. Open `https://<APP_SERVICE_NAME>.azurewebsites.net/` and test `/health`.

If you prefer the included workflow, add these GitHub repository secrets first:
- `AZURE_WEBAPP_NAME`: your App Service name.
- `AZURE_WEBAPP_PUBLISH_PROFILE`: publish profile XML downloaded from your App Service's Get publish profile option.

Then commit and push. The workflow deploys on each push to `main`.

## WAF demo inputs
- Normal: `hello team`
- XSS-looking text: `<script>alert(1)</script>`
- SQL-injection-looking text: `' OR '1'='1`

The app renders input as text and has no database, so these strings are not executed. To test Azure WAF, route requests through the Application Gateway URL; testing the App Service URL directly bypasses that gateway. Detection mode generally logs matching requests; Prevention mode can block requests that match configured rules. Actual outcomes depend on the WAF policy and rule set.

This is a safe demonstration app, not a deliberately vulnerable app.
