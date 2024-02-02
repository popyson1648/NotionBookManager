import os
from dotenv import load_dotenv
from notion_client import Client

def init_env():
    load_dotenv()
    notion_api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('DATABASE_ID')
    notion = Client(auth=notion_api_key)
    return notion, notion_api_key, database_id

def _prop(name, content):
    if not content:
        return {}
    if isinstance(content, str):
        if name == "Name":
            return {name: {"title": [{"text": {"content": content}}]}}
        elif name == "Cover":
            return {name: {"files": [{"type": "external", "name": "Cover Image", "external": {"url": content}}]}}
        elif name == "Category":
            return {name: {"select": {"name": content}}}
        elif name == "Subcategory":
            return {name: {"multi_select": [{"name": content}]}}
        else:
            return {name: {"rich_text": [{"text": {"content": content}}]}}
    elif isinstance(content, int):
        return {name: {"number": content}}
    elif isinstance(content, dict) and "name" in content:
        return {name: {"status": content}}
    elif isinstance(content, list) and all(isinstance(item, str) for item in content):
        if name == "Subcategory":
            return {name: {"multi_select": [{"name": item} for item in content]}}

def create_page(notion_client, database_id, name, isbn, publisher, author, reading_progress_status, thumbnail_url):
    new_page_data = {
        "parent": {"database_id": database_id},
        "properties": {}
    }

    # 各プロパティの追加前に、_propからの戻り値がNoneでないことを確認
    for prop_name, prop_value in [("Name", name),
                                  ("ISBN", isbn),
                                  ("Publisher", publisher),
                                  ("Author", author),
                                  ("Progress", {"name": reading_progress_status}),
                                  ("Cover", thumbnail_url) if thumbnail_url else None]:
        prop_data = _prop(prop_name, prop_value)
        if prop_data:
            new_page_data["properties"].update(prop_data)

    notion_client.pages.create(**new_page_data)
