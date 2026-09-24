frappe.query_reports["Server Service Report"] = {
	filters: [
		{
			fieldname: "server",
			label: "Server",
			fieldtype:  "Link",
			options: "Server"
		}
	]
};