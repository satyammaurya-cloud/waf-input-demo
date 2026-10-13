# Azure Application Gateway WAF 

## 1. Azure Application Gateway

**Definition:** Azure Application Gateway is a Layer 7 (Application
Layer) web traffic load balancer that routes HTTP/HTTPS requests to
backend applications. It can integrate with a Web Application Firewall
(WAF).



<img width="820" height="342" alt="image" src="https://github.com/user-attachments/assets/d0372d08-dbe9-45e3-b645-ecadd4ad5ab6" />

  -----------------------------------------------------------------------

**Interview answer:** Application Gateway is an Azure Layer 7 load
balancer for HTTP/HTTPS traffic. With WAF enabled, it can inspect
requests and help protect applications against common web attacks.

## 2. Web Application Firewall Policy

**Definition:** A WAF policy is a collection of security settings and
rules used to inspect HTTP requests and decide how matching traffic
should be handled.

**Simple explanation:** If Application Gateway is the gatekeeper, the
WAF policy is the security checklist it follows.

### Types of WAF rules

**Managed rules:** Maintained by Microsoft or based on supported OWASP
Core Rule Set versions. They help detect common attacks such as SQL
injection, XSS, and protocol violations.

**Custom rules:** Configured by administrators for specific
requirements, such as IP filtering, request matching, or rate limiting.

### Common policy settings

-   Detection or Prevention mode.
-   Managed rule sets and rule exclusions.
-   Custom rules, priorities, conditions, and actions.
-   Request body inspection and size-related settings.
-   Diagnostic logging.

A WAF policy must be associated with the relevant Application Gateway,
listener, or supported scope.

## 3. SQL Injection (SQLi)

**Definition:** SQL injection is an attack in which specially crafted
input changes the intended behavior of an application's SQL query.

``` sql
' OR '1'='1
```

## 4. Cross-Site Scripting (XSS)

**Definition:** XSS is a vulnerability in which attacker-controlled
content is interpreted as executable script in another user's browser.


``` html
<script>alert(1)</script>
```

``` html
<img src=x onerror=alert(1)>
```

### How WAF helps

WAF managed rules can inspect request content for common XSS patterns.
Matching traffic may be logged or blocked depending on the rule and
policy mode.

**Best practice:** Escape untrusted output, use context-aware encoding,
and apply an appropriate Content Security Policy where suitable.

In a Flask demo, if `<script>alert(1)</script>` appears as literal text
and does not execute, that is a good sign that output is being escaped.
It does **not**, by itself, prove that Azure WAF inspected or blocked
the request.

## 5. Detection Mode vs Prevention Mode

**Detection mode** - Evaluates requests against enabled WAF rules. -
Logs matching events when logging is configured. - Normally does not
block requests solely because they match those rules. - Useful for
observing traffic and identifying false positives.

**Prevention mode** - Evaluates requests against enabled WAF rules. -
Blocks requests that match applicable blocking rules. - Records relevant
events when diagnostics are configured. - Useful when protection is
ready to enforce.

## 6. How Application Gateway WAF Works

1.  **Client request:** A browser sends an HTTP/HTTPS request.
2.  **Listener:** Application Gateway receives traffic on the configured
    frontend.
3.  **WAF evaluation:** Managed and applicable custom rules inspect the
    request.
4.  **Decision:** The request is allowed to continue or blocked
    according to the policy and rule actions.
5.  **Backend:** Forwarded requests reach the application.

The exact behavior depends on the WAF policy, rule types, exclusions,
and request configuration.

## 7. Custom Rules and Rate Limiting

Custom rules let administrators define specific traffic conditions and
actions.

-   **Match rule:** Evaluates request attributes and performs an action
    when conditions match.
-   **Rate-limit rule:** Limits request frequency according to the
    configured threshold, duration, grouping, and conditions.

### Example: 10 requests per minute

  Setting            Example
  ------------------ -----------------------------------------
  Rule action        Deny traffic
  Priority           100, if available
  Rule type          Rate limit
  Duration           1 minute
  Threshold          10 requests
  Group traffic by   Client address
  Condition          Match the intended application requests

The condition must match the traffic you want to limit. Choose an
appropriate URI or other supported request condition that matches the
relevant paths.

**Important:** Do not use `0.0.0.0` as a catch-all client IP condition.
It is not a reliable way to match all client addresses.

### Test rate limiting

``` bash
for i in $(seq 1 15); do
  curl -sS -o /dev/null \
    -w "Request $i: HTTP %{http_code}\n" \
    "http://YOUR-APPLICATION-GATEWAY-IP/"
done
```

Replace `YOUR-APPLICATION-GATEWAY-IP` with your frontend IP. For HTTPS,
use the appropriate HTTPS URL and hostname.

This sends 15 requests but does not guarantee that requests after the
tenth will be blocked. The result depends on the condition, policy
configuration, and rate-limit enforcement. Confirm triggering in WAF
logs.

## 8. Azure App Service + Application Gateway WAF Lab

This lab uses a Flask `waf-input-demo` application hosted on Azure App
Service.

### Step 1: Deploy the Flask application

``` text
waf-input-demo/
├── app.py
├── requirements.txt
└── README.md
```

Example `requirements.txt`:

``` text
flask==3.0.3
gunicorn==22.0.0
```

Keep dependency versions consistent with the application deployment.
Deploy the repository to App Service and verify the app works before
routing traffic through WAF.

### Step 2: Configure the backend pool

1.  Open Application Gateway.
2.  Navigate to **Backend pools**.
3.  Add the App Service hostname, for example `bnbb.azurewebsites.net`.
4.  Replace the example with your actual hostname.

### Step 3: Configure backend settings

  Setting                  Value
  ------------------------ -----------------------------
  Backend protocol         HTTPS
  Backend port             443
  Certificate validation   Complete validation
  Certificate issuer       Public CA
  Hostname override        Actual App Service hostname
  Request timeout          20 seconds, adjustable

Ensure hostname validation and TLS/SNI use the correct App Service
hostname.

### Step 4: Configure listener and routing

1.  Configure a frontend IP and listener.
2.  Create a routing rule.
3.  Associate the rule with the backend pool.
4.  Associate the backend settings.
5.  Verify **Backend health** reports Healthy.

### Step 5: Attach the WAF policy

1.  Open the WAF policy.
2.  Enable the supported managed rule set.
3.  Start with Detection mode if you need to observe traffic.
4.  Associate the policy with the intended gateway or listener.
5.  Configure diagnostic logging.

### Step 6: Test requests

Use the Application Gateway frontend endpoint, not the direct App
Service URL: - Submit normal text. - Submit the XSS-like string. -
Submit the SQL-injection-like string. - Send repeated requests to test
rate limiting.

### Step 7: Validate results

Check HTTP responses and WAF logs. Confirm the matched rule, action,
timestamp, and request details before concluding that WAF blocked a
request.

-----------------------------------------------------------------------

## Conclusion

<img width="678" height="706" alt="image" src="https://github.com/user-attachments/assets/de284ec1-d944-47ac-a063-0c6c3d407e55" />

<img width="1172" height="550" alt="image" src="https://github.com/user-attachments/assets/bc0dcf86-5795-404a-bf0d-d04c9acd48e4" />


<img width="1885" height="716" alt="image" src="https://github.com/user-attachments/assets/b600b04e-2a20-4345-be19-9c034e78c21e" />

<img width="1823" height="774" alt="image" src="https://github.com/user-attachments/assets/8cab8106-322a-4f79-8fc0-826c79046523" />

