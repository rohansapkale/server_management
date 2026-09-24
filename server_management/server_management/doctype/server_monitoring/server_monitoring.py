import frappe
from frappe.model.document import Document


class ServerMonitoring(Document):

    def validate(self):
        self.set_status()

    def set_status(self):
        cpu = self.cpu_usage or 0
        ram = self.ram_usage or 0
        disk = self.disk_usage or 0

        if cpu > 95 or disk > 90:
            self.status = "Critical"

        elif cpu > 80 or ram > 80 or disk > 80:
            self.status = "Warning"

        else:
            self.status = "Normal"