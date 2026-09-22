// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

frappe.ui.form.on("Server", {
    refresh(frm) {
        frm.set_indicator(
            frm.doc.status,
            get_status_indicator_color(frm.doc.status)
        );
        frm.add_custom_button(
            "View Hosted Websites",
            () => {
                frapp.set_route("List", "Website_", {
                    server: frm.doc.name
                });
            },
            "Quick Actions"
        );
        frm.add_custom_button(
            "View Services",
            () => {
                frappe.set_route("List", "Server Services", {
                    server: frm.doc.name
                });
            },
            "Quick Actions"
        );
        frm.add_custom_button(
            "Check Health",
            () => {
                check_server_health(frm);
            },
            "Quick Actions"
        );
    },
    status(frm) {
        frm.set_indicator(
            frm.doc.status,
            get_status_indicator_color(frm.doc.status)
        )
    }
});

function get_status_indicator_color(status) {
    switch (status) {
        case "Online":
            return "green"
        case "Offline":
            return "red";

        case "Maintenance":
            return "orange";

        case "Decommissioned":
            return "darkgrey";
        default:
            return "blue";
    }
}
function check_server_health(frm) {

	frappe.show_alert({
		message: `Checking health of ${frm.doc.name}...`,
		indicator: "blue"
	});

	frappe.call({
		method: "server_management.server_management.doctype.server.server.check_health",
		args: {
			server: frm.doc.name
		},

		callback: function (r) {

			if (r.message) {

				frappe.msgprint({
					title: "Server Health",
					message: r.message,
					indicator: "green"
				});

			}
		}
	});
}