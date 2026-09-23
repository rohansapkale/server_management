frappe.query_reports["Incident Report"] = {
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
            fieldname: "priority",
            label: "Priority",
            fieldtype: "Select",
            options: [
                "",
                "Low",
                "Medium",
                "High",
                "Critical"
            ].join("\n")
        },
        {
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options: [
                "",
                "Open",
                "Assigned",
                "Investigating",
                "Monitoring",
                "Resolved",
                "Closed"
            ].join("\n")
        },
        {
            fieldname: "assigned_to",
            label: "Assigned To",
            fieldtype: "Link",
            options: "User"
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