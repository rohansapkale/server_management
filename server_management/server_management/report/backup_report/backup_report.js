// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt
frappe.query_reports["Backup Report"] = {
	filters: [
		{
			fieldname: "server",
			label: "Server",
			fieldtype: "Link",
			options: "Server"
		},
		{
			fieldname: "website",
			label: "Website",
			fieldtype: "Link",
			options: "Website"
		},
		{
			fieldname: "backup_type",
			label: "Backup Type",
			fieldtype: "Select",
			options: [
				"",
				"Database",
				"Files",
				"Full",
				"Configuration"
			].join("\n")
		},
		{
			fieldname: "status",
			label: "Status",
			fieldtype: "Select",
			options: [
				"",
				"Scheduled",
				"Running",
				"Successful",
				"Failed",
				"Deleted"
			].join("\n")
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