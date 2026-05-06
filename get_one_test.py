from flask import Flask, jsonify
import pandas as pd
import random

app = Flask(__name__)
app.json.ensure_ascii = False

try:
    df = pd.read_excel('WikiRace_題庫總表.xlsx')
    print(f"成功載入題庫，共有 {len(df)} 題！")
except Exception as e:
    print(f"讀取題庫失敗，請確認檔案是否存在。錯誤: {e}")
    df = pd.DataFrame() # 給個空的預防當機

# 開設API網址
@app.route('/api/get_question', methods=['GET'])
def get_question():
    if df.empty:
        return jsonify({"status": "error", "message": "題庫空空如也"}), 500
    random_question = df.sample(1).iloc[0]
    path_string = random_question['完整路徑']
    path_list = path_string.split(' -> ')

    response_data = {
        "status": "success",
        "data": {
            "start_title": random_question['起始'],
            "end_title": random_question['終點'],
            "shortest_path_steps": len(path_list) - 1, # 步數 = 節點數 - 1
            "optimal_path": path_list
        }
    }
    
    # jsonify 會自動把 Python 字典轉換成標準的 JSON 格式
    return jsonify(response_data)

# 啟動伺服器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)