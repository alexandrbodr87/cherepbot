import os
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import g4f
from telegram import Bot
import asyncio

TOKEN = "7201522733:AAEYnZkZvkF6B9b8ABUfPqFaTP7p172CZQI"
CHAT_ID = "1003848831304"
SOURCE_URL = "https://cherinfo.ru/news"
BASE_URL = "https://cherinfo.ru"

async def get_rewrite(text):
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Сделай краткий рерайт новости. Начни с жирного заголовка. Структурируй по смыслу: {text[:2000]}"}],
        )
        return response
    except:
        return text[:1000]

async def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    r = requests.get(SOURCE_URL, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    links = []
    for a in soup.find_all('a', href=True):
        if '/news/' in a['href'] and a['href'] != '/news/':
            full_url = a['href'] if a['href'].startswith('http') else BASE_URL + a['href']
            if full_url not in links:
                links.append(full_url)

    if not links:
        return

    link = links[0]

    if os.path.exists("last_news.txt"):
        with open("last_news.txt", "r") as f:
            if link in f.read():
                return

    article = Article(link)
    article.download()
    article.parse()
    
    raw_text = article.text
    img = article.top_image
    rewritten_text = await get_rewrite(raw_text)

    bot = Bot(token=TOKEN)
    
    try:
        if img and len(img) > 5:
            await bot.send_photo(chat_id=CHAT_ID, photo=img, caption=rewritten_text[:1024])
        else:
            await bot.send_message(chat_id=CHAT_ID, text=rewritten_text[:4096])
        
        with open("last_news.txt", "w") as f:
            f.write(link)
    except Exception as e:
        pass

if __name__ == "__main__":
    asyncio.run(main())
