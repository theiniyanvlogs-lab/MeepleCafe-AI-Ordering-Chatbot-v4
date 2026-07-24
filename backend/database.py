"""
=========================================================
Meeple Cafe AI Ordering Chatbot
SQLite Database Manager
Version : 4.0.0
Author  : Sugumar R
=========================================================
"""

import sqlite3
from contextlib import closing
from pathlib import Path

from backend.config import DATABASE_FILE


class DatabaseManager:
    """
    SQLite Database Manager

    Handles:
    - Database connection
    - Table creation
    - Order storage
    - Order retrieval
    """

    def __init__(self):
        self.db_path = str(DATABASE_FILE)
        self.create_tables()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        with closing(self.connect()) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    address TEXT NOT NULL,
                    payment_method TEXT NOT NULL,
                    total_amount REAL DEFAULT 0,
                    status TEXT DEFAULT 'Preparing',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY(order_id)
                        REFERENCES orders(order_id)
                )
            """)

            conn.commit()

    # =====================================================
    # Orders
    # =====================================================

    def create_order(
        self,
        customer_name,
        phone,
        email,
        address,
        payment_method,
        total_amount=0,
    ):

        with closing(self.connect()) as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO orders
                (
                    customer_name,
                    phone,
                    email,
                    address,
                    payment_method,
                    total_amount
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_name,
                    phone,
                    email,
                    address,
                    payment_method,
                    total_amount,
                ),
            )

            conn.commit()

            return cursor.lastrowid

    def add_order_item(
        self,
        order_id,
        item_id,
        quantity,
    ):

        with closing(self.connect()) as conn:

            conn.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    item_id,
                    quantity
                )
                VALUES (?, ?, ?)
                """,
                (
                    order_id,
                    item_id,
                    quantity,
                ),
            )

            conn.commit()

    def get_orders(self):

        with closing(self.connect()) as conn:

            rows = conn.execute(
                """
                SELECT *
                FROM orders
                ORDER BY created_at DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def get_order(self, order_id):

        with closing(self.connect()) as conn:

            row = conn.execute(
                """
                SELECT *
                FROM orders
                WHERE order_id=?
                """,
                (order_id,),
            ).fetchone()

            if row:
                return dict(row)

            return None

    def update_status(
        self,
        order_id,
        status,
    ):

        with closing(self.connect()) as conn:

            conn.execute(
                """
                UPDATE orders
                SET status=?
                WHERE order_id=?
                """,
                (
                    status,
                    order_id,
                ),
            )

            conn.commit()

    def delete_order(self, order_id):

        with closing(self.connect()) as conn:

            conn.execute(
                "DELETE FROM order_items WHERE order_id=?",
                (order_id,),
            )

            conn.execute(
                "DELETE FROM orders WHERE order_id=?",
                (order_id,),
            )

            conn.commit()

    def total_orders(self):

        with closing(self.connect()) as conn:

            row = conn.execute(
                "SELECT COUNT(*) AS total FROM orders"
            ).fetchone()

            return row["total"]


database = DatabaseManager()
