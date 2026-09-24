import frappe


def execute(filters=None):
    columns = [
        {
            "label": "Website",
            "fieldname": "website",
            "fieldtype": "Link",
            "options": "Website",
            "width": 150
        },
        {
            "label": "Domain",
            "fieldname": "domain",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "label": "Server",
            "fieldname": "server",
            "fieldtype": "Link",
            "options": "Server",
            "width": 150
        },
        {
            "label": "Framework",
            "fieldname": "framework",
            "fieldtype": "Data",
            "width": 130
        },
        {
            "label": "SSL Status",
            "fieldname": "ssl_status",
            "fieldtype": "Data",
            "width": 120
        }
    ]

    data = frappe.get_all(
        "Website",
        fields=[
            "name as website",
            "domain",
            "customer",
            "server",
            "framework",
            "ssl_status"
        ],
        order_by="modified desc"
    )

    return columns, data