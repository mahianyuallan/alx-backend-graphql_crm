#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

LOG_FILE = "/tmp/order_reminders_log.txt"
ENDPOINT = "http://localhost:8000/graphql"

query = """
query RecentOrders($since: DateTime!) {
  orders(orderDate_Gte: $since) {
    id
    customer {
      email
    }
  }
}
"""

variables = {"since": (datetime.now() - timedelta(days=7)).isoformat()}

response = requests.post(ENDPOINT, json={"query": query, "variables": variables})
data = response.json()

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(LOG_FILE, "a") as f:
    for order in data.get("data", {}).get("orders", []):
        f.write(f"[{timestamp}] Reminder sent for order {order['id']} ({order['customer']['email']})\n")

print("Order reminders processed!")
