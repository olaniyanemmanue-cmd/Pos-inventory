from database import DatabaseManager
from inventory import InventoryManager


def seed_sample_products(inventory):
    items = [
        ("100100100001", "Apple iPhone 15", "Electronics", "TechMart", 799.00, 18, 5),
        ("100100100002", "Samsung Galaxy S24", "Electronics", "TechMart", 749.00, 15, 4),
        ("100100100003", "Sony WH-1000XM5 Headphones", "Electronics", "AudioHub", 349.99, 12, 3),
        ("100100100004", "Nike Air Max 270", "Fashion", "SportStyle", 129.99, 25, 8),
        ("100100100005", "Adidas Ultraboost 23", "Fashion", "SportStyle", 159.95, 20, 6),
        ("100100100006", "Levi's 501 Jeans", "Fashion", "DenimWorld", 59.99, 30, 7),
        ("100100100007", "KitchenAid Stand Mixer", "Home", "HomeEssentials", 249.00, 8, 2),
        ("100100100008", "Samsung 55-inch Smart TV", "Home", "ElectroHome", 499.00, 10, 3),
        ("100100100009", "L'Oréal Paris Shampoo", "Beauty", "GlowMart", 14.99, 40, 10),
        ("100100100010", "Nescafé Gold Coffee", "Groceries", "MallGrocer", 8.49, 60, 12),
        ("100100100011", "Coco Crunch Cereal", "Groceries", "BreakfastMart", 5.49, 35, 8),
        ("100100100012", "Sparkling Lemonade", "Beverages", "CoolDrinks", 2.99, 50, 10),
        ("100100100013", "Fresh Red Apples", "Fruits", "FreshHarvest", 3.29, 42, 8),
        ("100100100014", "Banana Pack", "Fruits", "FreshHarvest", 2.49, 48, 10),
        ("100100100015", "Trail Mix Snack", "Snacks", "SnackWorld", 4.99, 30, 6),
        ("100100100016", "Whole Milk 1L", "Dairy", "FreshFarm", 3.79, 24, 5),
        ("100100100017", "Orange Juice 1L", "Beverages", "CoolDrinks", 4.49, 28, 6),
        ("100100100018", "Honey Oats Cereal", "Groceries", "BreakfastMart", 6.29, 28, 7),
        ("100100100019", "Frozen Mixed Vegetables", "Frozen", "FreshHarvest", 4.99, 18, 4),
        ("100100100020", "Bottled Water 500ml", "Beverages", "CoolDrinks", 1.49, 70, 15),
    ]

    for barcode, name, category, supplier, price, stock, threshold in items:
        if inventory.get_product_by_barcode(barcode) is None:
            inventory.add_product(barcode, name, category, supplier, price, stock, threshold)


def main():
    db = DatabaseManager()
    inventory = InventoryManager(db)
    seed_sample_products(inventory)
    print("Database initialized with default users and sample product data.")


if __name__ == "__main__":
    main()
