# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Backup",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Backup",
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
            "label": "Website",
            "fieldname": "website",
            "fieldtype": "Link",
            "options": "Website",
            "width": 150
        },
        {
            "label": "Backup Type",
            "fieldname": "backup_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Backup Date",
            "fieldname": "backup_date",
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "label": "File Name",
            "fieldname": "file_name",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": "File Size",
            "fieldname": "file_size",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Backup Location",
            "fieldname": "backup_location",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Retention Days",
            "fieldname": "retention_days",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": "Expiry Date",
            "fieldname": "expiry_date",
            "fieldtype": "Date",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("server"):
        conditions.append(
            "server = %(server)s"
        )
        values["server"] = filters["server"]

    if filters.get("website"):
        conditions.append(
            "website = %(website)s"
        )
        values["website"] = filters["website"]

    if filters.get("backup_type"):
        conditions.append(
            "backup_type = %(backup_type)s"
        )
        values["backup_type"] = filters["backup_type"]

    if filters.get("status"):
        conditions.append(
            "status = %(status)s"
        )
        values["status"] = filters["status"]

    if filters.get("from_date"):
        conditions.append(
            "DATE(backup_date) >= %(from_date)s"
        )
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append(
            "DATE(backup_date) <= %(to_date)s"
        )
        values["to_date"] = filters["to_date"]

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            name,
            server,
            website,
            backup_type,
            backup_date,
            file_name,
            file_size,
            backup_location,
            status,
            retention_days,
            expiry_date
        FROM `tabBackup`
        {where_clause}
        ORDER BY backup_date DESC
        """,
        values,
        as_dict=True
    )