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

logger = logging.getLogger('topmemas')
logger.setLevel(logging.INFO)

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)

fh = logging.FileHandler('topmemasLOG.txt')
fh.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(message)s')

sh.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(sh)
logger.addHandler(fh)

def get_html(url):
    session = requests_html.HTMLSession()
    response = session.get(url)
    response.html.render(scrolldown=10)
    return response.html

def get_images(html):
    images = {}
    divs = html.find('div.cont_item')
    for div in divs:
        img = div.find('img', first=True)
        if img:
            src = img.attrs['src']
            if not src.startswith("https://"):
                src = "https://topmemas.top/" + src
            try:
                images[src] = img.attrs['title']
            except KeyError:
                images[src] = ''
    return images

def send_images(images):
    for url, caption in images.items():
        bot.send_photo('@YOUR_CHANNEL', photo=url, caption=caption)
        logger.info(f'Sent image {url} to @YOUR_CHANNEL')
        save_last_images({url: caption})
        for i in trange(60, 0, -1):
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

signal.signal(signal.SIGINT, signal_handler)

url = 'https://topmemas.top/'

while True:
    html = get_html(url)
    logger.info(f'Got HTML from {url}')
    images = get_images(html)
    logger.info(f'Found {len(images)} images on the site')
    new_images = check_new_images(images)
    logger.info(f'Found {len(new_images)} new images to send')
    if new_images:
        send_images(new_images)
        logger.info(f'Sent {len(new_images)} images to @YOUR_CHANNEL)
    for i in trange(300, 0, -1):
        time.sleep(1)
