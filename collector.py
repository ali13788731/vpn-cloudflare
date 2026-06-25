import json
import base64
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
import jdatetime
import requests

# ==========================================
# 🌐 دامنه‌های چرخشی IRCF
# ==========================================
OPERATORS = {
    "MCI": "mci.ircf.space",       # همراه اول
    "MTN": "mtn.ircf.space",       # ایرانسل
    "MKH": "mkh.ircf.space"        # مخابرات
}

# لینک مستقیم مخزن yebekhe (میکس تمام پروتکل‌ها)
YEBEKHE_URL = "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix"

# ==========================================
# 🛠 توابع پردازش
# ==========================================
def get_tehran_time():
    """ دریافت تاریخ و ساعت دقیق تهران با در نظر گرفتن تایم‌زون """
    tehran_tz = ZoneInfo("Asia/Tehran")
    now_tehran = datetime.now(tehran_tz)
    return jdatetime.datetime.fromgregorian(datetime=now_tehran).strftime("%Y-%m-%d %H:%M")

def inject_clean_ip_vless(conf, operator_name, clean_domain, time_tag):
    """ تزریق دامنه تمیز به VLESS / VLESS (بدون دستکاری SNI) """
    try:
        parsed = urllib.parse.urlparse(conf)
        user_info = parsed.netloc.split('@')[0]
        port = parsed.port if parsed.port else 443
        
        # جایگذاری دامنه تمیز در آدرس، بدون تغییر در پارامترهای دیگر
        new_netloc = f"{user_info}@{clean_domain}:{port}"
        
        # اصلاح نام کانفیگ
        old_name = urllib.parse.unquote(parsed.fragment)
        short_name = old_name[:12] + ".." if len(old_name) > 12 else old_name
        new_name = f"IRCF-{operator_name} | {short_name} | {time_tag}"
        
        new_parsed = parsed._replace(netloc=new_netloc, fragment=urllib.parse.quote(new_name))
        return urllib.parse.urlunparse(new_parsed)
    except Exception:
        return None

def inject_clean_ip_vmess(conf, operator_name, clean_domain, time_tag):
    """ تزریق دامنه تمیز به VMESS """
    try:
        b64_str = conf[8:] + "=" * ((4 - len(conf[8:]) % 4) % 4)
        data = json.loads(base64.urlsafe_b64decode(b64_str).decode('utf-8'))
        
        # تغییر آدرس سرور به دامنه IRCF
        data['add'] = clean_domain
        
        # اصلاح نام
        old_name = data.get('ps', 'Server')
        short_name = old_name[:12] + ".." if len(old_name) > 12 else old_name
        data['ps'] = f"IRCF-{operator_name} | {short_name} | {time_tag}"
        
        new_b64 = base64.urlsafe_b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
        return "vmess://" + new_b64
    except Exception:
        return None

def fetch_yebekhe_configs():
    """ دانلود کانفیگ‌های تازه از Yebekhe """
    print("📥 Downloading fresh configs from yebekhe...")
    try:
        response = requests.get(YEBEKHE_URL, timeout=15)
        response.raise_for_status()
        
        text_data = response.text.strip()
        # دیکد کردن Base64 مخزن yebekhe
        try:
            text_data = base64.b64decode(text_data).decode('utf-8')
        except:
            pass
            
        lines = text_data.split('\n')
        print(f"✅ Downloaded {len(lines)} raw configs.")
        return lines
    except Exception as e:
        print(f"⚠️ Error downloading from yebekhe: {e}")
        return []

# ==========================================
# ⚙️ بدنه اصلی برنامه
# ==========================================
def main():
    time_tag = get_tehran_time()
    print(f"⏰ Start building routing configs at: {time_tag}")

    # ۱. دریافت کانفیگ‌های پایه
    raw_configs = fetch_yebekhe_configs()
    if not raw_configs:
        print("❌ Process aborted. No configs fetched.")
        return

    final_configs = {"MCI": [], "MTN": [], "MKH": []}
    
    # ۲. پردازش و تزریق دامنه برای هر اپراتور
    print("\n⚙️ Injecting IRCF domains...")
    for conf in raw_configs:
        conf = conf.strip()
        if not conf: continue
        
        for op_name, domain in OPERATORS.items():
            if conf.startswith("vless://") or conf.startswith("trojan://"):
                new_conf = inject_clean_ip_vless(conf, op_name, domain, time_tag)
                if new_conf: final_configs[op_name].append(new_conf)
                
            elif conf.startswith("vmess://"):
                new_conf = inject_clean_ip_vmess(conf, op_name, domain, time_tag)
                if new_conf: final_configs[op_name].append(new_conf)

    # ۳. ذخیره‌سازی در فایل‌های مجزا
    for op_name, configs in final_configs.items():
        # استخراج ۱۵۰ کانفیگ باکیفیت و اولیه برای جلوگیری از حجم نامعقول لینک
        selected_configs = configs[:150] 
        
        if selected_configs:
            content_str = "\n".join(selected_configs)
            encoded_content = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
            
            # فایل اصلی (Base64) برای کاربر
            with open(f"sub_{op_name.lower()}.txt", "w", encoding="utf-8") as f:
                f.write(encoded_content)
                
            # فایل کمکی برای دیدن ساختار کانفیگ‌ها در گیت‌هاب
            with open(f"sub_{op_name.lower()}_raw.txt", "w", encoding="utf-8") as f:
                f.write(content_str)
                
            print(f"✨ Saved {len(selected_configs)} optimized configs for {op_name}.")

if __name__ == '__main__':
    main()
