import wikipediaapi
import pandas as pd
import random
import os
from datetime import datetime

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='WikiRaceProject_YZU/1.0 (tengyuchen07@gmail.com)',
    language='zh',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

def generate_path(current_title,target_depth,current_depth,path=None,visited=None):
    if path is None:
        path = []
    if visited is None:
        visited = set()

    page = wiki_wiki.page(current_title)
    if not page.exists():
        return None 

    # 2. 取得網址，並將「標題」與「網址」打包成字典記錄起來
    current_url = page.fullurl
    node_info = {
        'title': current_title,
        'url': current_url
    }
    
    # 加入路徑與已訪問集合 (visited 依然用 title 來判斷有沒有走過就好)
    path.append(node_info)
    visited.add(current_title)

    if current_depth == target_depth:
        return path
    
    print(f"正在搜尋: {current_title} (深度: {current_depth})")

    page = wiki_wiki.page(current_title)    ## 取得當前頁面
    links = list(page.links.keys())     ##取得所有連結
    
    valid_links=[link for link in links if link not in visited and ":" not in link]##過濾掉已訪問過的連結和特殊頁面
    if not valid_links:
        return None
    random.shuffle(valid_links)

    for next_title in valid_links:  ##找到一條可用路徑就回傳
        result_path = generate_path(
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
    start_topic = input("起始條目 (例如: 台灣): ")
    
    while True:
        try:
            required_depth = int(input("目標深度 (建議 4-6): "))
            break
        except ValueError:
            print("請輸入有效的數字")
    
    final_path = generate_path(start_topic, required_depth,0,path=None,visited=None)

    if final_path:
        print("\n成功找到路徑")
        
        # 提取標題，方便組合與印出
        titles = [node['title'] for node in final_path]

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 定義終點
        end_topic = titles[-1]

        detailed_path_string = " -> ".join([f"{node['title']}" for node in final_path])

        # 建立單行紀錄的 DataFrame
        new_df = pd.DataFrame({
            '時間': [current_time],       # 注意這裡要加上中括號，使其成為一個 list，因為我們只有一列資料
            '起始': [start_topic],
            '終點': [end_topic],
            '完整路徑': [detailed_path_string] # 這裡存入了包含網址的完整路徑
        })

        # 設定統一的總表檔名
        filename = "WikiRace_題庫總表.xlsx"

        # 檢查檔案是否已經存在
        if os.path.exists(filename):
            existing_df = pd.read_excel(filename)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_excel(filename, index=False)
            print(f"\n題目已附加題庫總表: {filename}")
        else:
            new_df.to_excel(filename, index=False)
            print(f"\n找不到舊檔案，已建立新的題庫總表: {filename}")
        
    else:
        print("\n尋找失敗")

if __name__ == "__main__":
    main()