"Error fetching data: {e}")
        return None

def format_message(data):
        def to_new(val_str):
                    try:
                                    val = float(val_str.replace(',', ''))
                                    return f"{val/100:,.2f}"
                                except:
                                                return "0.00"
                                    
                def to_usd_price(val_str, usd_sell):
                            try:
                                            val = float(val_str.replace(',', ''))
                                            usd = float(usd_sell.replaceimport requests
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

        data = {}

        # استخراج العملات من الجدول
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                currency_name = cols[0].get_text().strip()
                buy = cols[1].get_text().strip()
                sell = cols[2].get_text().strip()

                if 'USD' in currency_name or 'دولار' in currency_name:
                    data['usd'] = (buy, sell)
                elif 'EUR' in currency_name or 'يورو' in currency_name:
                    data['eur'] = (buy, sell)
                elif 'TRY' in currency_name or 'ليرة تركية' in currency_name:
                    data['try'] = (buy, sell)

        # استخراج الذهب
        gold_items = soup.find_all('a')
        for item in gold_items:
            text = item.get_text()
            if '21K' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 4:
                    data['gold_21'] = parts[3]
            elif '18K' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 4:
                    data['gold_18'] = parts[3]
            elif 'أونصة الذهب' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 1:
                    data['gold_ounce_usd'] = parts[0]

        # استخراج المحروقات
        fuel_items = soup.find_all('a')
        for item in fuel_items:
            text = item.get_text()
            if 'بنزين' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 2:
                    data['fuel_gasoline'] = parts[1]
            elif 'مازوت' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 2:
                    data['fuel_diesel'] = parts[1]
            elif 'غاز' in text:
                parts = re.findall(r'[\d,.]+', text)
                if len(parts) >= 2:
                    data['fuel_gas'] = parts[1]

        # قيم افتراضية في حال الفشل
        data.setdefault('usd', ('12,160', '12,240'))
        data.setdefault('eur', ('14,090', '14,290'))
        data.setdefault('try', ('280', '284'))
        data.setdefault('gold_21', '1,590,700')
        data.setdefault('gold_18', '1,363,500')
        data.setdefault('gold_ounce_usd', '4,596')
        data.setdefault('gold_coin', '12,725,000')
        data.setdefault('fuel_gasoline', '10,400')
        data.setdefault('fuel_diesel', '9,180')
        data.setdefault('fuel_gas', '128,520')

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
        except:
            return "0.00"

    def to_usd_price(val_str, usd_sell):
        try:
            val = float(val_str.replace(',', ''))
            usd = float(usd_sell.replace(',', ''))
            return f"{val/usd:,.2f}"
        except:
            return "0.00"

    usd_sell = data['usd'][1]

    msg = f"🇸🇾 نشرة أسعار الصرف والذهب في سوريا 🇸🇾\n"
    msg += f"⏰ {data['date']}\n\n"
    
    msg += f"💰 أسعار العملات (شراء | مبيع):\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    
    msg += f"🇺🇸 الدولار الأمريكي:\n"
    msg += f"  - السعر القديم: {data['usd'][0]} | {data['usd'][1]} ل.س\n"
    msg += f"  - السعر الجديد: {to_new(data['usd'][0])} | {to_new(data['usd'][1])} ل.س\n\n"
    
    msg += f"🇪🇺 اليورو:\n"
    msg += f"  - السعر القديم: {data['eur'][0]} | {data['eur'][1]} ل.س\n"
    msg += f"  - السعر الجديد: {to_new(data['eur'][0])} | {to_new(data['eur'][1])} ل.س\n"
    msg += f"  - بالدولار: {to_usd_price(data['eur'][1], usd_sell)} $\n\n"
    
    msg += f"🇹🇷 الليرة التركية:\n"
    msg += f"  - السعر القديم: {data['try'][0]} | {data['try'][1]} ل.س\n"
    msg += f"  - السعر الجديد: {to_new(data['try'][0])} | {to_new(data['try'][1])} ل.س\n"
    msg += f"  - بالدولار: {to_usd_price(data['try'][1], usd_sell)} $\n\n"
    
    msg += f"✨ أسعار الذهب:\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🔸 عيار 21:\n"
    msg += f"  - {data['gold_21']} ل.س\n"
    msg += f"  - {to_new(data['gold_21'])} ل.س (جديد)\n"
    msg += f"  - {to_usd_price(data['gold_21'], usd_sell)} $\n\n"
    
    msg += f"🔸 عيار 18:\n"
    msg += f"  - {data['gold_18']} ل.س\n"
    msg += f"  - {to_new(data['gold_18'])} ل.س (جديد)\n"
    msg += f"  - {to_usd_price(data['gold_18'], usd_sell)} $\n\n"
    
    msg += f"🌍 الأونصة: {data['gold_ounce_usd']} $\n"
    msg += f"🪙 الليرة الذهبية: {data['gold_coin']} ل.س\n\n"
    
    msg += f"⛽ المحروقات والطاقة:\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"⛽ بنزين: {data['fuel_gasoline']} ل.س ({to_usd_price(data['fuel_gasoline'], usd_sell)} $)\n"
    msg += f"🛢️ مازوت: {data['fuel_diesel']} ل.س ({to_usd_price(data['fuel_diesel'], usd_sell)} $)\n"
    msg += f"🔵 غاز: {data['fuel_gas']} ل.س ({to_usd_price(data['fuel_gas'], usd_sell)} $)\n\n"
    
    msg += f"📢 اشترك لتصلك التحديثات فوراً:\n"
    msg += f"🔗 {CHANNEL_ID}\n"
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

if __name__ == '__main__':
    main()
