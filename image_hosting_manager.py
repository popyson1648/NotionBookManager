import requests
import os
from dotenv import load_dotenv

def init_env():
    load_dotenv()
    gyazo_access_token = os.getenv('GYAZO_ACCESS_TOKEN')
    return gyazo_access_token

def _download_img(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def _upload_img(isbn, image_data, access_token):
    headers = {'Authorization': 'Bearer ' + access_token}

    files = {'imagedata': (isbn, image_data)}
    response = requests.post('https://upload.gyazo.com/api/upload', headers=headers, files=files)
    response.raise_for_status()
    return response.json()["url"]

def get_img_url(isbn, src_img_url, access_token):
    try:
        img_data = _download_img(src_img_url)
        hosted_img_url = _upload_img(isbn, img_data, access_token)
    except requests.RequestException as e:
        print("Error:", e)
    return hosted_img_url