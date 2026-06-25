import os
import requests
import re
from datetime import datetime, timezone

CF_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")

url = "https://api.cloudflare.com/client/v4/graphql"
headers = {
    "Authorization": f"Bearer {CF_TOKEN}",
    "Content-Type": "application/json"
}

# زمان شروع امروز به وقت UTC
start_of_today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

query = """
query GetWorkersMetrics($accountId: String!, $timeStart: String!) {
  viewer {
    accounts(filter: { accountTag: $accountId }) {
      workersInboundRequestsAdaptiveGroups(limit: 1, filter: { datetime_geq: $timeStart }) {
        sum {
          requests
        }
      }
    }
  }
}
"""

variables = {
    "accountId": CF_ACCOUNT_ID,
    "timeStart": start_of_today
}

try:
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    res_data = response.json()
    requests_count = res_data['data']['viewer']['accounts'][0]['workersInboundRequestsAdaptiveGroups'][0]['sum']['requests']
    formatted_requests = f"{requests_count:,}"
except Exception as e:
    print(f"Error: {e}")
    formatted_requests = "N/A"

# ساختار جدید اچ‌تی‌ام‌ال برای تزریق به فایل اصلی
html_stats = f"""<div class="stat-box">
            <span class="label">تعداد کل درخواست‌ها (Requests)</span>
            <span class="value">{formatted_requests}</span>
        </div>
        <div class="footer">آخرین بروزرسانی: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC</div>
        """

# بازنویسی کامپوننت آمار در فایل index.html
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

updated_html = re.sub(r".*?", html_stats, html_content, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(updated_html)

print("index.html updated!")
