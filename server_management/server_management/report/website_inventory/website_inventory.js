frappe.query_reports["Website Inventory"] = {
	filters: [
		{
			fieldname: "environment",
			label: "Environment",
			fieldtype: "Select",
			options: "\nDevelopment\nStaging\nProduction"
		}
	]
};