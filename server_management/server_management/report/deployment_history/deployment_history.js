frappe.query_reports["Deployment History"] = {
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
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options: [
                "",
                "Requested",
                "Approved",
                "Running",
                "Successful",
                "Failed",
                "Cancelled",
                "Rolled Back"
            ].join("\n")
        },
        {
            fieldname: "deployment_type",
            label: "Deployment Type",
            fieldtype: "Select",
            options: [
                "",
                "Manual",
                "Automatic",
                "Rollback",
                "Scheduled"
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