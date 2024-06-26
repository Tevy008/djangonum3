import requests
import os
from bs4 import BeautifulSoup

#guide

url = 'https://tululu.org/b1/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
print(soup.prettify())

title_tag = soup.find('main').find('header').find('h1')
title_text = title_tag.text
print(title_text)

image_output = soup.find('img', class_='attachment-post-image')['src'] 
print(image_output)
