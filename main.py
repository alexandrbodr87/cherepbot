import os, telebot, requests, time
import g4f

BOT_TOKEN = "7201522733:AAEYnZkZvkF6B9b8ABUfPqFaTP7p172CZQI"
CHANNEL_ID = "@cherepnew"
NEWS_API_KEY = "8ac22501cc5946919e38e24204964995"
DB_FILE = "cher_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def run():
    url = f"https://newsapi.org/v2/everything?q=Череповец OR Северсталь&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=20)
        data = r.json()
        articles = data.get("articles", [])

        if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
        with open(DB_FILE, 'r') as f: done = f.read().splitlines()

        posted = 0
        for a in articles:
            if posted >= 2: break
            link = a["url"]
            if link not in done:
                try:
                    response = g4f.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": f"Сделай краткий пост для ТГ (заголовок жирным): {a['title']}\n{a['description']}"}]
                    )
                    msg = response + f"\n\n[🏙 cherepnew](https://t.me/cherepnew)"
                except:
                    msg = f"**{a['title']}**\n\n{a['description']}\n\n[🏙 cherepnew](https://t.me/cherepnew)"
                
                if a.get("urlToImage"): bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg[:1024], parse_mode='Markdown')
                else: bot.send_message(CHANNEL_ID, msg[:4096], parse_mode='Markdown')
                
                with open(DB_FILE, 'a') as f: f.write(link + "\n")
                posted += 1
                time.sleep(5)
    except: pass

if __name__ == "__main__":
    run()
