import requests
import argparse
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, unquote, urlsplit
import os.path
import time



def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, book_id, filename, folder="books/"):
    os.makedirs(folder, exist_ok=True)
    params = {"id": book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(f"{folder}{sanitize_filename(filename)}.txt")
    with open(filepath, 'wb') as file:
        file.write(response.content)



def parse_book_page(response, book_url):
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h1').text
        title_book, author = title_tag.split(" :: ")
        url_img = soup.find('div', class_='bookimage').find("img")["src"]
        full_url_img = urljoin(book_url, url_img)
        comments = []
        comment_elements = soup.find_all('div', class_='texts')
        for element in comment_elements:
            comment = element.find('span', class_="black").text
            comments.append(comment.strip())
        genres = []
        types_genres = soup.find('span', class_='d_book').find_all("a")
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
    parser.add_argument("--start_id", type=int, help="ID первой книги", default= 1)
    parser.add_argument("--end_id", type=int, help="ID последней книги", default= 10 )
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        try:
            book_url =f'https://tululu.org/b{book_id}/'
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            params_books = parse_book_page(response, book_url)
            download_image(params_books["image_url"])
            filename = f"{book_id}. {params_books['title'].strip()}"
            book_url = "https://tululu.org/txt.php"
            download_txt(book_url, book_id, filename)
        except requests.exceptions.HTTPError:
            print(f"Книга с ID {book_id} не найдена.")
        except requests.exceptions.ConnectionError:
            print("Повтороное подключение...")
            time.sleep(20)


if __name__ == "__main__":
    main()