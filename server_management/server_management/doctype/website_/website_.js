// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Website_", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Website", {

    refresh(frm) {

        if (frm.is_new()) {
            return;
        }

        frm.add_custom_button("View Server", function () {

            if (!frm.doc.server) {
                frappe.msgprint("No Server is linked.");
                return;
            }

            frappe.set_route(
                "Form",
                "Server",
                frm.doc.server
            );

        }, "Actions");


        frm.add_custom_button("Create Deployment", function () {

            frappe.new_doc("Deployment", {
                website: frm.doc.name,
                server: frm.doc.server
            });

        }, "Actions");


        frm.add_custom_button("View Deployments", function () {

            frappe.set_route(
                "List",
                "Deployment",
                {
                    website: frm.doc.name
                }
            );

        }, "Actions");


        frm.add_custom_button("View Backups", function () {

            frappe.set_route(
                "List",
                "Backup",
                {
                    website: frm.doc.name
                }
            );

        }, "Actions");

    }

});