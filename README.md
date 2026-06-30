# AI Security Lab — AWS

This is a hands-on, four-phase AI security lab built on AWS to demonstrate real-world 
attack, hardening, and monitoring techniques for AI/ML systems.

Built as a portfolio project while studying for the CompTIA SecAI+ (CY0-001) 
certification, mapped to OWASP Top 10 for LLMs, MITRE ATLAS, and NIST AI RMF.

---

## Architecture
User (curl/Postman)
│
▼
API Gateway (REST API)
│
▼
Lambda (Python — RAG handler)
│
├──► S3 (knowledge base documents)
└──► Amazon Bedrock (Claude 3 Haiku)

**AWS Accounts:** Two-account AWS Organizations setup
- `Sandbox`  — application workload
- `Security` — monitoring, alerting, Security Hub

**Region:** us-east-1  
**IaC:** Terraform 1.15.7

---

## The Four Phases

### Phase 1 — Deploy an Insecure system ✅ (In Progress)
Deploy a functional RAG application with intentional security gaps:
- S3 bucket with no explicit encryption enforcement or public access block
- IAM Lambda execution role with overpermissive `Resource: *` policies
- API Gateway endpoint with no authentication or throttling
- Lambda handler with no input validation or output sanitization
- No CloudTrail logging, no Bedrock Guardrails

**Goal:** Produce a realistic "rushed MVP" that mirrors common real-world 
AI deployment mistakes. Every gap is documented in `threat-model/threat_model.md`.

### Phase 2 — Red Team (Planned)
Attack the Phase 1 deployment using documented techniques:
- Direct and indirect prompt injection via API and poisoned S3 documents
- Attempt system prompt extraction
- Test for sensitive information disclosure
- Model evasion and jailbreak attempts
- API abuse / model stealing reconnaissance

All findings documented in `red-team/findings.md` with OWASP LLM Top 10 
and MITRE ATLAS classifications.

### Phase 3 — Harden (Planned)
Apply security controls layer by layer:
- IAM least privilege (scoped ARN-specific policies)
- Bedrock Guardrails (content filtering, PII redaction, topic denial)
- API Gateway authentication (Cognito authorizer + usage plan throttling)
- S3 encryption enforcement + bucket policy + block public access
- Lambda input validation + prompt firewall + output sanitization
- AWS WAF on API Gateway

### Phase 4 — Monitor & Detect (Planned)
Build AI-specific detection and response:
- CloudTrail cross-account logging to Security account
- CloudWatch metric filters for anomalous Bedrock invocation patterns
- Alerts for high-volume requests (model stealing signal)
- Alerts for prompt length anomalies (injection signal)
- Security Hub integration with custom AI findings
- AI Incident Response Runbook (`runbooks/ai_incident_response.md`)

---

## Repository Structure
ai-security-lab-aws/
├── terraform/
│   ├── sandbox/          # Phase 1 + 3 application infrastructure
│   └── security/         # Phase 4 monitoring infrastructure
├── lambda/
│   ├── handler.py        # RAG application logic
│   └── sample-data/      # Knowledge base documents
├── threat-model/
│   └── threat_model.md   # Pre-deployment threat model
├── red-team/
│   └── findings.md       # Phase 2 attack findings
└── runbooks/
└── ai_incident_response.md

---

## Security Framework Mappings

| Control Area | Framework | Reference |
|---|---|---|
| LLM application risks | OWASP Top 10 for LLMs v2025 | LLM01–LLM10 |
| AI attack techniques | MITRE ATLAS | AML.T#### |
| AI risk governance | NIST AI RMF 1.0 | GOVERN / MAP / MEASURE / MANAGE |
| AI incident response | NIST SP 800-61 adapted for AI | Phase 2→4 runbook |

---

## Intentional Vulnerabilities (Phase 1)

The following are deliberately insecure and will be remediated in Phase 3:

| Resource | Vulnerability | OWASP Mapping |
|---|---|---|
| IAM Role | `Resource: *` on Bedrock and S3 | — |
| API Gateway | No authentication, no throttling | LLM10 — Unbounded Consumption |
| Lambda | No input validation or prompt template | LLM01 — Prompt Injection |
| S3 | No explicit encryption or access policy | LLM02 — Sensitive Info Disclosure |
| Bedrock | No guardrails configured | LLM01, LLM02 |
| CloudTrail | Disabled — no audit logging | — |

---

## Prerequisites

- AWS CLI with SSO profiles configured (`sandbox`, `security`, `management`)
- Terraform >= 1.15.0 (arm64 native recommended for Apple Silicon)
- Python 3.11+
- AWS Organizations with Sandbox and Security member accounts
- Anthropic FTU form submitted at management account level

---

## Cost

All resources are serverless. Estimated lab cost: **< $15/month** with a 
budget alert configured in the management account targeting the Sandbox account.

Primary cost driver: Amazon Bedrock token usage (Claude 3 Haiku — cheapest 
Anthropic model on Bedrock, fractions of a cent per request at lab volume).

---

## Author
Tayo S — Cloud Security Engineer  
[github.com/tayo214](https://github.com/tayo214)

*CompTIA SecAI+ (CY0-001) study lab | AI Security Engineer portfolio project*