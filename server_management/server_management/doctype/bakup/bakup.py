# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Bakup(Document):
	_DOCTYPE_NAME = "Bakup"
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate


class Backup(Document):

    def validate(self):
        self.validate_target()
        self.calculate_expiry_date()

    def validate_target(self):
        if not self.server and not self.website:
            frappe.throw(
                "Please specify at least one target: Server or Website."
            )

    def calculate_expiry_date(self):
        if self.backup_date:
            retention_days = self.retention_days or 30
            self.expiry_date = add_days(
                getdate(self.backup_date),
                retention_days
            )

    def on_update(self):
        self.check_failed_backup()

    def check_failed_backup(self):
        if self.status != "Failed":
            return

        frappe.msgprint(
            f"Backup {self.name} has failed.",
            alert=True
        )

        if frappe.db.exists("DocType", "Incident"):
            incident = frappe.get_doc({
                "doctype": "Incident",
                "subject": f"Backup Failed - {self.name}",
                "description": (
                    f"Backup: {self.name}\n"
                    f"Server: {self.server or 'N/A'}\n"
                    f"Website: {self.website or 'N/A'}\n"
                    f"Backup Type: {self.backup_type or 'N/A'}"
                )
            })

            incident.insert(ignore_permissions=True)