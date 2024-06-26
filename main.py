import requests
import argparse
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, unquote, urlsplit
import os.path



def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder="books/"):
    if not os.path.exists(folder):
        os.mkdir(folder)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(f"{folder}{sanitize_filename(filename)}.txt")
    with open(filepath, 'wb') as file:
        file.write(response.content)



def parse_book_page(response,book_url,):
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h1')
        title_text = title_tag.text
        title_book,author = title_text.split(" :: ")
        url_img = soup.find('div', class_='bookimage').find("img")["src"]
        full_url_img = urljoin(book_url, url_img)
        comments = []
        comment_elements = soup.find_all('div', class_='texts')
        for element in comment_elements:
            comment = element.find('span').text
            comments.append(comment.strip())
        genres = []
        comment_genres = soup.find('span', class_='d_book').find_all("a")
        for element in comment_genres:
            genre = element.text
            genres.append(genre.strip())
        book_date ={
            "title": title_book,
            "author": author,
            "image_url": full_url_img,
            "genre": genre,
            "comments": comment,
        }
        return book_date


def download_image(image_url,img_folder="images/",):
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
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
    for book_id in range(args.start_id,args.end_id):
        try:
            book_url =f'https://tululu.org/b{book_id}'
            response = requests.get(book_url)
            response.raise_for_status()
            # check_for_redirect(response)
            book_data = parse_book_page(response, book_url)
            download_image(book_data["image_url"])
            filename = f"{book_id}. {book_data['title'].strip()}"
            url_book = f"https://tululu.org/txt.php?id={book_id}"
            download_txt(url_book,filename)
        except:
            print(f"Книга с ID {book_id} не найдена.")


if __name__ == "__main__":
    main()


