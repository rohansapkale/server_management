import frappe 
from frappe.utils import now_datetime

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