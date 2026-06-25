import os
import requests
from datetime import datetime, timezone

# خواندن متغیرها از سیکرت‌های گیت‌هاب
CF_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")

url = "https://api.cloudflare.com/client/v4/graphql"
headers = {
    "Authorization": f"Bearer {CF_TOKEN}",
    "Content-Type": "application/json"
}

# دریافت تاریخ امروز برای فیلتر کردن آمار از ابتدای روز
start_of_today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

# کوئری GraphQL برای گرفتن تعداد ریکوئست‌های ورکرها
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
except Exception:
    requests_count = "N/A"

# ساخت استایل متنی برای قرار گرفتن در ریپازیتوری
stats_text = f"""### 📊 Cloudflare VPN Usage (Today)
- **Total Requests:** `{requests_count:,}`
- **Last Updated:** `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}`
"""

# خواندن و آپدیت کردن فایل README
with open("README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()

import re
updated_readme = re.sub(r".*?", stats_text, readme_content, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated_readme)

print("README.md updated successfully!")
