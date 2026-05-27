import os
import sqlite3
import json
import csv
from datetime import datetime
from werkzeug.security import generate_password_hash


class DatabaseManager:
    def __init__(self, db_path="data/pos.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                supplier TEXT NOT NULL,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL,
                restock_threshold INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_code TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_email TEXT,
                created_at TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax REAL NOT NULL,
                discount REAL NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL,
                payment_method TEXT,
                payment_status TEXT,
                payment_reference TEXT
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                barcode TEXT NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                method TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                reference TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
            """
        )

        self.conn.commit()
        self._ensure_default_users()

    def _ensure_default_users(self):
        existing = self.fetchone("SELECT id FROM users LIMIT 1")
        if not existing:
            self.execute(
                "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                ("admin", generate_password_hash("admin123"), "Admin", "Store Administrator"),
            )
            self.execute(
                "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                ("cashier", generate_password_hash("cashier123"), "Cashier", "Frontline Cashier"),
            )

    def execute(self, query, params=()):
        result = self.cursor.execute(query, params)
        self.conn.commit()
        return result

    def fetchone(self, query, params=()):
        return self.cursor.execute(query, params).fetchone()

    def fetchall(self, query, params=()):
        return self.cursor.execute(query, params).fetchall()

    def backup_table_json(self, table_name, backup_folder="data/backups"):
        os.makedirs(backup_folder, exist_ok=True)
        rows = self.fetchall(f"SELECT * FROM {table_name}")
        result = [dict(row) for row in rows]
        filename = os.path.join(backup_folder, f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        return filename

    def backup_table_csv(self, table_name, backup_folder="data/backups"):
        os.makedirs(backup_folder, exist_ok=True)
        rows = self.fetchall(f"SELECT * FROM {table_name}")
        if not rows:
            return None
        filename = os.path.join(backup_folder, f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys())
            for row in rows:
                writer.writerow(list(row))
        return filename

    def close(self):
        self.conn.close()
