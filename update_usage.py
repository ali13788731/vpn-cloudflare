import os
import requests
import re
import json
from datetime import datetime, timezone

CF_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")

url = "https://api.cloudflare.com/client/v4/graphql"
headers = {
    "Authorization": f"Bearer {CF_TOKEN}",
    "Content-Type": "application/json"
}

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

formatted_requests = "N/A"

try:
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    res_data = response.json()
    
    # چاپ دیتای دریافتی در لاگ برای عیب‌یابی (اگر مشکلی بود اینجا مشخص می‌شود)
    print("API Response:", json.dumps(res_data, indent=2))
    
    if 'errors' in res_data and res_data['errors']:
        print(f"❌ Error from Cloudflare API: {res_data['errors']}")
        formatted_requests = "API Error"
    else:
        # استخراج امن اطلاعات بدون کرش کردن
        accounts = res_data.get('data', {}).get('viewer', {}).get('accounts', [])
        if accounts:
            groups = accounts[0].get('workersInboundRequestsAdaptiveGroups', [])
            if groups:
                requests_count = groups[0].get('sum', {}).get('requests', 0)
                formatted_requests = f"{requests_count:,}"
            else:
                formatted_requests = "0" # هنوز مصرفی در امروز ثبت نشده است
        else:
            print("❌ Account ID not found or Token lacks permissions.")
            formatted_requests = "Auth/ID Error"

except Exception as e:
    print(f"❌ Python execution error: {e}")
    formatted_requests = "Script Error"

html_stats = f"""<div class="stat-box">
            <span class="label">تعداد کل درخواست‌ها (Requests)</span>
            <span class="value">{formatted_requests}</span>
        </div>
        <div class="footer">آخرین بروزرسانی: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC</div>
        """

try:
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    updated_html = re.sub(r".*?", html_stats, html_content, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(updated_html)
        
    print("✅ index.html updated successfully!")
except Exception as e:
    print(f"❌ Error writing to HTML file: {e}")
