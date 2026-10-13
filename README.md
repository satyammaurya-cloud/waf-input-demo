# Azure Application Gateway WAF --- Complete Study Notes

A hands-on guide to Azure Application Gateway, Web Application Firewall
(WAF), common web attacks, WAF modes, custom rules, rate limiting,
deployment, and troubleshooting.

## Table of Contents

1.  [Azure Application Gateway](#1-azure-application-gateway)
2.  [WAF Policy](#2-web-application-firewall-policy)
3.  [SQL Injection](#3-sql-injection-sqli)
4.  [Cross-Site Scripting](#4-cross-site-scripting-xss)
5.  [Detection vs Prevention](#5-detection-mode-vs-prevention-mode)
6.  [How WAF Works](#6-how-application-gateway-waf-works)
7.  [Custom Rules and Rate Limiting](#7-custom-rules-and-rate-limiting)
8.  [Azure Lab](#8-azure-app-service--application-gateway-waf-lab)
9.  [Logs and Troubleshooting](#9-waf-logs-and-troubleshooting)
10. [Best Practices](#10-best-practices)
11. [Interview Revision](#11-quick-interview-revision)

## 1. Azure Application Gateway

**Definition:** Azure Application Gateway is a Layer 7 (Application
Layer) web traffic load balancer that routes HTTP/HTTPS requests to
backend applications. It can integrate with a Web Application Firewall
(WAF).

**Simple explanation:** Think of Application Gateway as a gatekeeper
between users and your web application. It receives requests, applies
routing rules, and forwards allowed requests to the appropriate backend.

### Key features

-   Layer 7 load balancing for HTTP/HTTPS.
-   Host-based and path-based routing.
-   TLS termination and HTTPS communication to the backend.
-   WAF integration.
-   Health probes to monitor backend availability.
-   Cookie-based session affinity when required.
-   Autoscaling and zone redundancy, depending on configuration and SKU.

### Main components

  -----------------------------------------------------------------------
  Component                           Purpose
  ----------------------------------- -----------------------------------
  Frontend IP                         Entry point for client traffic

  Listener                            Listens on an IP, port, protocol,
                                      and optionally hostname

  Routing rule                        Connects a listener to a backend
                                      and defines routing behavior

  Backend pool                        Contains backend targets such as
                                      VMs, IP addresses, or App Services

  Backend settings                    Defines backend protocol, port,
                                      hostname, and timeout

  Health probe                        Checks whether backend targets are
                                      healthy

  WAF policy                          Applies web security rules to
                                      requests
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

Example test strings:

``` sql
' OR '1'='1
```

``` sql
' UNION SELECT NULL--
```

These are SQL-injection-like strings; they do not automatically exploit
a vulnerability.

### Potential impact

-   Unauthorized data access.
-   Authentication bypass in vulnerable applications.
-   Modification or deletion of database data.
-   Exposure of sensitive information.

### How WAF helps

1.  A client submits an HTTP request.
2.  WAF managed rules inspect relevant request components.
3.  If a request matches a blocking rule in Prevention mode, WAF can
    block it.
4.  Matching details may be recorded in diagnostic logs.

**Best practice:** Use parameterized SQL queries and secure input
handling. WAF is an additional layer, not a replacement for secure
application coding.

## 4. Cross-Site Scripting (XSS)

**Definition:** XSS is a vulnerability in which attacker-controlled
content is interpreted as executable script in another user's browser.

Example test strings:

``` html
<script>alert(1)</script>
```

``` html
<img src=x onerror=alert(1)>
```

Use these only in your authorized test environment.

### Potential impact

-   Unauthorized actions in a user's browser.
-   Theft of accessible session information.
-   Manipulation of page content.
-   Phishing or redirection.

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

  -----------------------------------------------------------------------
  Behavior                Detection               Prevention
  ----------------------- ----------------------- -----------------------
  Inspect requests        Yes                     Yes

  Log matching events     When configured         When configured

  Block matching          Normally no             Yes, when applicable
  managed-rule traffic                            

  Best use                Initial observation     Enforcing protection
  -----------------------------------------------------------------------

**Interview tip:** Start with Detection mode to understand traffic and
false positives. Move to Prevention mode after validation.

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

## 9. WAF Logs and Troubleshooting

### Enable diagnostics

1.  Open Application Gateway in Azure Portal.
2.  Navigate to **Monitoring → Diagnostic settings**.
3.  Send WAF logs to a supported destination, such as Log Analytics.
4.  Open the workspace and inspect records around the test time.

If the `AGWFirewallLogs` table is available, start with:

``` kusto
AGWFirewallLogs
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
```

Inspect the available fields to identify the test request, matched rule,
and action.

### Common HTTP responses

  -----------------------------------------------------------------------
  Response                            Possible explanation
  ----------------------------------- -----------------------------------
  `200 OK`                            Application responded; this does
                                      not prove WAF inspection

  `403 Forbidden`                     WAF or another layer may have
                                      denied the request

  `502 Bad Gateway`                   Backend connectivity, health probe,
                                      hostname, or TLS issue

  `404 Not Found`                     Requested application route may not
                                      exist
  -----------------------------------------------------------------------

### Troubleshooting checklist

-   Confirm the request passes through Application Gateway.
-   Check the WAF policy mode.
-   Confirm managed rules are enabled and applicable.
-   Check custom rule conditions and priorities.
-   Verify backend health and HTTPS settings.
-   Check WAF diagnostic logs.
-   Compare normal-request behavior with test-request behavior.

## 10. Best Practices

1.  Use managed WAF rules as a baseline for common web attacks.
2.  Start in Detection mode when learning or evaluating false positives.
3.  Use Prevention mode when the policy is ready to enforce protection.
4.  Keep backend TLS validation enabled and configure the correct
    hostname.
5.  Use secure application coding practices, including output escaping
    and parameterized database queries.
6.  Enable diagnostic logging and monitor blocked requests.
7.  Test rate limiting with controlled traffic and verify actual
    enforcement.
8.  Restrict direct backend access where appropriate so the intended
    gateway security boundary cannot be bypassed.
9.  Avoid overly broad custom rules that can block legitimate traffic.
10. Do not store credentials, tokens, or certificates in the Git
    repository.

## 11. Quick Interview Revision

  -----------------------------------------------------------------------
  Question                            Short answer
  ----------------------------------- -----------------------------------
  What is Application Gateway?        An Azure Layer 7 load balancer for
                                      HTTP/HTTPS traffic.

  What is WAF?                        A firewall that inspects web
                                      requests for suspicious patterns
                                      and attacks.

  What is a WAF policy?               A set of managed and custom rules
                                      applied to a supported scope.

  What is SQL injection?              An attack that manipulates SQL
                                      query behavior through crafted
                                      input.

  What is XSS?                        A vulnerability that allows
                                      untrusted content to execute as
                                      script in a browser.

  Detection vs Prevention?            Detection logs matching traffic;
                                      Prevention can block matching
                                      traffic.

  Managed vs Custom rules?            Managed rules provide standard
                                      protections; custom rules implement
                                      specific conditions and actions.

  What is rate limiting?              Restricting request frequency
                                      according to a configured threshold
                                      and duration.

  Why use backend HTTPS?              To encrypt traffic between
                                      Application Gateway and the
                                      backend.

  How do you verify a WAF block?      Correlate the test request with WAF
                                      logs and the rule action.
  -----------------------------------------------------------------------

## Conclusion

Azure Application Gateway provides Layer 7 routing, while its WAF
integration adds inspection and protection against common web attacks.
Managed rules, custom rules, rate limiting, correct backend
configuration, and diagnostic logs work together to protect and
troubleshoot web applications.

The key lesson from this lab is that a request returning `403` is not
sufficient proof of WAF protection. Confirm that traffic passed through
Application Gateway and that the WAF logs show the relevant rule and
blocking action.
