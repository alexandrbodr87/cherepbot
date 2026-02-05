import os, telebot, requests, time

BOT_TOKEN = "7201522733:AAEYnZkZvkF6B9b8ABUfPqFaTP7p172CZQI"
CHANNEL_ID = "@cherepnew"
CITY_QUERY = "Череповец"
CHANNEL_LINK = "https://t.me/cherepnew"
NEWS_API_KEY = "8ac22501cc5946919e38e24204964995"
GROQ_KEY = os.getenv("GROQ_KEY")
DB_FILE = "cher_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def ask_groq(title, description):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = f"Напиши один заголовок и суть новости до 300 симв. Текст: {title}. {description}"
    data = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20).json()
        return r['choices'][0]['message']['content'].strip()
    except: return None

def run():
    url = f"https://newsapi.org/v2/everything?q={CITY_QUERY}&sortBy=publishedAt&language=ru&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, 'r') as f: done = f.read().splitlines()
    p = 0
    for a in articles:
        if p >= 2: break
        if a["url"] not in done:
            summary = ask_groq(a['title'], a['description'] or a['title'])
            txt = summary if summary else (a['description'] if a['description'] else a['title'])
            msg = f"{txt}\n\n🏙 <a href='{CHANNEL_LINK}'>Череповец.news</a>"
            try:
                if a.get("urlToImage"):
                    bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg, parse_mode='HTML')
                else:
                    bot.send_message(CHANNEL_ID, msg, parse_mode='HTML')
                with open(DB_FILE, 'a') as f: f.write(a["url"] + "\n")
                p += 1
                time.sleep(5)
            except: pass

if __name__ == "__main__":
    run()
