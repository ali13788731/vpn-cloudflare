import os
import requests
import json
from datetime import datetime, timezone

CF_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")

url = "https://api.cloudflare.com/client/v4/graphql"
headers = {
    "Authorization": f"Bearer {CF_TOKEN}",
    "Content-Type": "application/json"
}

today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

query = """
query GetWorkersMetrics($accountId: String!, $date: String!) {
  viewer {
    accounts(filter: { accountTag: $accountId }) {
      workersInboundRequests1d(limit: 1, filter: { date: $date }) {
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
    "date": today_date
}

formatted_requests = "N/A"

try:
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    res_data = response.json()
    
    print("API Response:", json.dumps(res_data, indent=2))
    
    if 'errors' in res_data and res_data['errors']:
        print(f"❌ Error from Cloudflare API: {res_data['errors']}")
        formatted_requests = "API Error"
    else:
        accounts = res_data.get('data', {}).get('viewer', {}).get('accounts', [])
        if accounts:
            groups = accounts[0].get('workersInboundRequests1d', [])
            if groups:
                requests_count = groups[0].get('sum', {}).get('requests', 0)
                formatted_requests = f"{requests_count:,}"
            else:
                formatted_requests = "0"
        else:
            formatted_requests = "Auth/ID Error"

except Exception as e:
    print(f"❌ Python execution error: {e}")
    formatted_requests = "Script Error"

html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد مصرف VPN</title>
    <style>
        body {{ font-family: Tahoma, Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .card {{ background-color: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-align: center; border: 1px solid #334155; width: 350px; }}
        h1 {{ font-size: 20px; margin-bottom: 25px; color: #38bdf8; }}
        .stat-box {{ background-color: #0f172a; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #1e293b; }}
        .label {{ font-size: 13px; color: #94a3b8; display: block; margin-bottom: 5px; }}
        .value {{ font-size: 24px; font-weight: bold; color: #f8fafc; }}
        .footer {{ font-size: 11px; color: #64748b; margin-top: 20px; direction: ltr; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>📊 وضعیت مصرف کلاودفلر امروز</h1>
        
        <div class="stat-box">
            <span class="label">تعداد کل درخواست‌ها (Requests)</span>
            <span class="value">{formatted_requests}</span>
        </div>
        <div class="footer">Last Update: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ index.html generated successfully!")
