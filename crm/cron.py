from datetime import datetime
import requests

def log_crm_heartbeat():
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Optional: check GraphQL endpoint health
    try:
        res = requests.post("http://localhost:8000/graphql", json={"query": "{ hello }"})
        if res.ok:
            message = f"{timestamp} CRM is alive (GraphQL OK)\n"
        else:
            message = f"{timestamp} CRM is alive (GraphQL Error)\n"
    except Exception:
        message = f"{timestamp} CRM is alive (GraphQL Unreachable)\n"

    with open(log_file, "a") as f:
        f.write(message)

def update_low_stock():
    from datetime import datetime
    import requests

    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mutation = """
    mutation {
      updateLowStockProducts {
        success
        updatedProducts {
          name
          stock
        }
      }
    }
    """

    response = requests.post("http://localhost:8000/graphql", json={"query": mutation})
    data = response.json()

    with open(log_file, "a") as f:
        if data.get("data", {}).get("updateLowStockProducts", {}).get("success"):
            for product in data["data"]["updateLowStockProducts"]["updatedProducts"]:
                f.write(f"[{timestamp}] {product['name']} restocked to {product['stock']}\n")

