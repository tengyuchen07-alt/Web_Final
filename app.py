from flask import Flask, jsonify,request
import requests
from bs4 import BeautifulSoup
import urllib.parse

app= Flask(__name__)
app.json.ensure_ascii = False

def is_valid_link(href):
    if not href:
        return False
    if not href.startswith('/wiki/'):
        return False
    invalid_prefixes = [
        '/wiki/Wikipedia:', '/wiki/Category:', '/wiki/File:', 
        '/wiki/Help:', '/wiki/Special:', '/wiki/Talk:', '/wiki/Template:'
    ]
    for prefix in invalid_prefixes:
        if href.startswith(prefix):
            return False
    return True
@app.route('/api/get_page_content', methods=['POST'])
def get_page_content():
    data=request.get_json()
    link=data.get('link','')
    if not is_valid_link(link):
        return jsonify({"status": "ignore",
                         "html": ""
        })
    url = 'https://zh.wikipedia.org' + link
    headers = {
        'User-Agent': 'WikiPathAI_Backend_B (Student_Project)'
    }
    try:
        response=requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return jsonify({"status": "error",
                            "html": "無法連線至為維基百科"
            })
        soup=BeautifulSoup(response.text, 'html.parser')
        content_div=soup.find('div', id='mw-content-text')
        if not content_div:
            return jsonify({"status": "error",
                            "html": "無法找到內容區塊"
            })
        for edit in content_div.find_all('span', class_='mw-editsection'):
            edit.decompose()
        for ref in content_div.find_all('sup', class_='reference'):
            ref.decompose()
        for img in content_div.find_all('img'):
            img.decompose()
        for indobox in content_div.find_all('table', class_='infobox'):
            indobox.decompose()
        html_content=str(content_div)
        page_title=urllib.parse.unquote(link.split('/wiki/',' '))
        return jsonify({"status": "success",
                        "html": html_content,
                        "title": page_title
        })
    except Exception as e:
        return jsonify({"status": "error",
                        "html": f"發生錯誤: {str(e)}"
        })
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debiug=True)
        
