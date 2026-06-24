import os
import requests
import asyncio
from bs4 import BeautifulSoup
from newspaper import Article
# Предполагаем, что вы перешли на официальную библиотеку OpenAI
# from openai import AsyncOpenAI
from telegram import Bot, TelegramError
# import logging # Рекомендуется добавить логирование

# --- 1. Конфигурация и Безопасность ---
# Настоятельно рекомендуется использовать переменные окружения!
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SOURCE_URL = "https://cherinfo.ru/news"
BASE_URL = "https://cherinfo.ru"

# Инициализация бота только в случае наличия токена
bot = Bot(token=TOKEN) if TOKEN else None

async def get_rewrite(text: str) -> str:
    """Отправляет текст на рерайт с использованием API (предположим, OpenAI/GPT)."""
    if not bot:
        print("Ошибка: API клиента не инициализирован.")
        return text[:1000] # Возврат заглушки
        
    # --- Имитация вызова API (замените на реальный вызов) ---
    # try:
    #     client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    #     prompt = f"Сделай краткий рерайт новости. Начни с жирного заголовка. Структурируй по смыслу: {text[:5000]}"
    #     response = await client.chat.completions.create(...)
    #     return response.choices[0].message.content
    # except Exception as e:
    #     print(f"Ошибка API при рерайте: {e}")
    #     return text[:1000] # Fallback
    
    print("Используется заглушка рерайта.")
    return f"**[РЕРАЙТ С ИИ]**\n\nЭто отредактированный и структурированный текст новости, который был получен с помощью ИИ. Оригиал: {text[:500]}..."


async def scrape_and_process_news():
    """Основная асинхронная функция для скрапинга, обработки и отправки."""
    
    if not bot:
        print("Невозможно запустить скрипт: Telegram Token не найден.")
        return
        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    print("Шаг 1: Загрузка главной страницы новостей...")
    try:
        r = requests.get(SOURCE_URL, headers=headers, timeout=20)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    links = []
    
    # Улучшенная логика поиска ссылок
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Проверяем, что это ссылка на новость и содержит цифры
        if '/news/' in href and any(char.isdigit() for char in href):
            full_url = href if href.startswith('http') else BASE_URL + href
            if full_url not in links:
                links.append(full_url)

    if not links:
        print("Не удалось найти ссылки на новости.")
        return

    link = links[0]
    print(f"Найден новый линк: {link}")

    # 2. Проверка на дубликаты
    try:
        if os.path.exists("last_news.txt"):
            with open("last_news.txt", "r") as f:
                last_link = f.read().strip()
            if last_link == link:
                print("Эта новость уже была опубликована. Завершение работы.")
                return
    except IOError as e:
        print(f"Ошибка при чтении файла last_news.txt: {e}")

    # 3. Извлечение статьи
    try:
        print("Шаг 2: Загрузка и парсинг статьи...")
        article = Article(link)
        article.download(timeout=30) # Увеличенный таймаут
        article.parse()
        raw_text = article.text
    except Exception as e:
        print(f"Критическая ошибка при парсинге статьи {link}: {e}")
        return
        
    if not raw_text:
        print("Не удалось извлечь текст статьи.")
        return
# 4. Рерайт
    print("Шаг 3: Рерайт текста с помощью ИИ...")
    rewritten_text = await get_rewrite(raw_text)
    
    # 5. Публикация в Telegram
    print("Шаг 4: Публикация в Telegram...")
    
    # Определение, что публиковать
    photo = article.top_image
    caption_text = rewritten_text
    
    try:
        if photo and len(photo) > 10:
            # Фотография найдена
            await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=caption_text)
        else:
            # Только текст
            # Ограничение текста лучше делать на стороне бэкенда, а не фиксированным лимитом
            await bot.send_message(chat_id=CHAT_ID, text=caption_text)
        
        print("Успешно опубликовано.")

    except TelegramError as e:
        print(f"Ошибка отправки в Telegram: {e}. Возможно, чат ID неверен или бот потерял доступ.")
    except Exception as e:
        print(f"Непредвиденная ошибка при отправке: {e}")
        
    finally:
        # 6. Обновление файла
        try:
            with open("last_news.txt", "w") as f:
                f.write(link)
        except IOError as e:
            print(f"Предупреждение: Не удалось записать новый линк в файл: {e}")


if name == "main":
    # Убедитесь, что переменные окружения заданы перед запуском
    if not TOKEN or not CHAT_ID:
        print("ОШИБКА: Пожалуйста, установите переменные окружения TELEGRAM_TOKEN и TELEGRAM_CHAT_ID.")
    else:
        asyncio.run(scrape_and_process_news())
