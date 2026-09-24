import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class Incident(Document):
	def validate(self):
		self.validate_priority()
		self.validate_resolution()

	def before_save(self):
		self.set_resolved_at()

	def validate_priority(self):
		if self.priority == "Critical" and not self.assigned_to:
			frappe.throw(
				"Critical incidents must have an <b>Assigned To </b> user"
			)
	def validate_resolution(self):
		if self.status in ["Resolved","Closed"]:
			if not self.resolution:
				frappe.throw(
					"Resolution is required when an incident is "
					"Resolved or Closed."
				)

			if not self.resolved_at:
				frappe.throw(
					"Resolved At is required when an incident is "
					"Resolved or Closed."
				)
	def set_resolved_at(self):
		if self.status == "Resolved" and not self.resolved_at:
			self.resolved_at = now_datetime()
