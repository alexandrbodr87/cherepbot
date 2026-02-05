import os, telebot, requests, time
import google.generativeai as genai

BOT_TOKEN = "7201522733:AAEYnZkZvkF6B9b8ABUfPqFaTP7p172CZQI"
CHANNEL_ID = "@cherepnew"
NEWS_API_KEY = "8ac22501cc5946919e38e24204964995"
GEMINI_KEY = "AIzaSyAu666zkt38354ADCo2WJmOdizdQa0OQmY"
DB_FILE = "cher_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def run():
    url = f"https://newsapi.org/v2/everything?q=Череповец OR Северсталь&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=20).json()
        articles = r.get("articles", [])
        if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
        with open(DB_FILE, 'r') as f: done = f.read().splitlines()
        
        posted = 0
        for a in articles:
            if posted >= 2: break
            link = a["url"]
            if link not in done:
                prompt = f"Сделай краткий новостной пост для Телеграм (заголовок жирным). Добавь подходящие по теме новости эмодзи-стикеры: {a['title']}\n{a['description']}"
                response = model.generate_content(prompt)
                msg = response.text + f"\n\n[🏙 cherepnew](https://t.me/cherepnew)"
                if a.get("urlToImage"): bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg[:1024], parse_mode='Markdown')
                else: bot.send_message(CHANNEL_ID, msg[:4096], parse_mode='Markdown')
                with open(DB_FILE, 'a') as f: f.write(link + "\n")
                posted += 1
                time.sleep(5)
    except: pass

if __name__ == "__main__": run()
