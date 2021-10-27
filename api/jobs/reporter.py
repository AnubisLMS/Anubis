import os
from discord import Webhook, RequestsWebhookAdapter
from bot import generate_report

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "DEBUG")

if __name__ == "__main__":
    webhook = Webhook.from_url(
        DISCORD_WEBHOOK_URL,
        adapter=RequestsWebhookAdapter()
    )

    webhook.send(
        f"```{generate_report()}```",
        username='Anubis_Daily_Report'
    )