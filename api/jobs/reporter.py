import os
from discord import Webhook, RequestsWebhookAdapter
from bot import generate_report

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "DEBUG")

if __name__ == "__main__":
    # Construct the webhook object using the webhook url
    webhook = Webhook.from_url(
        DISCORD_WEBHOOK_URL,
        adapter=RequestsWebhookAdapter()
    )

    # Send the report under username Anubis_Daily_Report
    webhook.send(
        f"```{generate_report()}```",
        username='Anubis_Daily_Report'
    )