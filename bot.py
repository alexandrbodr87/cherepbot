import os
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import g4f
from telegram import Bot
import asyncio

TOKEN = "7201522733:AAEYnZkZvkF6B9b8ABUfPqFaTP7p172CZQI"
CHAT_ID = "@cherepnew"
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
    r = requests.get(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    
    first_news = soup.find('div', class_='news-item')
    link_tag = first_news.find('a', href=True)
    link = BASE_URL + link_tag['href']

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
        if img:
            await bot.send_photo(chat_id=CHAT_ID, photo=img, caption=rewritten_text[:1024])
        else:
            await bot.send_message(chat_id=CHAT_ID, text=rewritten_text[:4096])
        
        with open("last_news.txt", "w") as f:
            f.write(link)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
