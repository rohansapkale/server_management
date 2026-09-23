# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SSLCertificate(Document):
	_DOCTYPE_NAME = "SSL Certificate"
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, today


class SSLCertificate(Document):

    def validate(self):
        self.calculate_days_remaining()
        self.calculate_status()

    def calculate_days_remaining(self):
        if self.expiry_date:
            self.days_remaining = date_diff(
                getdate(self.expiry_date),
                getdate(today())
            )

    def calculate_status(self):
        if not self.expiry_date:
            return

        if self.status == "Revoked":
            return

        if self.days_remaining <= 0:
            self.status = "Expired"

        elif self.days_remaining <= 30:
            self.status = "Expiring Soon"

        else:
            self.status = "Valid"