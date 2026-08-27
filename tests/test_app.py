import os
import csv
import tempfile
import unittest
from unittest.mock import patch, MagicMock


os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "test-deployment"

import app


class TestSupportTicketTriage(unittest.TestCase):

    @patch("app.client")
    def test_triage_ticket_returns_expected_fields(self, mock_client):

        mock_response = MagicMock()

        mock_response.choices[0].message.content = """
        {
            "category": "Account",
            "urgency": "High",
            "confidence": 0.90,
            "route": "Account Support",
            "human_review": false,
            "reason": "The customer cannot access their account."
        }
        """

        mock_client.chat.completions.create.return_value = mock_response

        result = app.triage_ticket(
            "Cannot login",
            "My password is not working."
        )

        self.assertEqual(result["category"], "Account")
        self.assertEqual(result["urgency"], "High")
        self.assertEqual(result["route"], "Account Support")
        self.assertEqual(result["confidence"], 0.90)
        self.assertFalse(result["human_review"])
        self.assertIn("reason", result)


    @patch("app.triage_ticket")
    def test_batch_processing_creates_output(self, mock_triage):

        mock_triage.return_value = {
            "category": "Billing",
            "urgency": "High",
            "confidence": 0.95,
            "route": "Payments Team",
            "human_review": False,
            "reason": "Duplicate payment."
        }

        with tempfile.TemporaryDirectory() as temp_dir:

            input_file = os.path.join(
                temp_dir,
                "tickets.csv"
            )

            output_file = os.path.join(
                temp_dir,
                "results.csv"
            )

            with open(
                input_file,
                "w",
                encoding="utf-8",
                newline=""
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "ticket_id",
                        "subject",
                        "body"
                    ]
                )

                writer.writeheader()

                writer.writerow({
                    "ticket_id": "T001",
                    "subject": "Charged twice",
                    "body": "I was charged twice."
                })

            results = app.process_batch(
                input_file,
                output_file
            )

            self.assertEqual(len(results), 1)
            self.assertEqual(
                results[0]["category"],
                "Billing"
            )

            self.assertTrue(
                os.path.exists(output_file)
            )


if __name__ == "__main__":
    unittest.main()