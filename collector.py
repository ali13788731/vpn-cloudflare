import os
import urllib.parse
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
import jdatetime

# ==========================================
# 🚀 تنظیمات اختصاصی ورکر کلادفلر شما
# ==========================================
WORKER_DOMAIN = os.environ.get("WORKER_DOMAIN", "your-worker-name.your-subdomain.workers.dev")
WORKER_UUID = os.environ.get("WORKER_UUID", "00000000-0000-4000-8000-000000000000")

# ==========================================
# 🌐 دامنه‌های چرخشی IRCF برای هر اپراتور
# ==========================================
OPERATORS = {
    "mci": "mci.ircf.space",       # همراه اول
    "irancell": "mtn.ircf.space",  # ایرانسل
    "mkh": "mkh.ircf.space"        # مخابرات
}

# پورت‌های امن (HTTPS) کلادفلر
CF_PORTS = [443, 2053, 2083, 2087, 2096, 8443]

# ==========================================
# 🛠 توابع
# ==========================================
def get_persian_time():
    """ دریافت تاریخ و ساعت فعلی به وقت تهران """
    try:
        tehran_tz = ZoneInfo("Asia/Tehran")
        now_tehran = datetime.now(tehran_tz)
        return jdatetime.datetime.fromgregorian(datetime=now_tehran).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

def generate_worker_vless(address, port, operator_name, time_tag):
    """ ساخت لینک VLESS با استفاده از دامنه‌های چرخشی """
    
    # نام‌گذاری: 🚀 MyWorker [MCI] - Port:443 | 2026-06-25 12:00
    config_name = f"🚀 MyWorker [{operator_name.upper()}] - Port:{port} | {time_tag}"
    
    query = urllib.parse.urlencode({
        "encryption": "none",
        "security": "tls",
        "sni": WORKER_DOMAIN,
        "type": "ws",
        "host": WORKER_DOMAIN,
        "path": "/?ed=2048"
    })
    
    return f"vless://{WORKER_UUID}@{address}:{port}?{query}#{urllib.parse.quote(config_name)}"

# ==========================================
# ⚙️ بدنه اصلی
# ==========================================
def main():
    time_tag = get_persian_time()
    print(f"⏰ Start building configs at: {time_tag}")

    # پردازش برای هر اپراتور
    for op_name, domain in OPERATORS.items():
        configs = []
        print(f"\n📡 Generating configs for {op_name.upper()} using {domain} ...")
        
        # ساخت یک کانفیگ برای هر پورت کلادفلر
        for port in CF_PORTS:
            vless_link = generate_worker_vless(domain, port, op_name, time_tag)
            configs.append(vless_link)
            
        # ذخیره‌سازی در فایل‌های مجزا
        if configs:
            content_str = "\n".join(configs)
            encoded_content = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
            
            # ذخیره فایل Base64
            with open(f"sub_{op_name}.txt", "w", encoding="utf-8") as f:
                f.write(encoded_content)
                
            # ذخیره فایل Raw
            with open(f"sub_{op_name}_raw.txt", "w", encoding="utf-8") as f:
                f.write(content_str)
                
            print(f"✨ Success! Saved {len(configs)} configs for {op_name}.")

if __name__ == '__main__':
    main()
