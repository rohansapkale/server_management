# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Server(Document):
	def validate(self):
		self.validate_ssh_port()
	def validate_ssh_port(self):
		if not self.ssh_port:
			return
		try:
			port = int(self.ssh_port)
		except (ValueError,TypeError):
			frappe.throw("SSH Port Must be a valid number")#
		if port <1 or port > 65535:
			frappe.throw("Enter a valid port number")
	def validate(self):
		if not self.ip_address:
			return
		try:
			ip = ip_address.ip_address(self.ip_address.strip())
			if ip.version == 4:
				self.ip_version="IPV4"
			else:
				self.ip_version="IPV6"
		except ValueError:
			frappe.throw(
				f"Invalid IP address: <b>{self.ip_address}</b>. "
				"Please enter a valid IPv4 or IPv6 address."
			)