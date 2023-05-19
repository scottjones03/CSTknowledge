import requests
from typing import List

class NotionAPI:
    DATABASE_ID = "695ece9dd1a749c2a94ddeea02d1fce3"

    def __init__(self, token) -> None:
        self._headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
    def format_text(text:str):
        formatted_text = []
        start_bold = False
        start_italic = False
        split_text = text.split()

        for word in split_text:
            if '***' in word:
                start_bold = not start_bold
                start_italic = not start_italic
                formatted_word = word.replace('***', '')
                formatted_text.append({'type': 'text', 'text': {'content': formatted_word, 'annotations': {'bold': start_bold, 'italic': start_italic, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}}})
            if '**' in word:
                start_bold = not start_bold
                formatted_word = word.replace('**', '')
                formatted_text.append({'type': 'text', 'text': {'content': formatted_word, 'annotations': {'bold': start_bold, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}}})
            elif '*' in word:
                start_italic = not start_italic
                formatted_word = word.replace('*', '')
                formatted_text.append({'type': 'text', 'text': {'content': formatted_word, 'annotations': {'bold': False, 'italic': start_italic, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}}})
            else:
                formatted_text.append({'type': 'text', 'text': {'content': word}})
                
        return formatted_text
    
    def create_page(self, name: str, texts: List[str] = [], author: str = ''):
        create_url = "https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": NotionAPI.DATABASE_ID}, 
            "children": []
        }
        for text in texts:
            chunks = ['']
            for line in text.splitlines(True):
                if len(chunks[-1])+len(line)<2000:
                    chunks[-1]+=line
                else:
                    chunks.append(line) 
            for chunk in chunks:
                data["children"].append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": NotionAPI.format_text(chunk),
                        }
                    }
                )

        data["properties"]= {
                'Reviewed':{'checkbox': False},
                'Name': {'title': [{'text': {'content': f'{name}', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 'plain_text': f'{name}', 'href': None}]},
                'Author': {'rich_text': [{'text': {'content': f'{author}', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 'plain_text': f'{author}', 'href': None}]},
        }
        
        res = requests.post(create_url, headers=self._headers, json=data)
        return res



    def get_pages(self, num_pages=None):
        """
        If num_pages is None, get all pages, otherwise just the defined number.
        """
        url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"

        get_all = num_pages is None
        page_size = 100 if get_all else num_pages

        payload = {"page_size": page_size}
        response = requests.post(url, json=payload, headers=self._headers)

        data = response.json()

        # Comment this out to dump all data to a file
        # import json
        # with open('db.json', 'w', encoding='utf8') as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)

        results = data["results"]
        while data["has_more"] and get_all:
            payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
            url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"
            response = requests.post(url, json=payload, headers=self._headers)
            data = response.json()
            results.extend(data["results"])

        return results

    def delete_page(self, name: str):
        for page in self.get_pages():
            page_name = page["properties"]["Name"]["title"][0]['plain_text']
            if page_name==name:
                url = f"https://api.notion.com/v1/pages/{page['id']}"

                payload = {"archived": True}

                res = requests.patch(url, json=payload, headers=self._headers)
               