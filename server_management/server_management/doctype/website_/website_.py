# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Website_(Document):
	_DOCTYPE_NAME = "Website_"
   import frappe
   form frappe.model.document import Document

class website(document):
	def validate(self):
        self.validate_server()
		self.validate_production()
        self.validate_status_transition()

	 def validate_server(self):
         if not self.server:
            return	
        
		 server_status = frappe.db.get_value(
            "Server",
            self.server,
            "status"
		 )
		 if(
			 if (
            self.status == "Active"
            and server_status == "Decommissioned"
        ):
            frappe.throw(
                f"Active Website cannot be linked to "
                f"Decommissioned Server: {self.server}"
            )
	 def validate_production(self):
        if self.environment == "Production":

            if not self.domain:
                frappe.throw(
                    "Production website must have a Domain."
                )

            if not self.ssl_enabled:
                frappe.msgprint(
                    "SSL is recommended for Production websites.",
                    alert=True
                )
	 def validate_status_transition(self):
        if self.is_new():
            return

        old_status = self.get_db_value("status")

        if old_status == self.status:
            return

        restricted_statuses = [
            "Archived",
            "Suspended"
        ]

        if self.status in restricted_statuses:

            active_deployment = frappe.db.exists(
                "Deployment",
                {
                    "website": self.name,
                    "status": "Active"
                }	
			)

            if active_deployment:
                frappe.throw(
                    f"Cannot change Website status to "
                    f"{self.status} while an active deployment exists."
                )			


	

