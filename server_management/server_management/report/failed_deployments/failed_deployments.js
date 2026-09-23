// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

frappe.query_reports["Failed Deployments"] = {
	filters: [
		{
			fieldname: "website",
			label: "Website",
			fieldtype: "Link",
			options: "Website"
		},
		{
			fieldname: "server",
			label: "Server",
			fieldtype: "Link",
			options: "Server"
		},
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			default: frappe.datetime.month_start()
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			default: frappe.datetime.month_end()
		}
	]
};
