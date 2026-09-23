import frappe


def execute(filters=None):
    columns = [
        {
            "label": "Server",
            "fieldname": "server",
            "fieldtype": "Link",
            "options": "Server",
            "width": 150
        },
        {
            "label": "IP Address",
            "fieldname": "ip_address",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": "Operating System",
            "fieldname": "operating_system",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Environment",
            "fieldname": "environment",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "CPU",
            "fieldname": "cpu",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "RAM",
            "fieldname": "ram",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Storage",
            "fieldname": "storage",
            "fieldtype": "Data",
            "width": 100
        }
    ]

    conditions = {}

    if filters and filters.get("environment"):
        conditions["environment"] = filters.get("environment")

    data = frappe.get_all(
        "Server",
        filters=conditions,
        fields=[
            "name as server",
            "ip_address",
            "operating_system",
            "environment",
            "status",
            "cpu",
            "ram",
            "storage"
        ],
        order_by="modified desc"
    )

    return columns, data