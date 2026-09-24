import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds


class Deployment(Document):
	def validate(self):
		self.validate_server()
		self.validate_website()
		self.validate_production_approval()
		self.calculate_duration()
		
	def validate_server(self):
		if not self.server:
			return
		
		server_status = frappe.db.get_value(
			"Server",
			self.server,
			"status"
		)
		blocked_statuses = ['Offilne',"Maintenace","Decomissioned"]

		if server_status in blocked_statuses:
			frappe.throw(
				f"Deployement cannot proceed beacuse server"
				f"<b>{self.server} is </b>{server_status}."
			)

	def validate_website(self):
		if not self.website:
			return
		website_status = frappe.db.get_value(
			"Website_",
			self.website,
			"status"
		)
		blocked_statuses = ["Suspended","Archive","Inactive"]

		if website_status in blocked_statuses:
			frappe.throw(
				f"Deployemnt cannot proceed because server"
				f"<b>{self.website} is </b>{server_status}"
			)
	def validate_production_approval(self):
		if not self.website:
			return
		environment = frappe.db.get_value(
			"website_",
			self.website,
			"environment"
		)
		if environment == "Production":
			if self.status == "Running" and not self.approved_by:
				frappe.throw(
					"Production deployment requires approval"
					"before it can be moved to Running."
				)
	def calculate_duration(self):
		if self.start_time and self.end_time:
			self.duration_seconds = time_diff_in_seconds(
				self.end_time,
				self.start_time
			)
	def before_save(self):
		self.add_timestamp_audit_log()
	def add_timestamp_audit_log(self):
		if not self.start_time and self.status=="Running":
			self.start_time = now_datetime()
		if self.status in ["Successful", "Failed", "Cancelled", "Rolled Back"]:
			if not self.end_time:
				self.end_time = now_datetime()
			if self.start_time and self.end_time:
				self.duration_seconds = time_diff_in_seconds(
					self.end_time,
					self.start_time
				)
	def on_update(self):
		self.create_incident_if_failed()
	def create_incident_if_failed(self):
		if self.status != "Failed":
			return

		# Prevent duplicate Incident creation
		existing_incident = frappe.db.exists(
			"Incident",
			{
				"deployment": self.name
			}
		)

		if existing_incident:
			return

		incident = frappe.get_doc({
			"doctype": "Incident",
			"title": f"Deployment Failed: {self.name}",
			"server": self.server,
			"website": self.website,
			"reported_by": frappe.session.user,
			"priority": "High",
			"category": "Deployment",
			"description": (
				f"Deployment <b>{self.name}</b> failed.<br><br>"
				f"<b>Commit:</b> {self.commit_id or 'N/A'}<br>"
				f"<b>Branch:</b> {self.branch or 'N/A'}<br>"
				f"<b>Deployment Type:</b> "
				f"{self.deployment_type or 'N/A'}<br><br>"
				f"<b>Deployment Log:</b><br>"
				f"{self.deployment_log or 'No deployment log available.'}"
			),
			"status": "Open"
		})

		# Only set this if your Incident DocType has a deployment field
		incident.deployment = self.name

		incident.insert(ignore_permissions=True)

		frappe.msgprint(
			f"Incident <b>{incident.name}</b> created automatically "
			f"because deployment <b>{self.name}</b> failed."
		)

