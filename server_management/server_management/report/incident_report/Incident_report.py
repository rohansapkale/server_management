# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, time_diff_in_seconds


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    calculate_duration(data)

    return columns, data


def get_columns():
    return [
        {
            "label": "Incident",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Incident",
            "width": 140
        },
        {
            "label": "Incident Title",
            "fieldname": "title",
            "fieldtype": "Data",
            "width": 250
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
            "label": "Priority",
            "fieldname": "priority",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 130
        },
        {
            "label": "Assigned To",
            "fieldname": "assigned_to",
            "fieldtype": "Link",
            "options": "User",
            "width": 180
        },
        {
            "label": "Started At",
            "fieldname": "started_at",
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "label": "Resolved At",
            "fieldname": "resolved_at",
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "label": "Duration",
            "fieldname": "duration",
            "fieldtype": "Data",
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

    if filters.get("priority"):
        conditions.append(
            "priority = %(priority)s"
        )
        values["priority"] = filters["priority"]

    if filters.get("status"):
        conditions.append(
            "status = %(status)s"
        )
        values["status"] = filters["status"]

    if filters.get("assigned_to"):
        conditions.append(
            "assigned_to = %(assigned_to)s"
        )
        values["assigned_to"] = filters["assigned_to"]

    if filters.get("from_date"):
        conditions.append(
            "DATE(started_at) >= %(from_date)s"
        )
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append(
            "DATE(started_at) <= %(to_date)s"
        )
        values["to_date"] = filters["to_date"]

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            name,
            title,
            server,
            website,
            priority,
            status,
            assigned_to,
            started_at,
            resolved_at
        FROM `tabIncident`
        {where_clause}
        ORDER BY started_at DESC
        """,
        values,
        as_dict=True
    )


def calculate_duration(data):
    current_time = now_datetime()

    for row in data:
        if not row.started_at:
            row.duration = "-"
            continue

        end_time = row.resolved_at or current_time

        seconds = time_diff_in_seconds(
            end_time,
            row.started_at
        )

        row.duration = format_duration(seconds)


def format_duration(seconds):
    seconds = int(seconds)

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    if days:
        return f"{days}d {hours}h {minutes}m"

    if hours:
        return f"{hours}h {minutes}m"

    if minutes:
        return f"{minutes}m"

    return f"{seconds}s"