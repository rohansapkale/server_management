# Copyright (c) 2026, Rohan Sapkale and Contributors
# See license.txt

import uuid
import frappe
from frappe.tests import IntegrationTestCase


class TestWebsite(IntegrationTestCase):
	"""
	Automated tests covering Website_ DocType:
	- Server binding requirement
	- Domain requirement for Production environment
	- Status checks and transition restrictions with active deployments
	- Decommissioned server binding prevention
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
			"server_name": f"Srv-{unique_id}",
			"hostname": f"srv-{unique_id}.example.com",
			"ip_address": "192.168.1.50",
			"status": "Online",
			"enviorment": "Development",
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		self.cleanup_records.append(("Server", doc.name))
		return doc

	def create_customer(self, **kwargs):
		unique_id = uuid.uuid4().hex[:8]
		defaults = {
			"doctype": "Customer_",
			"customer_name": f"Cust-{unique_id}",
			"status": "Active",
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		self.cleanup_records.append(("Customer_", doc.name))
		return doc

	def create_domain(self, **kwargs):
		unique_id = uuid.uuid4().hex[:8]
		defaults = {
			"doctype": "Domain_",
			"domain_name": f"site-{unique_id}.org",
			"registration_date": "2026-01-01",
			"expiry_date": "2027-01-01",
			"status": "Active",
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		self.cleanup_records.append(("Domain_", doc.name))
		return doc

	def create_website(self, **kwargs):
		unique_id = uuid.uuid4().hex[:8]
		defaults = {
			"doctype": "Website_",
			"website_name": f"Web-{unique_id}",
			"framework": "Frappe",
			"repository_url": "https://github.com/example/app",
			"repository_type": "GitHub",
			"production_branch": "main",
			"port": 8000,
			"status": "Active",
			"envirnoment": "Development",
		}
		defaults.update(kwargs)
		if "server" not in defaults:
			server = self.create_server()
			defaults["server"] = server.name
		if "customer" not in defaults:
			customer = self.create_customer()
			defaults["customer"] = customer.name
		if "domain" not in defaults:
			domain = self.create_domain()
			defaults["domain"] = domain.name

		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		self.cleanup_records.append(("Website_", doc.name))
		return doc

	# =========================================================================
	# Server Binding Requirement Tests
	# =========================================================================

	def test_server_binding_mandatory(self):
		"""Test that a Website cannot be created/validated without a Server binding."""
		domain = self.create_domain()
		customer = self.create_customer()

		website = frappe.get_doc({
			"doctype": "Website_",
			"website_name": f"No-Server-Site-{uuid.uuid4().hex[:8]}",
			"domain": domain.name,
			"customer": customer.name,
			"server": None,
			"framework": "Frappe",
			"repository_url": "https://github.com/example/app",
			"repository_type": "GitHub",
			"production_branch": "main",
			"port": 8000,
			"status": "Draft",
			"envirnoment": "Development",
		})

		with self.assertRaises(frappe.ValidationError):
			website.validate_server()

	def test_active_website_cannot_bind_to_decommissioned_server(self):
		"""Test that an Active Website cannot be linked to a Decommissioned Server."""
		decommissioned_server = self.create_server(status="Decommissioned")
		domain = self.create_domain()
		customer = self.create_customer()

		website = frappe.get_doc({
			"doctype": "Website_",
			"website_name": f"Decom-Site-{uuid.uuid4().hex[:8]}",
			"domain": domain.name,
			"customer": customer.name,
			"server": decommissioned_server.name,
			"framework": "Frappe",
			"repository_url": "https://github.com/example/app",
			"repository_type": "GitHub",
			"production_branch": "main",
			"port": 8000,
			"status": "Active",
			"envirnoment": "Development",
		})

		with self.assertRaises(frappe.ValidationError):
			website.validate_server()

	def test_active_website_bound_to_online_server_succeeds(self):
		"""Test that an Active Website bound to an Online Server passes validation."""
		online_server = self.create_server(status="Online")
		domain = self.create_domain()
		customer = self.create_customer()

		website = self.create_website(
			server=online_server.name,
			domain=domain.name,
			customer=customer.name,
			status="Active",
		)
		self.assertEqual(website.server, online_server.name)
		self.assertEqual(website.status, "Active")

	# =========================================================================
	# Domain Requirement for Production Tests
	# =========================================================================

	def test_production_website_requires_domain(self):
		"""Test that a Production Website must have a Domain specified."""
		server = self.create_server()
		customer = self.create_customer()

		website = frappe.get_doc({
			"doctype": "Website_",
			"website_name": f"Prod-No-Domain-{uuid.uuid4().hex[:8]}",
			"server": server.name,
			"customer": customer.name,
			"domain": None,
			"framework": "Frappe",
			"repository_url": "https://github.com/example/app",
			"repository_type": "GitHub",
			"production_branch": "main",
			"port": 8000,
			"status": "Draft",
			"envirnoment": "Production",
		})

		with self.assertRaises(frappe.ValidationError):
			website.validate_production()

	def test_production_website_with_domain_succeeds(self):
		"""Test that a Production Website with a Domain passes validation."""
		server = self.create_server()
		customer = self.create_customer()
		domain = self.create_domain()

		website = self.create_website(
			server=server.name,
			customer=customer.name,
			domain=domain.name,
			envirnoment="Production",
			status="Active",
		)
		self.assertEqual(website.domain, domain.name)
		self.assertEqual(website.envirnoment, "Production")

	# =========================================================================
	# Status Checks & Transition Tests
	# =========================================================================

	def test_status_transition_to_suspended_blocked_with_active_deployment(self):
		"""Test that Website status cannot be changed to Suspended when an active deployment exists."""
		server = self.create_server()
		website = self.create_website(server=server.name, status="Active")

		# Create an Active/Running Deployment for this website
		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "c1a2b3",
			"status": "Running",
			"approved_by": "Administrator",
		})
		deployment.insert(ignore_permissions=True)
		self.cleanup_records.append(("Deployment", deployment.name))

		# Attempt to change status to Suspended
		website.status = "Suspended"
		with self.assertRaises(frappe.ValidationError):
			website.validate_status_transition()

	def test_status_transition_to_archived_blocked_with_active_deployment(self):
		"""Test that Website status cannot be changed to Archived when an active deployment exists."""
		server = self.create_server()
		website = self.create_website(server=server.name, status="Active")

		# Create an Active/Running Deployment for this website
		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "c1a2b3",
			"status": "Running",
			"approved_by": "Administrator",
		})
		deployment.insert(ignore_permissions=True)
		self.cleanup_records.append(("Deployment", deployment.name))

		# Attempt to change status to Archived
		website.status = "Archived"
		with self.assertRaises(frappe.ValidationError):
			website.validate_status_transition()

	def test_status_transition_allowed_without_active_deployment(self):
		"""Test that Website status can be changed to Suspended/Archived when no active deployment exists."""
		website = self.create_website(status="Active")

		website.status = "Suspended"
		# Should not raise exception
		website.validate_status_transition()
		website.save(ignore_permissions=True)
		self.assertEqual(website.status, "Suspended")

		website.status = "Archived"
		website.validate_status_transition()
		website.save(ignore_permissions=True)
		self.assertEqual(website.status, "Archived")
