"""Slack notification module for price alerts."""

import httpx


class SlackNotifier:
    """Sends price drop notifications to Slack."""

    def __init__(self, webhook_url: str | None) -> None:
        """Initialize the notifier with Slack webhook URL."""
        self.webhook_url = webhook_url
        self.enabled = webhook_url is not None and webhook_url.strip() != ""

    def send_price_drop_alert(
        self,
        product_id: str,
        product_name: str,
        current_price: int,
        historical_low: int,
    ) -> bool:
        """Send a price drop notification to Slack.

        Returns True if notification was sent successfully, False otherwise.
        """
        # The None check is implied by `enabled`; it narrows the type for httpx.
        if not self.enabled or self.webhook_url is None:
            return False

        price_drop = historical_low - current_price
        drop_percent = (price_drop / historical_low) * 100 if historical_low > 0 else 0

        product_url = f"https://24h.pchome.com.tw/prod/{product_id}"

        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔔 PChome 價格新低通知",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*📦 商品*\n{product_name}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*💰 當前價格*\nNT$ {current_price:,}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*📉 歷史最低*\nNT$ {historical_low:,}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*🔻 降幅*\n-{price_drop:,} ({drop_percent:.1f}%)",
                        },
                    ],
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔗 查看商品",
                                "emoji": True,
                            },
                            "url": product_url,
                        }
                    ],
                },
            ]
        }

        try:
            response = httpx.post(
                self.webhook_url,
                json=message,
                timeout=10.0,
            )
            return response.status_code == 200
        except httpx.RequestError as e:
            print(f"Failed to send Slack notification: {e}")
            return False
