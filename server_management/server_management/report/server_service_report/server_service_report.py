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
            "label": "Service Name",
            "fieldname": "service_name",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Type",
            "fieldname": "service_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Version",
            "fieldname": "version",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Port",
            "fieldname": "port",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Last Checked",
            "fieldname": "last_checked",
            "fieldtype": "Datetime",
            "width": 160
        }
    ]

    conditions = {}

    if filters and filters.get("server"):
        conditions["server"] = filters["server"]

    data = frappe.get_all(
        "Server Service",
        filters=conditions,
        fields=[
            "server",
            "service_name",
            "service_type",
            "version",
            "port",
            "status",
            "last_checked"
        ],
        order_by="modified desc"
    )

    return columns, data