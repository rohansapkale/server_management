import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, today


class Domain_(Document):

	def validate(self):
		self.validate_dates()
		self.calculate_days_remaining()
		self.update_status()

	def validate_dates(self):
		if not self.registration_date or not self.expiry_date:
			return
		registration_date = getdate(self.registration_date)
		expiry_date = getdate(self.expiry_date)

		if expiry_date < registration_date:
			frappe.throw(
				"expiry date must be strictly greater than Registration Date."
			)
	def calculate_days_remaining(self):
		if not self.expiry_date:
			self.days_remaining = None
			return

		self.days_remaining = date_diff(
			getdate(self.expiry_date),
			getdate(today())
		)

	def update_status(self):
		if self.days_remaining is None:
			return

		if self.days_remaining < 0:
			self.status = "Expired"

		elif self.days_remaining <= 7:
			self.status = "Critical"

		elif self.days_remaining <= 30:
			self.status = "Warning"

		else:
			self.status = "Active"

