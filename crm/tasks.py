from celery import shared_task
import requests
from datetime import datetime

@shared_task
def generate_crm_report():
    """
    Fetches CRM summary data (customers, orders, revenue)
    via GraphQL and logs it to /tmp/crm_report_log.txt
    """
    endpoint = "http://localhost:8000/graphql"

    query = """
    query {
        customersCount
        ordersCount
        totalRevenue
    }
    """

    try:
        response = requests.post(endpoint, json={"query": query})
        data = response.json().get("data", {})

        customers = data.get("customersCount", 0)
        orders = data.get("ordersCount", 0)
        revenue = data.get("totalRevenue", 0.0)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(log_line)

        print("CRM report generated successfully!")

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()} - Error generating report: {str(e)}\n")
