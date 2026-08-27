import os
import csv
import json
from dotenv import load_dotenv
from openai import AzureOpenAI


# Load environment variables
load_dotenv()

azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not azure_api_key:
    raise ValueError(
        "AZURE_OPENAI_API_KEY not found. Please add it to your .env file."
    )

if not azure_endpoint:
    raise ValueError(
        "AZURE_OPENAI_ENDPOINT not found. Please add it to your .env file."
    )

if not azure_deployment:
    raise ValueError(
        "AZURE_OPENAI_DEPLOYMENT not found. Please add it to your .env file."
    )

client = AzureOpenAI(
    api_key=azure_api_key,
    azure_endpoint=azure_endpoint,
    api_version="2024-02-01"
)


SYSTEM_PROMPT = """
You are an AI Support Ticket Triage Agent.

Your job is to analyze a customer support ticket and make a structured
triage decision.

For every ticket, determine:

1. category
2. urgency
3. confidence
4. route
5. human_review
6. reason

ALLOWED CATEGORIES:
- Billing
- Account
- Technical
- Orders
- Subscription
- Other

ALLOWED URGENCY LEVELS:
- Low
- Medium
- High
- Critical

ROUTING RULES:
- Billing -> Payments Team
- Account -> Account Support
- Technical -> Technical Support
- Orders -> Order Support
- Subscription -> Retention Team
- Other -> General Support

URGENCY GUIDELINES:

Critical:
- Account takeover
- Security breach
- Major financial risk
- System-wide outage

High:
- Money charged incorrectly
- Payment failure affecting a purchase
- Login/account access problem
- Important functionality completely broken
- Order issue requiring urgent resolution

Medium:
- Refund delay
- Product/order problem
- Subscription issue
- Recurring technical problem

Low:
- General questions
- How-to questions
- Non-urgent requests

CONFIDENCE:
Return a number between 0 and 1.

HUMAN REVIEW:
Set human_review to true if:
- the ticket is ambiguous
- there is insufficient information
- confidence is below 0.70
- the issue does not clearly fit one category
- the issue involves an unusual or potentially serious situation

Otherwise set human_review to false.

REASON:
Give a short explanation of why the ticket received its category,
urgency and routing.

IMPORTANT:
Return ONLY valid JSON.

Use exactly this structure:

{
    "category": "Billing",
    "urgency": "High",
    "confidence": 0.94,
    "route": "Payments Team",
    "human_review": false,
    "reason": "The customer reports being charged despite the order being cancelled."
}
"""


def triage_ticket(subject, body):
    """
    Send one support ticket to the AI model and return
    the structured triage decision.
    """

    response = client.chat.completions.create(
        model=azure_deployment,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Subject: {subject}

Customer message:
{body}
"""
            }
        ]
    )

    result = json.loads(
        response.choices[0].message.content
    )

    return result


def process_batch(input_file, output_file):
    """
    Read tickets from CSV, process each ticket,
    validate and enforce safety rules, then save results.
    """

    results = []

    allowed_categories = {
        "Billing",
        "Account",
        "Technical",
        "Orders",
        "Subscription",
        "Other"
    }

    allowed_urgencies = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    routing_map = {
        "Billing": "Payments Team",
        "Account": "Account Support",
        "Technical": "Technical Support",
        "Orders": "Order Support",
        "Subscription": "Retention Team",
        "Other": "General Support"
    }

    with open(
        input_file,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for ticket in reader:

            print(
                f"Processing {ticket['ticket_id']}..."
            )

            result = triage_ticket(
                ticket["subject"],
                ticket["body"]
            )

            # -----------------------------
            # VALIDATE CATEGORY
            # -----------------------------

            category = result.get("category", "Other")

            if category not in allowed_categories:
                category = "Other"

            # -----------------------------
            # VALIDATE URGENCY
            # -----------------------------

            urgency = result.get("urgency", "Medium")

            if urgency not in allowed_urgencies:
                urgency = "Medium"

            # -----------------------------
            # VALIDATE CONFIDENCE
            # -----------------------------

            try:
                confidence = float(
                    result.get("confidence", 0)
                )
            except (ValueError, TypeError):
                confidence = 0.0

            confidence = max(
                0.0,
                min(1.0, confidence)
            )

            # -----------------------------
            # DETERMINE ROUTE
            # -----------------------------

            route = routing_map[category]

            # -----------------------------
            # HUMAN REVIEW
            # -----------------------------

            human_review = bool(
                result.get("human_review", True)
            )

            # Deterministic safety rules
            if confidence < 0.70:
                human_review = True

            if urgency == "Critical":
                human_review = True

            # Security/account takeover cases
            subject_lower = ticket["subject"].lower()
            body_lower = ticket["body"].lower()

            security_keywords = [
                "hacked",
                "account takeover",
                "unauthorized access",
                "security breach",
                "stolen account",
                "someone accessed"
            ]

            if any(
                keyword in subject_lower
                or keyword in body_lower
                for keyword in security_keywords
            ):
                human_review = True

            # -----------------------------
            # REASON
            # -----------------------------

            reason = result.get(
                "reason",
                "No explanation provided."
            )

            results.append({
                "ticket_id": ticket["ticket_id"],
                "subject": ticket["subject"],
                "category": category,
                "urgency": urgency,
                "confidence": confidence,
                "route": route,
                "human_review": human_review,
                "reason": reason
            })

    # -----------------------------
    # SAVE RESULTS
    # -----------------------------

    with open(
        output_file,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        fieldnames = [
            "ticket_id",
            "subject",
            "category",
            "urgency",
            "confidence",
            "route",
            "human_review",
            "reason"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    return results


def main():

    input_file = "data/sample_tickets.csv"
    output_file = "output/triage_results.csv"

    os.makedirs("output", exist_ok=True)

    print("\n===================================")
    print(" AI SUPPORT TICKET TRIAGE AGENT")
    print("===================================\n")

    results = process_batch(
        input_file,
        output_file
    )

    print("\n===================================")
    print(" TRIAGE RESULTS")
    print("===================================\n")

    for result in results:

        print(
            f"{result['ticket_id']} | "
            f"{result['category']} | "
            f"{result['urgency']} | "
            f"Confidence: {result['confidence']} | "
            f"{result['route']} | "
            f"Human Review: {result['human_review']}"
        )

    print(
        f"\nResults saved to: {output_file}"
    )

def interactive_mode():
    print("\n===================================")
    print(" INTERACTIVE TICKET TRIAGE")
    print("===================================\n")

    subject = input("Enter ticket subject: ").strip()
    body = input("Enter customer message: ").strip()

    if not subject or not body:
        print("\nSubject and message cannot be empty.")
        return

    print("\nAnalyzing ticket...\n")

    result = triage_ticket(subject, body)

    print("===================================")
    print(" TRIAGE DECISION")
    print("===================================")

    print(f"Category:      {result.get('category')}")
    print(f"Urgency:       {result.get('urgency')}")
    print(f"Confidence:    {result.get('confidence')}")
    print(f"Route:         {result.get('route')}")
    print(f"Human Review:  {result.get('human_review')}")
    print(f"Reason:        {result.get('reason')}")

    print("===================================")

if __name__ == "__main__":
    main()

    print("\n")
    choice = input("Do you want to test a new ticket? (y/n): ").strip().lower()

    if choice == "y":
        interactive_mode()