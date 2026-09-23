import frappe


@frappe.whitelist()
def get_server_status(server):
    if not server:
        frappe.throw("Server is required")

    if not frappe.db.exists("Server", server):
        frappe.throw("Server not found")

    server_doc = frappe.get_doc("Server", server)

    websites = frappe.get_all(
        "Website",
        filters={"server": server},
        fields=["name", "website_name", "domain", "environment", "status"]
    )

    services = frappe.get_all(
        "Server Service",
        filters={"server": server},
        fields=["name", "service_name", "status", "version"]
    )

    telemetry = frappe.get_all(
        "Server Telemetry",
        filters={"server": server},
        fields=["cpu_usage", "ram_usage", "disk_usage", "checked_at"],
        order_by="checked_at desc",
        limit_page_length=1
    )

    return {
        "server": server_doc.name,
        "status": server_doc.status,
        "environment": server_doc.environment,
        "specifications": {
            "cpu": server_doc.cpu,
            "ram": server_doc.ram,
            "storage": server_doc.storage,
            "operating_system": server_doc.operating_system
        },
        "hosted_websites": websites,
        "services": services,
        "latest_telemetry": telemetry[0] if telemetry else None
        
    }
    import frappe


@frappe.whitelist()
def get_website_details(website):
    if not website:
        frappe.throw("Website is required")

    if not frappe.db.exists("Website", website):
        frappe.throw("Website not found")

    website_doc = frappe.get_doc("Website", website)

    deployments = frappe.get_all(
        "Deployment",
        filters={"website": website},
        fields=[
            "name",
            "status",
            "deployment_date",
            "duration",
            "version"
        ],
        order_by="deployment_date desc"
    )

    backups = frappe.get_all(
        "Backup",
        filters={"website": website},
        fields=[
            "name",
            "backup_date",
            "status",
            "backup_size",
            "backup_location"
        ],
        order_by="backup_date desc"
    )

    return {
        "website": website_doc.name,
        "metadata": {
            "website_name": website_doc.website_name,
            "customer": website_doc.customer,
            "server": website_doc.server,
            "environment": website_doc.environment,
            "framework": website_doc.framework,
            "repository_url": website_doc.repository_url,
            "repository_type": website_doc.repository_type,
            "production_branch": website_doc.production_branch,
            "port": website_doc.port
        },
        "active_domain": website_doc.domain,
        "ssl_status": website_doc.ssl_status,
        "deployment_history": deployments,
        "backups": backups
    }
    import frappe


@frappe.whitelist()
def get_available_servers(environment=None):
    filters = {
        "status": "Available"
    }

    if environment:
        filters["environment"] = environment

    servers = frappe.get_all(
        "Server",
        filters=filters,
        fields=[
            "name",
            "server_name",
            "environment",
            "status",
            "ip_address",
            "provider",
            "cpu",
            "ram",
            "storage"
        ]
    )

    return servers