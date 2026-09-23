
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

@frappe.whitelist()
def get_deployement_history(website=None, server= None, limit= 20):
    """ Return deployement history for a website or server. """
    filters = {}

    if website:
        filters["website"]= website
    if server:
        filters["server"]=server
    deployements = frappe.get_all(
        "Deployement",
        filters = filters,
        fields=[
            "name",
			"website",
			"server",
			"branch",
			"commit_id",
			"commit_message",
			"deployment_type",
			"requested_by",
			"approved_by",
			"deployment_date",
			"start_time",
			"end_time",
			"duration_seconds",
			"status",
			"rollback_required"
        ],
        order_by = "creation desc",
        limit_page_length=int(limit)
    )
    return deployement

@frappe.whitelist()
def create_deployement_request(payload):
    """Create a deployment request after pre-flight checks."""

    if isinstance(payload,str):
        payload = frappe.parse_json(payload)
    if not payload:
        frappe.throw("Deployment payload is required.")
    website = payload.get("website")
    server = payload.get("server")

    if not website:
        frappe.throw("website is required")
    if not server:
        frappe.throw("server is required")
    #check server
    server_status = frappe.db.get_value(
        "Server",
        server,
        "status"
    )
    if server_status in [
        "Offline",
        "Maintenance",
		"Decommissioned"
    ]:
        frappe.thorw(
            f"Deployment cannot be created because server"
            f"<b>{server}<b/> is <b>{server_status}<b/>."
        )

    #check website 
    website_status= frappe.db.get_value(
        "Website_",
        website,
        "status"
    )
        if server_status in [
		"Suspended",
		"Archived",
		"Inactive"
    ]:
        frappe.thorw(
            f"Deployment cannot be created because website"
            f"<b>{website}<b/> is <b>{website_status}<b/>."
        )

    #create edeployment
    deployement = frappe.get_doc({
        		"doctype": "Deployment",
		"website": website,
		"server": server,
		"repository_url": payload.get("repository_url"),
		"branch": payload.get("branch"),
		"commit_id": payload.get("commit_id"),
		"commit_message": payload.get("commit_message"),
		"deployment_type": payload.get(
			"deployment_type",
			"Manual"
		),
		"requested_by": frappe.session.user,
		"deployment_date": now_datetime(),
		"status": "Requested",
		"rollback_required": 0
    })

    deployement.insert()
    return{
        "success":True,
        "message":"Deployment request created successfully.",
        "deployment":deployement.name,
        "status":deployment.status
    }

@frappe.whitelist()
def get_dashboard_metrics():
    """Return executive dashboard KPI Metrics."""

    metrics = {
        "total_servers":frappe.db.count("Server"),
        "online_servers":frappe.db.count(
            "Server",
            {"status":"Online"}
        ),
        "total_websites":frappe.db.count("Website"),
        "active_websites":frappe.db.count(
            "Website",
            {"status":"Active"}
        ),
        		"expiring_domains": frappe.db.count(
			"Domain",
			{
				"status": ["in", ["Warning", "Critical"]]
			}
		),

		"open_incidents": frappe.db.count(
			"Incident",
			{
				"status": [
					"in",
					[
						"Open",
						"Assigned",
						"Investigating",
						"Monitoring"
					]
				]
			}
		),

		"failed_deployments": frappe.db.count(
			"Deployment",
			{"status": "Failed"}
		),

		"successful_deployments": frappe.db.count(
			"Deployment",
			{"status": "Successful"}
		)
    }
    metrics["generated_at"] = now_datetime()

    return metrics

