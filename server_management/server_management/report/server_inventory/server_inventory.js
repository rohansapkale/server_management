frappe.query_reports["Server Inventory"] = {
	filters: [
		{
			fieldname: "environment",
			label: "Environment",
			fieldtype: "Select",
			options: "\nDevelopment\nStaging\nProduction"
		}
	]
};