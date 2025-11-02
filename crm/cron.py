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
