"""Telegram notification module for price alerts."""

import re

import httpx


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2 format."""
    special_chars = r"_*[]()~`>#+=|{}.!-"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)


class TelegramNotifier:
    """Sends price drop notifications to Telegram."""

    def __init__(self, bot_token: str, chat_id: str) -> None:
        """Initialize the notifier with Telegram Bot credentials."""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_price_drop_alert(
        self,
        product_id: str,
        product_name: str,
        current_price: int,
        historical_low: int,
    ) -> bool:
        """Send a price drop notification to Telegram.

        Returns True if notification was sent successfully, False otherwise.
        """
        price_drop = historical_low - current_price
        drop_percent = (price_drop / historical_low) * 100 if historical_low > 0 else 0

        product_url = f"https://24h.pchome.com.tw/prod/{product_id}"

        # Escape product name for MarkdownV2
        escaped_name = escape_markdown_v2(product_name)

        message = (
            f"🔔 *價格警報*\n\n"
            f"*{escaped_name}*\n"
            f"💰 `NT${current_price:,}`（歷史新低！）\n"
            f"📉 前次低價：NT${historical_low:,}\n"
            f"🔻 降幅：\\-{price_drop:,} \\({drop_percent:.1f}%\\)\n"
            f"[查看商品]({product_url})"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "MarkdownV2",
        }

        try:
            response = httpx.post(self.api_url, json=payload, timeout=10.0)
            if response.status_code == 200:
                return True
            else:
                print(
                    f"Failed to send Telegram notification: "
                    f"{response.status_code} {response.text}"
                )
                return False
        except httpx.RequestError as e:
            print(f"Failed to send Telegram notification: {e}")
            return False
