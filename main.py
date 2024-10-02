import requests
import argparse
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, unquote, urlsplit
import os.path
import time
import json


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def get_category_book_urls(start_page, end_page):
    description_book = []
    for number in range(start_page, end_page):
        url = f'https://tululu.org/l55/{number}'
        response = requests.get(url)
        response.raise_for_status()
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        selector = "table.d_book"
        books_card = soup.select(selector)
        for book_card in books_card:
            book_link = book_card.find('a')['href'] 
            full_book_link = urljoin(url, book_link)  
            description_book.append(full_book_link)
    return description_book


def download_txt(url, book_id, filename, folder="books/"):
    os.makedirs(folder, exist_ok=True)
    params = {"id": book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(f"{folder}/{sanitize_filename(filename)}.txt")
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(response, book_url):
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.select_one("h1").text
        title_book, author = title_tag.split(" :: ")
        url_selector = "div.bookimage img"
        url_img = soup.select_one(url_selector)["src"]
        full_url_img = urljoin(book_url, url_img)
        comments = []
        comment_selector = "div.texts"
        comment_elements = soup.select(comment_selector)
        for element in comment_elements:
            comment = element.find('span', class_="black").text
            comments.append(comment.strip())
        genres = []
        types_genres_selector = "span.d_book a"
        types_genres = soup.select(types_genres_selector)
        for element in types_genres:    
            genre = element.text
            genres.append(genre.strip())
        book_parameters ={
            "title": title_book,
            "author": author,
            "image_url": full_url_img,
            "genres": genres,                   
            "comments": comments,
        }
        return book_parameters


def download_image(image_url,img_folder="images/",):
    os.makedirs(img_folder, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = urlsplit(image_url).path.split("/")[-1]
    filepath = os.path.join(img_folder,filename)
    with open(unquote(filepath), 'wb') as file:
        file.write(response.content)


def main():
    parser = argparse.ArgumentParser(description='Скачивает книги по выбранному ID книги')
    parser.add_argument("--start_page", type=int, help="ID первой книги", default= 1)
    parser.add_argument("--end_page", type=int, help="ID последней книги", default= 701)
    parser.add_argument("--dest_folder", type=str, help="Путь для сохранения картинки/описания", default= "Folder/")
    parser.add_argument("--skip_imgs", action= "store_true", help="Не скачивать картинку",)
    parser.add_argument("--skip_txt", action= "store_true",  help="Не скачивать описание",)
    args = parser.parse_args()

    for_img = f"{args.dest_folder}/images"
    os.makedirs(for_img, exist_ok=True)

    for_txt = f"{args.dest_folder}/books"
    os.makedirs(for_txt, exist_ok=True)

    all_book_parameters = []   
    for book_id, fantastic in enumerate(get_category_book_urls(args.start_page, args.end_page)):
        try:
            response = requests.get(fantastic)
            response.raise_for_status()
            check_for_redirect(response)
            params_books = parse_book_page(response, fantastic)
            all_book_parameters.append(params_books)

            if not args.skip_imgs:                             
                download_image(params_books["image_url"], img_folder=for_img)

            filename = f"{book_id}, {params_books['title'].strip()}"
            book_url = "https://tululu.org/txt.php" 

            if not args.skip_txt:
                download_txt(book_url, book_id, filename, folder=for_txt)

        except requests.exceptions.HTTPError:
            print(f"Книга с ID {book_id} не найдена.")
        except requests.exceptions.ConnectionError:
            print("Повтороное подключение...")
            time.sleep(20)
    with open(f"{args.dest_folder}/data.json", "w", encoding='UTF-8') as json_file:
        json.dump(all_book_parameters, json_file, ensure_ascii=False)


if __name__ == "__main__":
    main()