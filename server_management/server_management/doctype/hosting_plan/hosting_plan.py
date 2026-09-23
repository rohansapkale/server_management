# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HostingPlan(Document):
	_DOCTYPE_NAME = "Hosting Plan"
class HostingPlan(Document):

    def validate(self):
        if self.monthly_price < 0:
            frappe.throw("Monthly price cannot be negative.")

        if self.max_websites < 0:
            frappe.throw("Max websites cannot be negative.")

        if self.max_storage_gb < 0:
            frappe.throw("Max storage cannot be negative.")

        if self.max_bandwidth_gb < 0:
            frappe.throw("Max bandwidth cannot be negative.")

        if self.max_databases < 0:
            frappe.throw("Max databases cannot be negative.")

        if self.max_email_accounts < 0:
            frappe.throw("Max email accounts cannot be negative.")

        if self.max_domains < 0:
            frappe.throw("Max domains cannot be negative.")