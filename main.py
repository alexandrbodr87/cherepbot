import os, telebot, requests, time

BOT_TOKEN = "7201522733:AAEYnZkZvkF6B9b8ABUfPqFaTP7p172CZQI"
CHANNEL_ID = "@cherepnew"
CITY_QUERY = "Череповец"
CHANNEL_LINK = "https://t.me/cherepnew"
NEWS_API_KEY = "8ac22501cc5946919e38e24204964995"
GROQ_KEY = os.getenv("GROQ_KEY")
DB_FILE = "cher_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def ask_groq(title, text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = f"Сделай из этого огрызка новости полноценный короткий пост. Напиши яркий заголовок и 1-2 законченных предложения. Строго до 250 символов. Не обрывай на полуслове. Текст: {title}. {text}"
    data = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20).json()
        return r['choices'][0]['message']['content'].strip()
    except: return None

def run():
    url = f"https://newsapi.org/v2/everything?q={CITY_QUERY}&sortBy=publishedAt&pageSize=10&language=ru&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    articles = r.get("articles", [])
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, 'r', encoding='utf-8') as f: done = f.read().splitlines()
    
    p = 0
    for a in articles:
        if p >= 2: break
        if a["url"] not in done and a["title"] not in done:
            raw_text = a.get('description') or a.get('title')
            clean_text = raw_text.split('[+')[0]
            
            summary = ask_groq(a['title'], clean_text)
            txt = summary if summary else a['title']
            msg = f"{txt}\n\n🏙 <a href='{CHANNEL_LINK}'>Череповец</a>"
            try:
                if a.get("urlToImage"):
                    bot.send_photo(CHANNEL_ID, a["urlToImage"], caption=msg, parse_mode='HTML')
                else:
                    bot.send_message(CHANNEL_ID, msg, parse_mode='HTML')
                with open(DB_FILE, 'a', encoding='utf-8') as f:
                    f.write(a["url"] + "\n")
                    f.write(a["title"] + "\n")
                p += 1
                time.sleep(5)
            except: pass

if __name__ == "__main__":
    run()
