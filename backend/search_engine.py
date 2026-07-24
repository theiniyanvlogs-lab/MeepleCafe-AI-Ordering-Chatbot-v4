"""
=========================================================
Meeple Cafe AI Ordering Chatbot
Menu Search Engine
Version : 4.0.0
Author  : Sugumar R
=========================================================
"""

from pathlib import Path
import pandas as pd

from backend.config import MENU_FILE


class SearchEngine:
    """
    Menu Search Engine

    Responsibilities
    ----------------
    - Load menu.csv
    - Return full menu
    - Search by keyword
    - Search by category
    - Search by price
    - Get item by ID
    """

    def __init__(self):
        self.menu = self._load_menu()

    # =====================================================
    # Load Menu
    # =====================================================

    def _load_menu(self):

        path = Path(MENU_FILE)

        if not path.exists():
            raise FileNotFoundError(f"Menu file not found: {path}")

        df = pd.read_csv(path)

        df.fillna("", inplace=True)

        return df

    # =====================================================
    # All Menu
    # =====================================================

    def get_all_menu(self):

        return self.menu.to_dict(orient="records")

    # =====================================================
    # Search
    # =====================================================

    def search(self, query: str):

        query = query.lower().strip()

        if not query:
            return []

        mask = self.menu.astype(str).apply(
            lambda col: col.str.lower().str.contains(query, na=False)
        ).any(axis=1)

        results = self.menu[mask]

        return results.to_dict(orient="records")

    # =====================================================
    # Category
    # =====================================================

    def search_category(self, category: str):

        if "Category" not in self.menu.columns:
            return []

        results = self.menu[
            self.menu["Category"].str.lower() == category.lower()
        ]

        return results.to_dict(orient="records")

    # =====================================================
    # Price
    # =====================================================

    def search_price(
        self,
        minimum=None,
        maximum=None,
    ):

        if "Price" not in self.menu.columns:
            return []

        df = self.menu.copy()

        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

        if minimum is not None:
            df = df[df["Price"] >= minimum]

        if maximum is not None:
            df = df[df["Price"] <= maximum]

        return df.to_dict(orient="records")

    # =====================================================
    # Item by ID
    # =====================================================

    def get_item(self, item_id):

        id_columns = ["ID", "Item_ID", "Menu_ID", "id"]

        for column in id_columns:

            if column in self.menu.columns:

                result = self.menu[self.menu[column] == item_id]

                if not result.empty:
                    return result.iloc[0].to_dict()

        return None

    # =====================================================
    # Categories
    # =====================================================

    def categories(self):

        if "Category" not in self.menu.columns:
            return []

        return sorted(self.menu["Category"].dropna().unique().tolist())

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self):

        return {
            "total_items": len(self.menu),
            "categories": len(self.categories()),
            "columns": list(self.menu.columns),
        }
