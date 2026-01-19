"""PChome API client for fetching tracking list and prices."""

from dataclasses import dataclass

import httpx

# API endpoints
TRACE_LIST_URL = "https://ecvip.pchome.com.tw/fsapi/member/products/trace/list"
BUTTON_API_URL = "https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button"

# Required headers
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 AppleWebKit/537.36",
}


@dataclass
class TrackedProduct:
    """A product in the tracking list."""

    id: str
    name: str
    brands: list[str]


@dataclass
class ProductPrice:
    """Price information for a product."""

    product_id: str
    price: int
    original_price: int


class PChomeAPIError(Exception):
    """Exception raised when PChome API returns an error."""

    pass


class PChomeAPI:
    """Client for PChome API."""

    def __init__(self, ecwebsess: str) -> None:
        """Initialize the API client with session cookie."""
        self.cookies = {"ECWEBSESS": ecwebsess}
        self.client = httpx.Client(
            headers=DEFAULT_HEADERS,
            cookies=self.cookies,
            timeout=30.0,
        )

    def __enter__(self) -> "PChomeAPI":
        return self

    def __exit__(self, *args: object) -> None:
        self.client.close()

    def get_tracking_list(self) -> list[TrackedProduct]:
        """Fetch all products in the tracking list."""
        products: list[TrackedProduct] = []
        page = 1
        limit = 100

        while True:
            response = self.client.get(
                TRACE_LIST_URL,
                params={"page": page, "limit": limit},
            )

            if response.status_code == 403:
                raise PChomeAPIError(
                    "Session expired or invalid. Please update PCHOME_ECWEBSESS. "
                    "See docs/COOKIE_GUIDE.md for instructions."
                )

            response.raise_for_status()
            data = response.json()

            for row in data.get("Rows", []):
                products.append(
                    TrackedProduct(
                        id=row["Id"],
                        name=row["Name"],
                        brands=row.get("BrandList", []),
                    )
                )

            total_pages = data.get("TotalPages", 1)
            if page >= total_pages:
                break
            page += 1

        return products

    def get_prices(self, product_ids: list[str]) -> dict[str, ProductPrice]:
        """Fetch prices for multiple products.

        Uses the button API which returns promotional prices (Price.Low)
        when available, falling back to regular price (Price.P).
        """
        if not product_ids:
            return {}

        # Button API requires product ID with -000 suffix
        item_ids = [f"{pid}-000" for pid in product_ids]

        # API accepts comma-separated list of product IDs
        response = self.client.get(
            f"{BUTTON_API_URL}&id={','.join(item_ids)}&fields=Id,Price"
        )

        if response.status_code == 403:
            raise PChomeAPIError("Session expired or invalid. Please update PCHOME_ECWEBSESS.")

        response.raise_for_status()
        data = response.json()

        prices: dict[str, ProductPrice] = {}
        for item in data:
            # Extract original product ID (remove suffix like -000, -001, etc.)
            full_id = item.get("Id", "")
            product_id = full_id.rsplit("-", 1)[0] if "-" in full_id else full_id

            # Skip if we already have this product (API may return variants)
            if product_id in prices:
                continue

            price_info = item.get("Price", {})
            # Price.Low is the promotional price (may be null)
            # Price.P is the regular online price
            # Price.M is the market/list price
            promo_price = price_info.get("Low")
            regular_price = price_info.get("P", 0)

            # Use promotional price if available, otherwise use regular price
            current_price = promo_price if promo_price else regular_price
            original_price = regular_price

            if current_price:
                prices[product_id] = ProductPrice(
                    product_id=product_id,
                    price=int(current_price),
                    original_price=int(original_price),
                )

        return prices
