import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv
# ================================================================
import json
# ================================================================

def init_env():
    load_dotenv()
    rakuten_developer_id = os.getenv('RAKUTEN_DEVELOPER_ID')
    return rakuten_developer_id

def _search_google_books_api(isbn):
    google_books_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}"}
    response = requests.get(google_books_url, params=params)

    if response.status_code == 200 and response.json()['totalItems'] > 0:
        book = response.json()['items'][0]['volumeInfo']

# ================================================================      
        # formatted_json = json.dumps(book, indent=4)
        # print("------------------------\n",
        #     formatted_json,
        #     "\n--------------------------")
# ================================================================

        title = book.get('title', None)
        publisher = book.get('publisher', None)
        authors = ', '.join(book.get('authors', [])) if book.get('authors') else None
        thumbnail = book.get('imageLinks', {}).get('thumbnail', None)

        return {
            "Title": title,
            "ISBN": isbn,
            "Publisher": publisher,
            "Authors": authors,
            "Thumbnail": thumbnail
        }
    return None

def _search_national_library_api(isbn):
    ndl_search_url = f"https://iss.ndl.go.jp/api/opensearch"
    params = {'isbn': isbn}
    response = requests.get(ndl_search_url, params=params)

    if response.status_code == 200:
        # 名前空間の定義
        ns = {'dc': 'http://purl.org/dc/elements/1.1/'}

        root = ET.fromstring(response.content)
        item = root.find('.//item')
        if item is None:
            return {}

        title = item.find('title').text if item.find('title') is not None else None

        # 名前空間を使用して出版社と著者を取得
        publisher = item.find('dc:publisher', ns).text if item.find('dc:publisher', ns) is not None else None
        authors_list = item.findall('dc:creator', ns)
        authors = ', '.join([author.text for author in authors_list]) if authors_list else None

        # print("\n!!!!", title,
        #     "\n!!!!", publisher,
        #     "\n!!!!", authors_list,
        #     "\n!!!!", authors)

        thumbnail = f'https://iss.ndl.go.jp/thumbnail/{isbn}'
        return {
            "Title": title,
            "Publisher": publisher,
            "Authors": authors,
            "Thumbnail": thumbnail
        }
    return {}


def _search_rakuten_books_api(isbn, developer_id):
    rakuten_url = f"https://app.rakuten.co.jp/services/api/BooksTotal/Search/20170404"
    params = {
        "format": "json",
        "keyword": "本",
        "isbnjan": isbn,
        "applicationId": developer_id,
    }
    response = requests.get(rakuten_url, params=params)

    # print("HTTP Response Status Code:",response.status_code)
    if response.status_code == 200:
        data = response.json()
        items = data.get("Items", [])
        if not items:
            return {}

        book = items[0].get("Item", {})
        title = book.get("title", None)
        publisher = book.get("publisherName", None)
        authors = book.get("author", None)
        thumbnail = book.get("largeImageUrl", None).replace('?_ex=200x200', '')

        # print(title,"\n",
        #     publisher,"\n",
        #     authors,"\n",
        #     thumbnail,"\n",)
        return {
            "Title": title,
            "Publisher": publisher,
            "Authors": authors,
            "Thumbnail": thumbnail
        }
    return {}

def search_books_by_isbn(isbn, rakuten_books_api_key):
    # Rakuten Books API
    print("[SEARCH]: Rakuten")
    book_info = _search_rakuten_books_api(isbn, rakuten_books_api_key) or {}
    print("##### Result (Rakuten) #####")
    print(book_info)

    # Google Books API
    if not book_info or not all(value for value in book_info.values()):
        print("[SEARCH]: Google")
        additional_info = _search_google_books_api(isbn) or {}
        for key, value in additional_info.items():
            if not book_info.get(key):
                book_info[key] = value
        print("##### Result (Google) #####")    
        print("[Added Data]: ",additional_info)
        print(book_info)

    # 国立国会図書館サーチAPIでの補完
    if not book_info or not all(value for value in book_info.values()):
        print("[SEARCH]: 国立国会図書館")
        additional_info = _search_national_library_api(isbn) or {}
        for key, value in additional_info.items():
            if not book_info.get(key):
                book_info[key] = value  
        print("##### Result (国立国会図書館) #####")    
        print("[Added Data]: ",additional_info)
        print(book_info)
    return book_info

