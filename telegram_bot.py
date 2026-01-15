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

def get_data():
    url = "https://sp-today.com/ar/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = {'currencies': [], 'gold': [], 'fuel': []}

        # استخراج العملات
        target_currencies = {
            'USD': 'دولار أمريكي',
            'EUR': 'يورو',
            'TRY': 'ليرة تركية',
            'SAR': 'ريال سعودي',
            'AED': 'درهم إماراتي',
            'EGP': 'جنيه مصري'
        }
        
        links = soup.find_all('a')
        found_codes = set()
        
        for link in links:
            text = link.get_text(separator="|").strip()
            parts = [p.strip() for p in text.split('|') if p.strip()]
            
            for code, name in target_currencies.items():
                if code in parts and code not in found_codes:
                    # البحث عن الأرقام في الأجزاء التالية
                    prices = []
                    for p in parts:
                        clean_p = p.replace(',', '')
                        if clean_p.isdigit():
                            prices.append(p)
                    
                    if len(prices) >= 2:
                        data['currencies'].append({
                            'code': code,
                            'name': name,
                            'buy': prices[0],
                            'sell': prices[1]
                        })
                        found_codes.add(code)

        # استخراج الذهب
        for link in links:
            text = link.get_text(separator="|").strip()
            parts = [p.strip() for p in text.split('|') if p.strip()]
            if '21K' in parts and len(parts) >= 5:
                data['gold'].append({'name': 'عيار 21', 'price': parts[4]})
            elif '18K' in parts and len(parts) >= 5:
                data['gold'].append({'name': 'عيار 18', 'price': parts[4]})
            elif 'أونصة الذهب' in text:
                match = re.search(r'\$(\d+[\d,.]*)', text)
                if match: data['gold_ounce'] = match.group(1)

        # استخراج المحروقات
        for link in links:
            text = link.get_text(separator="|").strip()
            parts = [p.strip() for p in text.split('|') if p.strip()]
            if 'بنزين' in parts and len(parts) >= 4:
                data['fuel'].append({'name': 'بنزين', 'price': parts[3]})
            elif 'مازوت' in parts and len(parts) >= 4:
                data['fuel'].append({'name': 'مازوت', 'price': parts[3]})
            elif 'غاز' in parts and len(parts) >= 4:
                data['fuel'].append({'name': 'غاز', 'price': parts[3]})

        data['date'] = datetime.datetime.now().strftime("%Y-%m-%d | %I:%M %p")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def format_msg(data):
    def calc_new(val_str):
        try:
            val = float(val_str.replace(',', ''))
            return f"{val/100:,.2f}"
        except: return "0.00"

    msg = "🇸🇾 *نشرة أسعار الصرف والذهب في سوريا* 🇸🇾\n"
    msg += f"⏰ `{data['date']}`\n\n"
    
    if data['currencies']:
        msg += "💰 *أسعار العملات (شراء | مبيع):*\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        for c in data['currencies']:
            msg += f"🔹 *{c['name']} ({c['code']}):*\n"
            msg += f"  - ليرة قديمة: {c['buy']} | {c['sell']}\n"
            msg += f"  - ليرة جديدة: `{calc_new(c['buy'])}` | `{calc_new(c['sell'])}` ✨\n\n"
    
    if data['gold'] or 'gold_ounce' in data:
        msg += "✨ *أسعار الذهب:*\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        for g in data['gold']:
            msg += f"🔸 {g['name']}: {g['price']} ل.س (`{calc_new(g['price'])}` جديد)\n"
        if 'gold_ounce' in data:
            msg += f"🌍 أونصة الذهب: `${data['gold_ounce']}`\n"
        msg += "\n"
    
    if data['fuel']:
        msg += "⛽ *المحروقات والطاقة:*\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        for f in data['fuel']:
            msg += f"🔹 {f['name']}: {f['price']}\n"
        msg += "\n"
    
    msg += "📢 *تابعونا عبر منصاتنا:*\n"
    msg += "━━━━━━━━━━━━━━━━━━\n\n"
    msg += "🔗 *تلجرام:*\nhttps://t.me/FarawlaShop\n\n"
    msg += "🔗 *واتساب:*\nhttps://whatsapp.com/channel/0029VaQSQveCRs1vibyRZp3A\n\n"
    msg += "🔗 *فيسبوك:*\nhttps://www.facebook.com/profile.php?id=61584349121096\n\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    return msg

def main():
    print("Starting update...")
    data = get_data()
    if data and data['currencies']:
        message = format_msg(data)
        try:
            bot.send_message(CHANNEL_ID, message, parse_mode='Markdown', disable_web_page_preview=True)
            print("Success!")
        except Exception as e:
            print(f"Error sending: {e}")
            bot.send_message(CHANNEL_ID, message.replace('*', '').replace('`', ''))
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
