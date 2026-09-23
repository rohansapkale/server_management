import frappe
from frappe.utils import getdate, today


def execute(filters=None):

    columns = [
        {
            "label": "Domain",
            "fieldname": "domain",
            "fieldtype": "Link",
            "options": "Domain",
            "width": 200
        },
        {
            "label": "Certificate",
            "fieldname": "certificate",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Provider",
            "fieldname": "provider",
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
        }
    ]

    certificates = frappe.get_all(
        "SSL Certificate",
        fields=[
            "name as certificate",
            "domain",
            "provider",
            "expiry_date"
        ],
        order_by="expiry_date asc"
    )

    data = []

    for certificate in certificates:

        if certificate.expiry_date:
            days_remaining = (
                getdate(certificate.expiry_date) - getdate(today())
            ).days
        else:
            days_remaining = None

        data.append({
            "domain": certificate.domain,
            "certificate": certificate.certificate,
            "provider": certificate.provider,
            "expiry_date": certificate.expiry_date,
            "days_remaining": days_remaining
        })

    return columns, data