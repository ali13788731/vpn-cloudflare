import os
import requests
from datetime import datetime

# ==========================================
# ۱. دریافت متغیرهای محیطی
# ==========================================
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")

if not CF_API_TOKEN or not CF_ACCOUNT_ID:
    print("❌ Error: CF_API_TOKEN or CF_ACCOUNT_ID missing!")
    exit(1)

# ==========================================
# ۲. تنظیمات مربوط به API کلودفلر
# ==========================================
url = "https://api.cloudflare.com/client/v4/graphql"

headers = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json"
}

# محاسبه تاریخ برای "امروز" (بامداد امروز به وقت UTC)
now_utc = datetime.utcnow()
start_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')

query = """
query GetWorkersAnalytics($accountTag: string, $startDate: string) {
  viewer {
    accounts(filter: {accountTag: $accountTag}) {
      workersInvocationsAdaptive(limit: 10000, filter: {datetime_geq: $startDate}) {
        sum {
          requests
          errors
        }
      }
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {
        "accountTag": str(CF_ACCOUNT_ID),
        "startDate": start_date
    }
}

# ==========================================
# ۳. ارسال درخواست و دریافت اطلاعات
# ==========================================
response = requests.post(url, headers=headers, json=payload)
data = response.json()

if "errors" in data and data["errors"]:
    print(f"❌ Error from Cloudflare API: {data['errors']}")
    exit(1)

print("✅ Data fetched successfully!")

# ==========================================
# ۴. استخراج مقادیر از دیتای دریافتی
# ==========================================
try:
    account_data = data["data"]["viewer"]["accounts"][0]
    invocations = account_data.get("workersInvocationsAdaptive", [])
    
    if invocations:
        requests_count = invocations[0]["sum"]["requests"]
        errors_count = invocations[0]["sum"]["errors"]
    else:
        requests_count = 0
        errors_count = 0
        
except (KeyError, IndexError) as e:
    print(f"❌ Error parsing data structure: {e}")
    requests_count = 0
    errors_count = 0

print(f"📊 Today's Requests: {requests_count} | Errors: {errors_count}")

# ==========================================
# ۵. ساخت فایل index.html با آمارهای جدید
# ==========================================
html_content = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد آمار کلودفلر</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1e1e2f;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .card {{
            background-color: #2a2a40;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            text-align: center;
            width: 300px;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #f39c12;
        }}
        .stat {{
            font-size: 20px;
            margin: 15px 0;
        }}
        .number-requests {{
            color: #3498db;
            font-weight: bold;
            font-size: 28px;
        }}
        .number-errors {{
            color: #e74c3c;
            font-weight: bold;
            font-size: 28px;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 12px;
            color: #888;
        }}
    </style>
</head>
<body>

    <div class="card">
        <h1>📊 آمار امروز ورکر</h1>
        
        <div class="stat">
            تعداد درخواست‌ها (Today): <br>
            <span class="number-requests">{requests_count:,}</span>
        </div>
        
        <div class="stat">
            تعداد خطاها (Today): <br>
            <span class="number-errors">{errors_count:,}</span>
        </div>

        <div class="footer">
            آخرین بروزرسانی: <br>
            {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC
        </div>
    </div>

</body>
</html>
"""

# ذخیره کردن فایل
with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("✅ index.html generated successfully!")
