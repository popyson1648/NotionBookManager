import os
import book_searcher
import notion_book_data_inserter
import image_hosting_manager

NOTION_CLIENT, NOTION_API_KEY, DATABASE_ID = notion_book_data_inserter.init_env()
GYAZO_API_KEY = image_hosting_manager.init_env()
RAKUTEN_API_KEY = book_searcher.init_env()

STATUS = "未着手"

def main():
    books = _read_isbn_list_to_array()
    for isbn in books:
        book_info = book_searcher.search_books_by_isbn(isbn, RAKUTEN_API_KEY)

        # Google Books API由来のThumbnail値はダウンロード後ホスティングし、そのURLを利用する。
        if "http://books.google.com/books/" in book_info["Thumbnail"]:
            thumbnail_url = image_hosting_manager.get_img_url(isbn, book_info["Thumbnail"], GYAZO_API_KEY)
        else:
            thumbnail_url = book_info["Thumbnail"]

        notion_book_data_inserter.create_page(
            NOTION_CLIENT,
            DATABASE_ID,
            book_info["Title"],
            isbn,
            book_info["Publisher"],
            book_info["Authors"],
            STATUS,
            thumbnail_url
        )


def _read_isbn_list_to_array():
    books = []
    filename = 'isbn_list.txt'
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                books.append(line.strip().replace('-', ''))
    else:
        print("isbn_list.txt ファイルが見つかりません。")
    return books

if __name__ == '__main__':
    main()