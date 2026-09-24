import frappe
from frappe.utils import getdate, today


def execute(filters=None):

    columns = [
        {
            "label": "Domain Name",
            "fieldname": "domain_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Registrar",
            "fieldname": "registrar",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Expiry Date",
            "fieldname": "expiry_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "Days Remaining",
            "fieldname": "days_remaining",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Auto Renew",
            "fieldname": "auto_renew",
            "fieldtype": "Data",
            "width": 120
        }
    ]

    domains = frappe.get_all(
        "Domain",
        fields=[
            "name as domain_name",
            "registrar",
            "expiry_date",
            "auto_renew"
        ],
        order_by="expiry_date asc"
    )

    data = []

    for domain in domains:

        if domain.expiry_date:
            days_remaining = (
                getdate(domain.expiry_date) - getdate(today())
            ).days
        else:
            days_remaining = None

        data.append({
            "domain_name": domain.domain_name,
            "registrar": domain.registrar,
            "expiry_date": domain.expiry_date,
            "days_remaining": days_remaining,
            "auto_renew": domain.auto_renew
        })

    return columns, data