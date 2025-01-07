from dotenv import load_dotenv
import unittest, os
from colorama import init, Fore
from assistant import Assistant

load_dotenv()
init(autoreset = True)


def run_chat(msg):
    IVAPEO_ASSISTANT_ID = os.getenv('IVAPEO_ASSISTANT_ID')
    TOOLS_API_URL = os.getenv('TOOLS_API_URL')
    TOOLS_API_URL = "http://127.0.0.1:8000"
    bot = Assistant('IVAPEO_BOT', IVAPEO_ASSISTANT_ID, TOOLS_API_URL)

    thread_id = bot.create_thread()
    
    ans, tools_called = bot.submit_message(msg, "34936069261", thread_id)
    print("="*150)
    print(Fore.BLUE + "User:", msg)
    print(Fore.BLUE + "Bot:", ans)
    print("="*150)
    
    return tools_called


class TestGet_product_details(unittest.TestCase):
    def test_get_product_details(self):
        msg = "Hola, dame los detalles del producto 'producto'"
        tools_called = run_chat(msg)
        self.assertIn("get_product_details", tools_called, f"The message {msg} failed in get_product_details")

    
    def test_get_product_details2(self):
        msg = "Quiero consultar informacion del producto 'producto'"
        tools_called = run_chat(msg)
        self.assertIn("get_product_details", tools_called, f"The message {msg} failed in get_product_details2")
    

class TestGet_products(unittest.TestCase):
    def test_get_products(self):
        msg = "Necesito información sobre el stock del producto 'producto'"
        tools_called = run_chat(msg)
        self.assertIn("get_products", tools_called, f"The message {msg} failed in get_products")


class TestGet_inventory_report(unittest.TestCase):
    def test_get_inventory_report(self):
        msg = "Quiero el informe del estado del inventario"
        tools_called = run_chat(msg)
        self.assertIn("get_inventory_report", tools_called, f"The message {msg} failed in get_inventory_report")


class TestGet_stock(unittest.TestCase):
    def test_get_stock(self):
        msg = "Dame el stock del almacén 'almacén'"
        tools_called = run_chat(msg)
        self.assertIn("get_stock", tools_called, f"The message {msg} failed in get_stock")


class TestMove_stock_between_warehouses(unittest.TestCase):
    def test_move_stock_between_warehouses(self):
        msg = "Abastece el almacén secundario 'almacén_secundario'"
        tools_called = run_chat(msg)
        self.assertIn("move_stock_between_warehouses", tools_called, f"The message {msg} failed in move_stock_between_warehouses")


class TestAnalyze_sales_and_create_orders(unittest.TestCase):
    def test_analyze_sales_and_create_orders(self):
        msg = "Abastecer el almacén 'almacén' desde la fecha '2023-01-01' por 4 semanas"
        tools_called = run_chat(msg)
        self.assertIn("analyze_sales_and_create_orders", tools_called, f"The message {msg} failed in analyze_sales_and_create_orders")


class TestGet_unsold_products(unittest.TestCase):
    def test_get_unsold_products(self):
        msg = "Quiero saber los productos no vendidos en el almacén 'almacén'"
        tools_called = run_chat(msg)
        self.assertIn("get_unsold_products", tools_called, f"The message {msg} failed in get_unsold_products")


class TestGet_sales_and_stock(unittest.TestCase):
    def test_get_sales_and_stock(self):
        msg = "Dame las ventas y el stock del producto 'producto' en el almacén 'almacén' para los últimos 30 días"
        tools_called = run_chat(msg)
        self.assertIn("get_sales_and_stock", tools_called, f"The message {msg} failed in get_sales_and_stock")


class TestCalculateInventoryTurnover(unittest.TestCase):
    def test_calculateInventoryTurnover(self):
        msg = "Calcula la rotación de inventario para el almacén 'almacén'"
        tools_called = run_chat(msg)
        self.assertIn("calculateInventoryTurnover", tools_called, f"The message {msg} failed in calculateInventoryTurnover")


class TestClean_messages(unittest.TestCase):
    def test_clean_messages(self):
        msg = "Limpia el historial de mensajes"
        tools_called = run_chat(msg)
        self.assertIn("clean_messages", tools_called, f"The message {msg} failed in clean_messages")


if __name__ == '__main__':
    unittest.main()
