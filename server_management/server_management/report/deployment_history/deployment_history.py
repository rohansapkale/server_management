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
            "label": "Deployment Type",
            "fieldname": "deployment_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Requested By",
            "fieldname": "requested_by",
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "label": "Approved By",
            "fieldname": "approved_by",
            "fieldtype": "Link",
            "options": "User",
            "width": 150
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
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Rollback Required",
            "fieldname": "rollback_required",
            "fieldtype": "Check",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("website"):
        conditions.append("website = %(website)s")
        values["website"] = filters["website"]

    if filters.get("server"):
        conditions.append("server = %(server)s")
        values["server"] = filters["server"]

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]

    if filters.get("deployment_type"):
        conditions.append("deployment_type = %(deployment_type)s")
        values["deployment_type"] = filters["deployment_type"]

    if filters.get("from_date"):
        conditions.append("DATE(deployment_date) >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("DATE(deployment_date) <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            name,
            website,
            server,
            branch,
            commit_id,
            commit_message,
            deployment_type,
            requested_by,
            approved_by,
            deployment_date,
            start_time,
            end_time,
            duration_seconds,
            status,
            rollback_required
        FROM `tabDeployment`
        {where_clause}
        ORDER BY deployment_date DESC
        """,
        values,
        as_dict=True
    )