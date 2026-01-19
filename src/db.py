"""Database module for managing price history with SQLite."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class PriceRecord:
    """A price record from the database."""

    product_id: str
    price: int
    recorded_at: datetime


class PriceDatabase:
    """SQLite database for tracking product prices."""

    def __init__(self, db_path: Path) -> None:
        """Initialize the database connection."""
        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def __enter__(self) -> "PriceDatabase":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def _init_tables(self) -> None:
        """Initialize database tables."""
        cursor = self.conn.cursor()

        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                price INTEGER NOT NULL,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)

        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_product_id
            ON price_history(product_id)
        """)

        self.conn.commit()

    def get_tracked_product_ids(self) -> set[str]:
        """Get all product IDs currently in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM products")
        return {row["id"] for row in cursor.fetchall()}

    def add_product(self, product_id: str, name: str) -> None:
        """Add a new product to the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO products (id, name, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (product_id, name),
        )
        self.conn.commit()

    def remove_product(self, product_id: str) -> None:
        """Remove a product and its price history from the database."""
        cursor = self.conn.cursor()
        # Delete price history first (foreign key)
        cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()

    def get_historical_low(self, product_id: str) -> int | None:
        """Get the historical lowest price for a product."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT MIN(price) as min_price
            FROM price_history
            WHERE product_id = ?
            """,
            (product_id,),
        )
        row = cursor.fetchone()
        return row["min_price"] if row and row["min_price"] is not None else None

    def get_latest_price(self, product_id: str) -> int | None:
        """Get the most recent price for a product."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT price
            FROM price_history
            WHERE product_id = ?
            ORDER BY recorded_at DESC
            LIMIT 1
            """,
            (product_id,),
        )
        row = cursor.fetchone()
        return row["price"] if row else None

    def record_price(self, product_id: str, price: int) -> None:
        """Record a new price for a product."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
            """,
            (product_id, price),
        )
        # Update product's updated_at timestamp
        cursor.execute(
            """
            UPDATE products SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (product_id,),
        )
        self.conn.commit()

    def get_price_history(self, product_id: str, limit: int = 10) -> list[PriceRecord]:
        """Get price history for a product."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT product_id, price, recorded_at
            FROM price_history
            WHERE product_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?
            """,
            (product_id, limit),
        )
        return [
            PriceRecord(
                product_id=row["product_id"],
                price=row["price"],
                recorded_at=datetime.fromisoformat(row["recorded_at"]),
            )
            for row in cursor.fetchall()
        ]
