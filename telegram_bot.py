import requests
from bs4 import BeautifulSoup
import time
import datetime
import telebot
import re

# إعدادات البوت
TOKEN = '8566644337:AAHA1kwjhaUYPrrFiupYy0yssDoz5OmRyG0'
CHANNEL_ID = '@FarawlaShop'
bot = telebot.TeleBot(TOKEN)

def get_sp_today_data():
    url = "https://sp-today.com/ar/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = {'currencies': []}

        # استخراج العملات من الروابط (a tags) لأن الموقع يستخدمها بدلاً من الجداول التقليدية أحياناً
        all_links = soup.find_all('a')
        
        # قائمة العملات المستهدفة
        target_currencies = {
            'USD': 'دولار أمريكي',
            'EUR': 'يورو',
            'TRY': 'ليرة تركية',
            'SAR': 'ريال سعودي',
            'AED': 'درهم إماراتي',
            'EGP': 'جنيه مصري',
            'GBP': 'جنيه إسترليني',
            'KWD': 'دينار كويتي',
            'JOD': 'دينار أردني'
        }

        found_currencies = set()

        for link in all_links:
            text = link.get_text(separator="\n").strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # البحث عن العملات في النصوص
            for code, name in target_currencies.items():
                if code in lines and code not in found_currencies:
                    # هيكل البيانات المتوقع: [CODE, NAME, BUY, SELL, CHANGE]
                    # مثال: ['USD', 'دولار أمريكي', '12,280', '12,330', '+0.00%']
                    if len(lines) >= 4:
                        buy = lines[2]
                        sell = lines[3]
                        
                        # التأكد أن القيم أرقام
                        if re.search(r'\d', buy) and re.search(r'\d', sell):
                            data['currencies'].append({
                                'name': f"{name} ({code})",
                                'buy': buy,
                                'sell': sell
                            })
                            found_currencies.add(code)
                            if code == 'USD':
                                data['usd_sell'] = sell

        # استخراج الذهب
        for link in all_links:
            text = link.get_text(separator="\n").strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if '21K' in text and len(lines) >= 5:
                data['gold_21'] = lines[4]
            elif '18K' in text and len(lines) >= 5:
                data['gold_18'] = lines[4]
            elif 'أونصة الذهب' in text:
                parts = re.findall(r'[\d,.]+', text)
                if parts: data['gold_ounce_usd'] = parts[0]

        # استخراج المحروقات
        for link in all_links:
            text = link.get_text(separator="\n").strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if 'بنزين' in text and len(lines) >= 4:
                data['fuel_gasoline'] = lines[3]
            elif 'مازوت' in text and len(lines) >= 4:
                data['fuel_diesel'] = lines[3]
            elif 'غاز' in text and len(lines) >= 4:
                data['fuel_gas'] = lines[3]

        data['date'] = datetime.datetime.now().strftime("%Y-%m-%d | %I:%M %p")
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def format_message(data):
    def to_new(val_str):
        try:
            # إزالة الفواصل والكلمات الزائدة مثل "ل.س"
            clean_val = re.sub(r'[^\d.]', '', val_str.replace(',', ''))
            val = float(clean_val)
            return f"{val/100:,.2f}"
        except: return "0.00"

    msg = f"🇸🇾 *نشرة أسعار الصرف والذهب في سوريا* 🇸🇾\n"
    msg += f"⏰ `{data['date']}`\n\n"
    
    if data['currencies']:
        msg += f"💰 *أسعار العملات (شراء | مبيع):*\n"
        msg += f"━━━━━━━━━━━━━━━━━━\n"
        for curr in data['currencies']:
            msg += f"🔹 *{curr['name']}:*\n"
            msg += f"  - القديم: {curr['buy']} | {curr['sell']} ل.س\n"
            msg += f"  - الجديد: `{to_new(curr['buy'])}` | `{to_new(curr['sell'])}` ل.س\n\n"
    
    msg += f"✨ *أسعار الذهب:*\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    if 'gold_21' in data:
        msg += f"🔸 عيار 21: {data['gold_21']} ل.س (`{to_new(data['gold_21'])}` جديد)\n"
    if 'gold_18' in data:
        msg += f"🔸 عيار 18: {data['gold_18']} ل.س (`{to_new(data['gold_18'])}` جديد)\n"
    if 'gold_ounce_usd' in data:
        msg += f"🌍 الأونصة: `${data['gold_ounce_usd']}`\n"
    msg += "\n"
    
    fuel_msg = ""
    if 'fuel_gasoline' in data:
        fuel_msg += f"⛽ بنزين: {data['fuel_gasoline']}\n"
    if 'fuel_diesel' in data:
        fuel_msg += f"🛢️ مازوت: {data['fuel_diesel']}\n"
    if 'fuel_gas' in data:
        fuel_msg += f"🔵 غاز: {data['fuel_gas']}\n"
    
    if fuel_msg:
        msg += f"⛽ *المحروقات والطاقة:*\n"
        msg += f"━━━━━━━━━━━━━━━━━━\n"
        msg += fuel_msg + "\n"
    
    msg += f"📢 *تابعونا عبر منصاتنا:*\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🔗 *تلجرام:*\nhttps://t.me/FarawlaShop\n\n"
    msg += f"🔗 *واتساب:*\nhttps://whatsapp.com/channel/0029VaQSQveCRs1vibyRZp3A\n\n"
    msg += f"🔗 *فيسبوك:*\nhttps://www.facebook.com/profile.php?id=61584349121096\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━"
    return msg

def main():
    print("Checking for updates...")
    data = get_sp_today_data()
    if data:
        message = format_message(data)
        try:
            # استخدام parse_mode='Markdown' لجعل الرسالة احترافية
            bot.send_message(CHANNEL_ID, message, parse_mode='Markdown', disable_web_page_preview=True)
            print("Update sent to channel!")
        except Exception as e:
            # في حال فشل الماركدوان، نرسل نص عادي
            print(f"Markdown failed, sending plain text. Error: {e}")
            bot.send_message(CHANNEL_ID, message.replace('*', '').replace('`', ''))
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()
