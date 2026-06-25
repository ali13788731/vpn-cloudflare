import os
import requests
import json

# ۱. دریافت متغیرهای محیطی از گیت‌هاب اکشن
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")

if not CF_API_TOKEN or not CF_ACCOUNT_ID:
    print("❌ Error: CF_API_TOKEN or CF_ACCOUNT_ID missing!")
    exit(1)

url = "https://api.cloudflare.com/client/v4/graphql"

headers = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json"
}

# ۲. کوئری کامل و بدون سه نقطه (تعریف دقیق فیلدهایی که از کلودفلر می‌خواهید)
query = """
query GetWorkersAnalytics($accountTag: string) {
  viewer {
    accounts(filter: {accountTag: $accountTag}) {
      workersInvocationsAdaptive(limit: 10000) {
        sum {
          requests
          errors
        }
        dimensions {
          datetime
        }
      }
    }
  }
}
"""

# ۳. ارسال متغیر اکانت آیدی به شکل استاندارد
payload = {
    "query": query,
    "variables": {
        "accountTag": str(CF_ACCOUNT_ID)
    }
}

# ۴. دریافت اطلاعات
response = requests.post(url, headers=headers, json=payload)
data = response.json()

# ۵. مدیریت خطاها
if "errors" in data and data["errors"]:
    print(f"❌ Error from Cloudflare API: {data['errors']}")
    exit(1)

print("✅ Data fetched successfully!")

# ==========================================
# کدهای مربوط به پردازش دیتا و ساخت فایل index.html
# خودتان را از اینجا به بعد قرار دهید...
# ==========================================
