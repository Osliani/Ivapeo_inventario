from openai import OpenAI
import os

# User functions
get_product_details = {
    "name": "get_product_details",
    "description": "Obtener los detalles de un producto dado su nombre.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Nombre del producto a consultar.",
            },
        },
        "required": ["product_name"],
    },
}

# Admin functions
get_products = {
    "name": "get_products",
    "description": "Informacion sobre stock y disponibilidad de un producto en especifico dado su nombre. Solo para admins.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Nombre del producto a consultar.",
            },
        },
        "required": ["product_name"],
    },
}

get_inventory_report = {
    "name": "get_inventory_report",
    "description": "Obtener el informe del estado del inventario.",
    "parameters": {},
}

get_stock = {
    "name": "get_stock",
    "description": "Obtener el stock de un almacén dado el nombre del almacén.",
    "parameters": {
        "type": "object",
        "properties": {
            "warehouse_name": {
                "type": "string",
                "description": "Nombre del almacén a consultar el stock.",
            },
        },
        "required": ["warehouse_name"],
    },
}

move_stock_between_warehouses = {
    "name": "move_stock_between_warehouses",
    "description": "Abastece un almacen o tienda a partir de su nombre...",
    "parameters": {
        "type": "object",
        "properties": {
            "secondary_warehouse_name": {
                "type": "string",
                "description": "Nombre del almacén secundario.",
            },
        },
        "required": ["secondary_warehouse_name"],
    },
}

analyze_sales_and_create_orders = {
    "name": "analyze_sales_and_create_orders",
    "description": "Abastecer los Almacenes, analiza el historial de ventas...",
    "parameters": {
        "type": "object",
        "properties": {
            "warehouseName": {
                "type": "string",
                "description": "Nombre del almacén objetivo.",
            },
            "startDate": {
                "type": "string",
                "description": "Fecha de inicio para el análisis de ventas (formato: YYYY-MM-DD)",
            },
            "weeksToSupply": {
                "type": "number",
                "description": "Número de semanas para abastecer...",
            },
        },
        "required": ["startDate", "weeksToSupply"],
    },
}

get_unsold_products = {
    "name": "get_unsold_products",
    "description": "Obtener los productos que no se han vendido en los últimos dos meses en un almacén específico.",
    "parameters": {
        "type": "object",
        "properties": {
            "warehouse_name": {
                "type": "string",
                "description": "Nombre del almacén a consultar.",
            },
        },
        "required": ["warehouse_name"],
    },
}

get_sales_and_stock = {
    "name": "get_sales_and_stock",
    "description": "Obtener las ventas y el stock actual de un producto en un almacén dado un rango de fecha.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Nombre del producto a consultar.",
            },
            "warehouse_name": {
                "type": "string",
                "description": "Nombre del almacén a consultar.",
            },
            "days": {
                "type": "number",
                "description": "Rango de fecha para consultar las ventas y el stock actual (30, 60, 90).",
            },
        },
        "required": ["product_name", "warehouse_name", "days"],
    },
}

calculateInventoryTurnover = {
    "name": "calculateInventoryTurnover",
    "description": "Calcular la rotación de inventario para un almacén específico en un periodo trimestral...",
    "parameters": {
        "type": "object",
        "properties": {
            "warehouse_name": {
                "type": "string",
                "description": "Nombre del almacén para el cual se calculará la rotación de inventario.",
            },
        },
        "required": ["warehouse_name"],
    },
}

clean_messages = {
    "name": "clean_messages",
    "description": "Limpia el historial de mensajes de la bd",
    "parameters": {},
}


if __name__ == "__main__":
	client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
	assistant = client.beta.assistants.create (
		instructions = "Eres un asistente que brinda soporte técnico a los usuarios. Acompaña tus respuestas con emojis.",
		name = "ivapeo_inventario",
		tools = [
            {"type": "function", "function": get_product_details},
            {"type": "function", "function": get_products},
            {"type": "function", "function": get_inventory_report},
            {"type": "function", "function": get_stock},
            {"type": "function", "function": move_stock_between_warehouses},
            {"type": "function", "function": analyze_sales_and_create_orders},
            {"type": "function", "function": get_unsold_products},
            {"type": "function", "function": get_sales_and_stock},
            {"type": "function", "function": calculateInventoryTurnover},
            {"type": "function", "function": clean_messages},
        ],
		model = "gpt-4-1106-preview",
	)

	print(assistant.id)
