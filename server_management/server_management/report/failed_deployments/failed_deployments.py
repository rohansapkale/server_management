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
            "label": "Deployment",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Deployment",
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
            "label": "Server",
            "fieldname": "server",
            "fieldtype": "Link",
            "options": "Server",
            "width": 150
        },
        {
            "label": "Branch",
            "fieldname": "branch",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Commit ID",
            "fieldname": "commit_id",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Commit Message",
            "fieldname": "commit_message",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": "Deployment Date",
            "fieldname": "deployment_date",
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "label": "Start Time",
            "fieldname": "start_time",
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "label": "End Time",
            "fieldname": "end_time",
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "label": "Duration",
            "fieldname": "duration_seconds",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": "Failure Reason",
            "fieldname": "deployment_log",
            "fieldtype": "Text",
            "width": 300
        },
        {
            "label": "Requested By",
            "fieldname": "requested_by",
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        }
    ]


def get_data(filters):
    conditions = [
        "status = 'Failed'"
    ]

    values = {}

    if filters.get("website"):
        conditions.append(
            "website = %(website)s"
        )
        values["website"] = filters["website"]

    if filters.get("server"):
        conditions.append(
            "server = %(server)s"
        )
        values["server"] = filters["server"]

    if filters.get("from_date"):
        conditions.append(
            "DATE(deployment_date) >= %(from_date)s"
        )
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append(
            "DATE(deployment_date) <= %(to_date)s"
        )
        values["to_date"] = filters["to_date"]

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            name,
            website,
            server,
            branch,
            commit_id,
            commit_message,
            deployment_date,
            start_time,
            end_time,
            duration_seconds,
            deployment_log,
            requested_by
        FROM `tabDeployment`
        WHERE {where_clause}
        ORDER BY deployment_date DESC
        """,
        values,
        as_dict=True
    )