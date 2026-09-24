# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import ipaddress

import frappe
from frappe.model.document import Document


class Server(Document):

	def validate(self):
		self.validate_ip_address()
		self.validate_ssh_port()
		self.validate_status()

	def on_update(self):
		self.handle_offline_status()

	def on_trash(self):
		self.prevent_production_server_deletion()

	def validate_ip_address(self):
		if not self.ip_address:
			return

		try:
			ipaddress.ip_address(self.ip_address)
		except ValueError:
			frappe.throw(
				"Invalid IP address. Please enter a valid IPv4 or IPv6 address."
			)

	def validate_ssh_port(self):
		if not self.ssh_port:
			return

		if not 1 <= int(self.ssh_port) <= 65535:
			frappe.throw(
				"SSH Port must be between 1 and 65535."
			)

	def validate_status(self):
		if self.status == "Decommissioned":
			frappe.msgprint(
				"Warning: This server has been decommissioned "
				"and cannot receive new deployments."
			)

	def prevent_production_server_deletion(self):
		env = getattr(self, "enviorment", getattr(self, "environment", None))
		if env != "Production":
			return

		active_websites = frappe.get_all(
			"Website_",
			filters={
				"server": self.name,
				"status": ["in", ["Active", "Maintenance"]]
			},
			pluck="name"
		)

		if active_websites:
			frappe.throw(
				"Production server cannot be deleted because "
				"active websites are linked to it:<br><br>"
				+ "<br>".join(active_websites)
			)

	def handle_offline_status(self):
		previous_doc = self.get_doc_before_save()

		if not previous_doc:
			return

		if (
			previous_doc.status != "Offline"
			and self.status == "Offline"
		):
			self.create_offline_incident()

	def create_offline_incident(self):

		existing_incident = frappe.db.exists(
			"Incident",
			{
				"server": self.name,
				"status": ["in", ["Open", "Assigned", "Investigating", "Monitoring"]],
				"category": "Server"
			}
		)

		if existing_incident:
			return

		incident = frappe.get_doc({
			"doctype": "Incident",
			"title": f"Server Offline: {self.name}",
			"server": self.name,
			"reported_by": frappe.session.user,
			"priority": "Critical",
			"category": "Server",
			"description": (
				f"Server <b>{self.name}</b> has transitioned "
				"to Offline status."
			),
			"status": "Open"
		})

		incident.insert(ignore_permissions=True)

		frappe.msgprint(
			f"Incident <b>{incident.name}</b> created because "
			f"server <b>{self.name}</b> went Offline."
		)
	@frappe.whitelist()
	def check_health(server):

		server_doc = frappe.get_doc("Server", server)

		return (
		f"<b>Server:</b> {server_doc.name}<br>"
		f"<b>Status:</b> {server_doc.status}<br>"
		f"<b>IP Address:</b> {server_doc.ip_address}<br>"
		f"<b>Environment:</b> {server_doc.environment}"
		)