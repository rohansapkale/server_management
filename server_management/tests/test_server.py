# Copyright (c) 2026, Rohan Sapkale and Contributors
# See license.txt

import uuid
import frappe
from frappe.tests import IntegrationTestCase


class TestServer(IntegrationTestCase):
	"""
	Automated tests covering Server DocType:
	- Port bounds validation (1 to 65535)
	- IP validation (IPv4 and IPv6)
	- Offline deployment prevention
	- Duplicate hostnames prevention
	- Offline status incident creation
	- Production server deletion protection
	"""

	def setUp(self):
		frappe.db.rollback()
		self.cleanup_records = []

	def tearDown(self):
		for doctype, name in reversed(self.cleanup_records):
			if frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
		frappe.db.rollback()

	def create_server(self, **kwargs):
		unique_id = uuid.uuid4().hex[:8]
		defaults = {
			"doctype": "Server",
			"server_name": f"Test-Server-{unique_id}",
			"hostname": f"srv-{unique_id}.example.com",
			"ip_address": "192.168.1.100",
			"provider": "Local",
			"server_type": "VPS",
			"operating_system": "Ubuntu",
			"ssh_port": 22,
			"status": "Online",
			"enviorment": "Development",
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		self.cleanup_records.append(("Server", doc.name))
		return doc

	# =========================================================================
	# Port Bounds Tests
	# =========================================================================

	def test_valid_ssh_ports(self):
		"""Test that valid SSH ports within 1-65535 pass validation."""
		valid_ports = [1, 22, 80, 443, 2222, 8080, 65535]
		for port in valid_ports:
			unique_id = uuid.uuid4().hex[:8]
			server = frappe.get_doc({
				"doctype": "Server",
				"server_name": f"Valid-Port-{port}-{unique_id}",
				"hostname": f"port-{port}-{unique_id}.example.com",
				"ip_address": "192.168.1.1",
				"ssh_port": port,
				"status": "Online",
			})
			# Should validate without throwing any exception
			server.validate_ssh_port()

	def test_ssh_port_below_lower_bound(self):
		"""Test that SSH port < 1 raises ValidationError."""
		invalid_ports = [0, -1, -22, -65535]
		for port in invalid_ports:
			server = frappe.get_doc({
				"doctype": "Server",
				"server_name": f"Invalid-Port-{port}",
				"hostname": f"invalid-port-{port}.example.com",
				"ip_address": "192.168.1.1",
				"ssh_port": port,
				"status": "Online",
			})
			with self.assertRaises(frappe.ValidationError, msg=f"Port {port} should fail validation"):
				server.validate_ssh_port()

	def test_ssh_port_above_upper_bound(self):
		"""Test that SSH port > 65535 raises ValidationError."""
		invalid_ports = [65536, 70000, 100000]
		for port in invalid_ports:
			server = frappe.get_doc({
				"doctype": "Server",
				"server_name": f"Invalid-Port-{port}",
				"hostname": f"invalid-port-{port}.example.com",
				"ip_address": "192.168.1.1",
				"ssh_port": port,
				"status": "Online",
			})
			with self.assertRaises(frappe.ValidationError, msg=f"Port {port} should fail validation"):
				server.validate_ssh_port()

	def test_ssh_port_non_numeric(self):
		"""Test that non-numeric SSH port raises ValidationError."""
		server = frappe.get_doc({
			"doctype": "Server",
			"server_name": "Invalid-Port-String",
			"hostname": "invalid-str.example.com",
			"ip_address": "192.168.1.1",
			"ssh_port": "invalid_port",
			"status": "Online",
		})
		with self.assertRaises(frappe.ValidationError):
			server.validate_ssh_port()

	# =========================================================================
	# IP Validation Tests
	# =========================================================================

	def test_valid_ipv4_address(self):
		"""Test that valid IPv4 addresses pass validation."""
		valid_ips = ["192.168.1.1", "10.0.0.1", "172.16.254.1", "127.0.0.1", "8.8.8.8"]
		for ip in valid_ips:
			server = frappe.get_doc({
				"doctype": "Server",
				"server_name": f"Valid-IP-{ip}",
				"ip_address": ip,
			})
			# Should validate without throwing any exception
			server.validate_ip_address()

	def test_valid_ipv6_address(self):
		"""Test that valid IPv6 addresses pass validation."""
		valid_ipv6s = [
			"::1",
			"2001:0db8:85a3:0000:0000:8a2e:0370:7334",
			"fe80::1",
			"2001:db8::1",
		]
		for ip in valid_ipv6s:
			server = frappe.get_doc({
				"doctype": "Server",
				"server_name": "Valid-IPv6",
				"ip_address": ip,
			})
			# Should validate without throwing any exception
			server.validate_ip_address()

	def test_invalid_ip_addresses(self):
		"""Test that invalid IP addresses raise ValidationError."""
		invalid_ips = [
			"999.999.999.999",
			"256.1.1.1",
			"1.2.3.4.5",
			"invalid-ip-string",
			"192.168.1.",
			"192.168.1.1.1",
			"xyz:123:abc",
		]
		for ip in invalid_ips:
			server = frappe.get_doc({
				"doctype": "Server",
				"server_name": f"Invalid-IP-{ip}",
				"ip_address": ip,
			})
			with self.assertRaises(frappe.ValidationError, msg=f"IP {ip} should fail validation"):
				server.validate_ip_address()

	def test_empty_ip_address_allowed(self):
		"""Test that empty or None IP address is handled gracefully."""
		server = frappe.get_doc({
			"doctype": "Server",
			"server_name": "Empty-IP-Server",
			"ip_address": "",
		})
		# Should not throw
		server.validate_ip_address()

	# =========================================================================
	# Offline Deployment Prevention Tests
	# =========================================================================

	def test_offline_deployment_prevention(self):
		"""Test that deployments cannot proceed to an Offline server."""
		server = self.create_server(status="Offline")

		customer = self._get_or_create_customer()
		domain = self._get_or_create_domain()

		website = self._create_website(
			server=server.name,
			domain=domain.name,
			customer=customer.name,
			status="Active",
			envirnoment="Development"
		)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "c1a2b3c4",
			"status": "Requested",
		})

		with self.assertRaises(frappe.ValidationError):
			deployment.validate_server()

	def test_server_status_offline_creates_incident(self):
		"""Test that transitioning server status to Offline creates an Incident."""
		server = self.create_server(status="Online")
		server.status = "Offline"
		server.save(ignore_permissions=True)

		# Verify an incident was created
		incident = frappe.db.exists(
			"Incident",
			{
				"server": server.name,
				"category": "ServerDown",
			}
		)
		self.assertTrue(incident, "Incident should be automatically created when server goes Offline")
		if incident:
			self.cleanup_records.append(("Incident", incident))

	# =========================================================================
	# Duplicate Hostname Tests
	# =========================================================================

	def test_duplicate_hostname_prevention(self):
		"""Test that creating a server with a duplicate hostname raises an error."""
		unique_hostname = f"unique-host-{uuid.uuid4().hex[:8]}.example.com"
		self.create_server(hostname=unique_hostname)

		duplicate_server = frappe.get_doc({
			"doctype": "Server",
			"server_name": f"Server-Dup-{uuid.uuid4().hex[:8]}",
			"hostname": unique_hostname,
			"ip_address": "10.0.0.2",
			"status": "Online",
		})

		with self.assertRaises((frappe.DuplicateEntryError, frappe.ValidationError, frappe.UniqueValidationError)):
			duplicate_server.insert(ignore_permissions=True)

	# =========================================================================
	# Helper Methods
	# =========================================================================

	def _get_or_create_customer(self):
		cust_name = f"Cust-{uuid.uuid4().hex[:8]}"
		customer = frappe.get_doc({
			"doctype": "Customer_",
			"customer_name": cust_name,
			"status": "Active"
		})
		customer.insert(ignore_permissions=True)
		self.cleanup_records.append(("Customer_", customer.name))
		return customer

	def _get_or_create_domain(self):
		dom_name = f"dom-{uuid.uuid4().hex[:8]}.com"
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": dom_name,
			"registration_date": "2026-01-01",
			"expiry_date": "2027-01-01",
			"status": "Active"
		})
		domain.insert(ignore_permissions=True)
		self.cleanup_records.append(("Domain_", domain.name))
		return domain

	def _create_website(self, **kwargs):
		uid = uuid.uuid4().hex[:8]
		defaults = {
			"doctype": "Website_",
			"website_name": f"Site-{uid}",
			"framework": "Frappe",
			"repository_url": "https://github.com/example/repo",
			"repository_type": "GitHub",
			"production_branch": "main",
			"port": 8000,
			"status": "Active",
			"envirnoment": "Development",
		}
		defaults.update(kwargs)
		site = frappe.get_doc(defaults)
		site.insert(ignore_permissions=True)
		self.cleanup_records.append(("Website_", site.name))
		return site
