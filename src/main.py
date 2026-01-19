"""Main entry point for PChome tracking list price follower."""

import sys
from datetime import datetime

from api import PChomeAPI, PChomeAPIError
from config import Config
from db import PriceDatabase
from notifier import SlackNotifier


def main() -> int:
    """Run the price tracker."""
    print(f"{'=' * 60}")
    print("PChome Tracking List Price Follower")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}\n")

    # Load configuration
    try:
        config = Config.load()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1

    # Initialize components
    notifier = SlackNotifier(config.slack_webhook_url)

    if notifier.enabled:
        print("📢 Slack notifications: Enabled")
    else:
        print("📢 Slack notifications: Disabled (no webhook URL)")

    print(f"💾 Database: {config.db_path}\n")

    # Fetch tracking list from PChome
    print("📥 Fetching tracking list from PChome...")
    try:
        with PChomeAPI(config.pchome_ecwebsess) as api:
            tracked_products = api.get_tracking_list()
            print(f"   Found {len(tracked_products)} products in tracking list\n")

            if not tracked_products:
                print("⚠️  No products in tracking list. Nothing to do.")
                return 0

            # Sync products with database
            with PriceDatabase(config.db_path) as db:
                existing_ids = db.get_tracked_product_ids()
                current_ids = {p.id for p in tracked_products}

                # Add new products
                new_ids = current_ids - existing_ids
                for product in tracked_products:
                    if product.id in new_ids:
                        db.add_product(product.id, product.name)
                        print(f"   ➕ Added new product: {product.name[:40]}...")

                # Remove products no longer in tracking list
                removed_ids = existing_ids - current_ids
                for product_id in removed_ids:
                    db.remove_product(product_id)
                    print(f"   ➖ Removed product: {product_id}")

                if new_ids or removed_ids:
                    print()

                # Fetch current prices
                print("💰 Fetching current prices...")
                product_ids = [p.id for p in tracked_products]
                prices = api.get_prices(product_ids)
                print(f"   Retrieved prices for {len(prices)} products\n")

                # Check for price drops and record prices
                print("📊 Analyzing prices...\n")
                alerts_sent = 0
                new_lows = 0

                for product in tracked_products:
                    price_info = prices.get(product.id)
                    if not price_info:
                        print(f"   ⚠️  {product.name[:50]}")
                        print(f"       價格: N/A")
                        print()
                        continue

                    current_price = price_info.price
                    historical_low = db.get_historical_low(product.id)

                    # Check if this is a new historical low
                    is_new_low = historical_low is None or current_price < historical_low

                    # Determine status and icon
                    if historical_low is None:
                        icon = "🆕"
                        status_line = "（首次記錄）"
                    elif is_new_low:
                        new_lows += 1
                        drop = historical_low - current_price
                        drop_pct = (drop / historical_low) * 100
                        icon = "🔻"
                        status_line = f"（歷史新低！原低價 NT${historical_low:,}，降 {drop_pct:.1f}%）"

                        # Send Slack notification
                        if notifier.send_price_drop_alert(
                            product_id=product.id,
                            product_name=product.name,
                            current_price=current_price,
                            historical_low=historical_low,
                        ):
                            alerts_sent += 1
                    else:
                        icon = "　"
                        status_line = f"（歷史低價 NT${historical_low:,}）"

                    # Print product info
                    name_display = product.name if len(product.name) <= 50 else product.name[:47] + "..."
                    print(f"   {icon} {name_display}")
                    print(f"       價格: NT${current_price:,} {status_line}")
                    print()

                    # Record current price
                    db.record_price(product.id, current_price)

                # Summary
                print(f"\n{'=' * 60}")
                print("📋 Summary:")
                print(f"   • Products tracked: {len(tracked_products)}")
                print(f"   • New products added: {len(new_ids)}")
                print(f"   • Products removed: {len(removed_ids)}")
                print(f"   • New historical lows: {new_lows}")
                if notifier.enabled:
                    print(f"   • Slack alerts sent: {alerts_sent}")
                print(f"{'=' * 60}")

    except PChomeAPIError as e:
        print(f"\n❌ PChome API error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise

    return 0


if __name__ == "__main__":
    sys.exit(main())
