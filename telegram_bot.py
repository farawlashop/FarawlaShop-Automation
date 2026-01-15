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

        # استخراج كافة العملات من الجدول
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                currency_name = cols[0].get_text().strip()
                buy = cols[1].get_text().strip()
                sell = cols[2].get_text().strip()
                
                # تنظيف الاسم من الرموز والكلمات الزائدة
                clean_name = currency_name.replace('USD', '').replace('EUR', '').replace('TRY', '').strip()
                
                currency_info = {
                    'name': currency_name,
                    'buy': buy,
                    'sell': sell
                }
                data['currencies'].append(currency_info)
                
                # حفظ الدولار بشكل خاص للحسابات
                if 'USD' in currency_name or 'دولار' in currency_name:
                    data['usd_sell'] = sell

        # استخراج الذهب
        gold_items = soup.find_all('a')
        for item in gold_items:
            text = item.get_text()
            if '21K' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 4: data['gold_21'] = parts[3]
            elif '18K' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 4: data['gold_18'] = parts[3]
            elif 'أونصة الذهب' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 1: data['gold_ounce_usd'] = parts[0]

        # استخراج المحروقات
        fuel_items = soup.find_all('a')
        for item in fuel_items:
            text = item.get_text()
            if 'بنزين' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 2: data['fuel_gasoline'] = parts[1]
            elif 'مازوت' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 2: data['fuel_diesel'] = parts[1]
            elif 'غاز' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 2: data['fuel_gas'] = parts[1]

        data['date'] = datetime.datetime.now().strftime("%Y-%m-%d | %I:%M %p")
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def format_message(data):
    def to_new(val_str):
        try:
            val = float(val_str.replace(',', ''))
            return f"{val/100:,.2f}"
        except: return "0.00"

    def to_usd_price(val_str, usd_sell_str):
        try:
            val = float(val_str.replace(',', ''))
            usd = float(usd_sell_str.replace(',', ''))
            return f"{val/usd:,.2f}"
        except: return "0.00"

    usd_sell = data.get('usd_sell', '12,330')

    msg = f"🇸🇾 نشرة أسعار الصرف والذهب في سوريا 🇸🇾\n"
    msg += f"⏰ {data['date']}\n\n"
    
    msg += f"💰 أسعار العملات (شراء | مبيع):\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    
    for curr in data['currencies']:
        msg += f"🔹 {curr['name']}:\n"
        msg += f"  - القديم: {curr['buy']} | {curr['sell']} ل.س\n"
        msg += f"  - الجديد: {to_new(curr['buy'])} | {to_new(curr['sell'])} ل.س\n\n"
    
    msg += f"✨ أسعار الذهب:\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    if 'gold_21' in data:
        msg += f"🔸 عيار 21: {data['gold_21']} ل.س ({to_new(data['gold_21'])} جديد)\n"
    if 'gold_18' in data:
        msg += f"🔸 عيار 18: {data['gold_18']} ل.س ({to_new(data['gold_18'])} جديد)\n"
    if 'gold_ounce_usd' in data:
        msg += f"🌍 الأونصة: {data['gold_ounce_usd']} $\n"
    msg += "\n"
    
    # إضافة المحروقات فقط إذا توفرت
    fuel_msg = ""
    if 'fuel_gasoline' in data:
        fuel_msg += f"⛽ بنزين: {data['fuel_gasoline']} ل.س\n"
    if 'fuel_diesel' in data:
        fuel_msg += f"🛢️ مازوت: {data['fuel_diesel']} ل.س\n"
    if 'fuel_gas' in data:
        fuel_msg += f"🔵 غاز: {data['fuel_gas']} ل.س\n"
    
    if fuel_msg:
        msg += f"⛽ المحروقات والطاقة:\n"
        msg += f"━━━━━━━━━━━━━━━━━━\n"
        msg += fuel_msg + "\n"
    
    msg += f"📢 تابعونا عبر منصاتنا:\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🔗 تلجرام: https://t.me/FarawlaShop\n"
    msg += f"🔗 واتساب: https://whatsapp.com/channel/0029VaQSQveCRs1vibyRZp3A\n"
    msg += f"🔗 فيسبوك: https://www.facebook.com/profile.php?id=61584349121096\n"
    msg += f"━━━━━━━━━━━━━━━━━━"
    return msg

def main():
    print("Checking for updates...")
    data = get_sp_today_data()
    if data:
        message = format_message(data)
        try:
            bot.send_message(CHANNEL_ID, message)
            print("Update sent to channel!")
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    main()
