# Copyright (c) 2026, Rohan Sapkale and Contributors
# See license.txt

import uuid
import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, getdate, today


class TestDomain(IntegrationTestCase):
	"""
	Automated tests covering Domain_ DocType:
	- Unique domain constraint
	- Expiry date validation (expiry > registration date)
	- Remaining days calculation
	- Dynamic status update (Expired, Critical, Warning, Active)
	"""

	def setUp(self):
		frappe.db.rollback()
		self.cleanup_records = []

	def tearDown(self):
		for doctype, name in reversed(self.cleanup_records):
			if frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
		frappe.db.rollback()

	def create_domain(self, **kwargs):
		unique_id = uuid.uuid4().hex[:8]
		defaults = {
			"doctype": "Domain_",
			"domain_name": f"test-domain-{unique_id}.com",
			"registration_date": "2026-01-01",
			"expiry_date": "2027-01-01",
			"status": "Active",
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		self.cleanup_records.append(("Domain_", doc.name))
		return doc

	# =========================================================================
	# Unique Domain Constraint Tests
	# =========================================================================

	def test_unique_domain_constraint(self):
		"""Test that duplicate domain names cannot be inserted."""
		unique_domain = f"unique-domain-{uuid.uuid4().hex[:8]}.com"
		self.create_domain(domain_name=unique_domain)

		duplicate_domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": unique_domain,
			"registration_date": "2026-01-01",
			"expiry_date": "2027-01-01",
		})

		with self.assertRaises((frappe.DuplicateEntryError, frappe.ValidationError)):
			duplicate_domain.insert(ignore_permissions=True)

	# =========================================================================
	# Expiry Date Validation Tests
	# =========================================================================

	def test_expiry_date_after_registration_date_passes(self):
		"""Test that expiry date greater than registration date passes validation."""
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"valid-dates-{uuid.uuid4().hex[:8]}.com",
			"registration_date": "2026-01-01",
			"expiry_date": "2026-06-01",
		})
		# Should not throw
		domain.validate_dates()

	def test_expiry_date_before_registration_date_fails(self):
		"""Test that expiry date before registration date raises ValidationError."""
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"invalid-dates-{uuid.uuid4().hex[:8]}.com",
			"registration_date": "2026-06-01",
			"expiry_date": "2026-01-01",
		})
		with self.assertRaises(frappe.ValidationError):
			domain.validate_dates()

	def test_expiry_date_equal_registration_date_fails(self):
		"""Test that expiry date equal to registration date raises ValidationError (must be strictly greater)."""
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"equal-dates-{uuid.uuid4().hex[:8]}.com",
			"registration_date": "2026-01-01",
			"expiry_date": "2026-01-01",
		})
		with self.assertRaises(frappe.ValidationError):
			domain.validate_dates()

	# =========================================================================
	# Remaining Days Calculation & Status Update Tests
	# =========================================================================

	def test_calculate_days_remaining(self):
		"""Test that days_remaining is calculated correctly against current date."""
		curr_today = getdate(today())
		expiry_in_45_days = add_days(curr_today, 45)

		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"calc-days-{uuid.uuid4().hex[:8]}.com",
			"registration_date": add_days(curr_today, -100),
			"expiry_date": expiry_in_45_days,
		})
		domain.calculate_days_remaining()
		self.assertEqual(domain.days_remaining, 45)

	def test_status_update_expired_when_days_negative(self):
		"""Test status is set to 'Expired' when days_remaining < 0."""
		curr_today = getdate(today())
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"expired-{uuid.uuid4().hex[:8]}.com",
			"registration_date": add_days(curr_today, -400),
			"expiry_date": add_days(curr_today, -5),
		})
		domain.calculate_days_remaining()
		domain.update_status()
		self.assertEqual(domain.status, "Expired")

	def test_status_update_critical_when_days_within_7(self):
		"""Test status is set to 'Critical' when 0 <= days_remaining <= 7."""
		curr_today = getdate(today())
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"critical-{uuid.uuid4().hex[:8]}.com",
			"registration_date": add_days(curr_today, -300),
			"expiry_date": add_days(curr_today, 5),
		})
		domain.calculate_days_remaining()
		domain.update_status()
		self.assertEqual(domain.status, "Critical")

	def test_status_update_warning_when_days_within_30(self):
		"""Test status is set to 'Warning' when 8 <= days_remaining <= 30."""
		curr_today = getdate(today())
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"warning-{uuid.uuid4().hex[:8]}.com",
			"registration_date": add_days(curr_today, -200),
			"expiry_date": add_days(curr_today, 20),
		})
		domain.calculate_days_remaining()
		domain.update_status()
		self.assertEqual(domain.status, "Warning")

	def test_status_update_active_when_days_greater_than_30(self):
		"""Test status is set to 'Active' when days_remaining > 30."""
		curr_today = getdate(today())
		domain = frappe.get_doc({
			"doctype": "Domain_",
			"domain_name": f"active-{uuid.uuid4().hex[:8]}.com",
			"registration_date": add_days(curr_today, -50),
			"expiry_date": add_days(curr_today, 90),
		})
		domain.calculate_days_remaining()
		domain.update_status()
		self.assertEqual(domain.status, "Active")
