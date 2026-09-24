# Copyright (c) 2026, Rohan Sapkale and Contributors
# See license.txt

import uuid
import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_to_date, now_datetime


class TestDeployment(IntegrationTestCase):
	"""
	Automated tests covering Deployment DocType:
	- Offline server blocking
	- Maintenance server blocking
	- Suspended / Archived website blocking
	- Production approval requirement for Running deployments
	- Duration calculation and audit logs
	- Incident creation on failed deployment
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
			"server_name": f"Deploy-Srv-{unique_id}",
			"hostname": f"srv-dep-{unique_id}.example.com",
			"ip_address": "192.168.1.80",
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
			"customer_name": f"Cust-Dep-{unique_id}",
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
			"domain_name": f"dep-{unique_id}.org",
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
			"website_name": f"Web-Dep-{unique_id}",
			"framework": "Frappe",
			"repository_url": "https://github.com/example/deploy-app",
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
	# Offline Server Blocking Tests
	# =========================================================================

	def test_offline_server_blocks_deployment(self):
		"""Test that deployment cannot proceed when linked server is Offline."""
		offline_server = self.create_server(status="Offline")
		website = self.create_website(server=offline_server.name)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": offline_server.name,
			"commit_id": "commit-001",
			"status": "Requested",
		})

		with self.assertRaises(frappe.ValidationError):
			deployment.validate_server()

	# =========================================================================
	# Maintenance Server Blocking Tests
	# =========================================================================

	def test_maintenance_server_blocks_deployment(self):
		"""Test that deployment cannot proceed when linked server is in Maintenance."""
		maint_server = self.create_server(status="Maintenance")
		website = self.create_website(server=maint_server.name)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": maint_server.name,
			"commit_id": "commit-002",
			"status": "Requested",
		})

		with self.assertRaises(frappe.ValidationError):
			deployment.validate_server()

	def test_decommissioned_server_blocks_deployment(self):
		"""Test that deployment cannot proceed when linked server is Decommissioned."""
		decom_server = self.create_server(status="Decommissioned")
		website = self.create_website(server=decom_server.name, status="Draft")

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": decom_server.name,
			"commit_id": "commit-003",
			"status": "Requested",
		})

		with self.assertRaises(frappe.ValidationError):
			deployment.validate_server()

	def test_online_server_allows_deployment(self):
		"""Test that deployment proceeds when linked server is Online."""
		online_server = self.create_server(status="Online")
		website = self.create_website(server=online_server.name)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": online_server.name,
			"commit_id": "commit-004",
			"status": "Requested",
		})
		# Should not raise exception
		deployment.validate_server()

	# =========================================================================
	# Suspended / Archived Website Blocking Tests
	# =========================================================================

	def test_suspended_website_blocks_deployment(self):
		"""Test that deployment cannot proceed when linked website is Suspended."""
		server = self.create_server(status="Online")
		website = self.create_website(server=server.name, status="Suspended")

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "commit-005",
			"status": "Requested",
		})

		with self.assertRaises(frappe.ValidationError):
			deployment.validate_website()

	def test_archived_website_blocks_deployment(self):
		"""Test that deployment cannot proceed when linked website is Archived."""
		server = self.create_server(status="Online")
		website = self.create_website(server=server.name, status="Archived")

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "commit-006",
			"status": "Requested",
		})

		with self.assertRaises(frappe.ValidationError):
			deployment.validate_website()

	def test_active_website_allows_deployment(self):
		"""Test that deployment proceeds when linked website is Active."""
		server = self.create_server(status="Online")
		website = self.create_website(server=server.name, status="Active")

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "commit-007",
			"status": "Requested",
		})
		# Should not raise exception
		deployment.validate_website()

	# =========================================================================
	# Production Approval Requirement Tests
	# =========================================================================

	def test_production_deployment_running_without_approval_blocked(self):
		"""Test that moving a Production deployment to 'Running' without approval is blocked."""
		server = self.create_server(status="Online")
		domain = self.create_domain()
		website = self.create_website(
			server=server.name,
			domain=domain.name,
			envirnoment="Production",
			status="Active",
		)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "commit-008",
			"status": "Running",
			"approved_by": None,
		})

		with self.assertRaises(frappe.ValidationError):
			deployment.validate_production_approval()

	def test_production_deployment_running_with_approval_succeeds(self):
		"""Test that moving a Production deployment to 'Running' with approval succeeds."""
		server = self.create_server(status="Online")
		domain = self.create_domain()
		website = self.create_website(
			server=server.name,
			domain=domain.name,
			envirnoment="Production",
			status="Active",
		)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "commit-009",
			"status": "Running",
			"approved_by": "Administrator",
		})
		# Should not throw
		deployment.validate_production_approval()

	def test_non_production_deployment_running_without_approval_succeeds(self):
		"""Test that a Development deployment can be moved to 'Running' without approval."""
		server = self.create_server(status="Online")
		website = self.create_website(
			server=server.name,
			envirnoment="Development",
			status="Active",
		)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"website": website.name,
			"server": server.name,
			"commit_id": "commit-010",
			"status": "Running",
			"approved_by": None,
		})
		# Should not throw
		deployment.validate_production_approval()

	# =========================================================================
	# Duration & Audit Log Tests
	# =========================================================================

	def test_deployment_duration_calculation(self):
		"""Test calculation of deployment duration from start_time and end_time."""
		start = now_datetime()
		end = add_to_date(start, seconds=125)

		deployment = frappe.get_doc({
			"doctype": "Deployment",
			"start_time": start,
			"end_time": end,
		})
		deployment.calculate_duration()
		self.assertEqual(deployment.duration_seconds, 125)
