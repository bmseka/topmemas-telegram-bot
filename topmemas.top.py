import requests_html
import telebot
import time
import logging
import pickle
import signal
import sys
import os
from tqdm import trange

bot = telebot.TeleBot('YOUR_TOKEN')

def get_html(url):
    session = requests_html.HTMLSession()
    response = session.get(url)
    # Выполняем JavaScript на странице и прокручиваем ее вниз 10 раз
    response.html.render(scrolldown=10)
    return response.html

def get_images(html):
    images = {}
    divs = html.find('div.cont_item')
    for div in divs:
        img = div.find('img', first=True)
        if img:
            # Получаем ссылку на картинку из атрибута src
            src = img.attrs['src']
            # Проверяем, что ссылка полная, иначе добавляем домен сайта к ней
            if not src.startswith("https://"):
                src = "https://topmemas.top/" + src
            # Добавляем ссылку на картинку и ее описание в словарь images
            try:
                images[src] = img.attrs['title']
            except KeyError:
                images[src] = ''
    return images

def send_images(images):
    for url, caption in images.items():
        bot.send_photo('@YOUR_CHANNEL', photo=url, caption=caption)
        logging.info(f'Sent image {url} to @YOUR_CHANNEL')
        save_last_images({url: caption})
        # делаем паузу в 60 секунд
        for i in trange(60, 0, -1):
            # делаем паузу в 1 секунду
            time.sleep(1)

def save_last_images(images):
    last_images = load_last_images()
    last_images.update(images)
    with open('last_images2.pickle', 'wb') as f:
        pickle.dump(last_images, f)

def load_last_images():
    if not os.path.exists('last_images2.pickle'):
        with open('last_images2.pickle', 'wb') as f:
            pickle.dump({}, f)
    with open('last_images2.pickle', 'rb') as f:
        return pickle.load(f)

def check_new_images(images):
    last_images = load_last_images()
    new_images = {}
    for url, caption in images.items():
        if url not in last_images:
            new_images[url] = caption
    return new_images

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

signal.signal(signal.SIGINT, signal_handler)

url = 'https://topmemas.top/'

while True:
    html = get_html(url)
    logging.info(f'Got HTML from {url}')
    images = get_images(html)
    logging.info(f'Found {len(images)} images on the site')
    new_images = check_new_images(images)
    logging.info(f'Found {len(new_images)} new images to send')
    if new_images:
        send_images(new_images)
        logging.info(f'Sent {len(new_images)} images to @YOUR_CHANNEL')
    # делаем паузу в 300 секунд
    for i in trange(300, 0, -1):
        # делаем паузу в 1 секунду
        time.sleep(1)
