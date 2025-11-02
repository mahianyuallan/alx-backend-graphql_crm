#!/bin/bash
# Script to delete inactive customers (no orders for the past year)

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

DELETED_COUNT=$(python3 manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff_date = timezone.now() - timedelta(days=365)
inactive = Customer.objects.filter(orders__isnull=True) | Customer.objects.exclude(orders__order_date__gte=cutoff_date)
count = inactive.count()
inactive.delete()
print(count)
")

echo \"[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers.\" >> $LOG_FILE
