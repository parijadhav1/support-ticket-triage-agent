# Decision Boundary

The AI Support Ticket Triage Agent uses the following decision boundaries
to determine urgency and whether a ticket requires human review.

## Urgency Decision Boundary

### Critical

A ticket is classified as Critical when it involves:

- Account takeover or unauthorized account access
- Security breaches
- Major financial risk
- System-wide outages

These cases may require immediate investigation and human intervention.

### High

A ticket is classified as High when it involves:

- Incorrect charges
- Payment failures preventing a purchase
- Login or account access problems
- Important functionality being completely broken
- Urgent order issues

### Medium

A ticket is classified as Medium when it involves:

- Refund delays
- Product or order problems
- Subscription issues
- Recurring technical problems

### Low

A ticket is classified as Low when it involves:

- General questions
- How-to requests
- Non-urgent requests

## Category Decision Boundary

Tickets are assigned to one of the following categories:

- Billing
- Account
- Technical
- Orders
- Subscription
- Other

If a ticket does not clearly fit one of these categories,
it is classified as Other and may require human review depending
on the confidence and situation.

## Routing Decision

Each category maps to a specific support team:

| Category | Route |
|----------|-------|
| Billing | Payments Team |
| Account | Account Support |
| Technical | Technical Support |
| Orders | Order Support |
| Subscription | Retention Team |
| Other | General Support |

## Human Review Boundary

A ticket is flagged for human review when:

- The ticket is ambiguous
- There is insufficient information
- Confidence is below 0.70
- The issue does not clearly fit a category
- The situation is unusual or potentially serious

Otherwise, the ticket is automatically routed without human review.

## Confidence

The model returns a confidence score between 0 and 1.

A confidence score below 0.70 is considered insufficient for
fully automated handling and triggers human review.

## Design Principle

The system favors automation for clear, well-understood support
requests while escalating uncertain, ambiguous, or potentially
high-impact cases to a human support agent.