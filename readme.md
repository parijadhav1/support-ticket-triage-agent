# AI Support Ticket Triage Agent

An AI-powered support ticket triage system built with Python and Azure OpenAI.

The agent analyzes customer support tickets and determines:

- Category
- Urgency
- Confidence score
- Support team routing
- Whether human review is required
- Reason for the decision

It also supports batch processing of support tickets from a CSV file.

---

## Architecture

CSV Input
    ↓
Python Application
    ↓
Azure OpenAI
    ↓
Structured JSON Classification
    ↓
Validation + Safety Rules
    ↓
Human Review Decision
    ↓
CSV Output

---

## Features

### 1. Ticket Classification

Each ticket is classified into one of:

- Billing
- Account
- Technical
- Orders
- Subscription
- Other

### 2. Urgency Detection

Tickets are assigned:

- Low
- Medium
- High
- Critical

### 3. Confidence Score

The AI returns a confidence score between 0 and 1.

### 4. Team Routing

Tickets are automatically routed based on category:

| Category | Route |
|---|---|
| Billing | Payments Team |
| Account | Account Support |
| Technical | Technical Support |
| Orders | Order Support |
| Subscription | Retention Team |
| Other | General Support |

### 5. Human-in-the-Loop

Tickets are flagged for human review when:

- Confidence is below 0.70
- The ticket is Critical
- The issue is ambiguous
- The issue involves a security/account takeover situation
- The model indicates that human review is necessary

Critical security-related decisions are additionally enforced through deterministic Python rules rather than relying entirely on the LLM.

---

## Project Structure

```text
support-ticket-triage-agent/
│
├── data/
│   └── sample_tickets.csv
│
├── output/
│   └── triage_results.csv
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md