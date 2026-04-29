import requests
from bs4 import BeautifulSoup
import urllib.parse
import random
import pandas as pd
import os
from datetime import datetime

def get_valid_links_and_url(title):
    # 將中文標題轉換成網址編碼 (例如: 台灣 -> %E5%8F%B0%E7%81%A3)
    encoded_title = urllib.parse.quote(title)
    url = f"https://zh.wikipedia.org/wiki/{encoded_title}"
    
    # 設定 User-Agent 遵守禮貌規範
    headers = {
        'User-Agent': 'WikiRaceGenerator_v2.0 (tengyuchen07@gmail.com)'
    }
    
    try:
        # 發送請求獲取網頁 HTML
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None, url
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 鎖定維基百科的正文主要區域 (排除側邊欄、頂部導覽)
        content_div = soup.find('div', id='mw-content-text')
        if not content_div:
            return None, url
            
        valid_links = set()
        
        #我們只尋找一般文字段落 <p> 與列表 <li> 裡面的連結
        for text_block in content_div.find_all(['p', 'li']):
            for a_tag in text_block.find_all('a', href=True):
                href = a_tag['href']
                if href.startswith('/wiki/') and ':' not in href and href != '/wiki/Wikipedia:%E9%A6%96%E9%A1%B5':
                    # 擷取條目名稱並解碼 (例如 /wiki/%E5%8F%B0%E7%81%A3 -> 台灣)
                    link_title = urllib.parse.unquote(href.replace('/wiki/', ''))
                    valid_links.add(link_title)
                    
        return list(valid_links), url
        
    except requests.RequestException:
        return None, url

def generate_wiki_path(current_title, target_depth, current_depth=0, path=None, visited=None):
    if path is None:
        path = []
    if visited is None:
        visited = set()

    links, current_url = get_valid_links_and_url(current_title)

    if links is None:
        return None
    
    node_info = {'title': current_title, 'url': current_url}
    path.append(node_info)
    visited.add(current_title)

    print(f"正在探索 [深度 {current_depth}]: {current_title}")

    if current_depth == target_depth:
        return path

    valid_links = [link for link in links if link not in visited]

    if not valid_links:
        return None

    random.shuffle(valid_links)

    for next_title in valid_links:
        result_path = generate_wiki_path(
            next_title, 
            target_depth, 
            current_depth + 1, 
            path.copy(), 
            visited.copy()
        )
        
        if result_path is not None:
            return result_path

    return None

def main():
    start_topic = input("請輸入維基競賽起始條目 (例如: 台灣): ")
    
    while True:
        try:
            # 因為直接抓取 HTML 速度稍慢，建議深度先從 3 或 4 開始測試
            required_depth = int(input("請輸入目標深度: "))
            break
        except ValueError:
            print("請輸入有效的數字！")
    
    final_path = generate_wiki_path(start_topic, required_depth,0,path=None,visited=None)

    if final_path:
        print("\n成功找到路徑！")
        
        titles = [node['title'] for node in final_path]

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        end_topic = titles[-1]

        detailed_path_string = " -> ".join([f"{node['title']}" for node in final_path])

        new_df = pd.DataFrame({
            '時間': [current_time],       
            '起始': [start_topic],
            '終點': [end_topic],
            '完整路徑': [detailed_path_string] 
        })

        filename = "WikiRace_題庫總表.xlsx"

        if os.path.exists(filename):
            existing_df = pd.read_excel(filename)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_excel(filename, index=False)
            print(f"\n題目已成功【附加】至題庫總表: {filename}")
        else:
            new_df.to_excel(filename, index=False)
            print(f"\n找不到舊檔案，已建立新的題庫總表: {filename}")
        
    else:
        print("\n尋找失敗")

if __name__ == "__main__":
    main()