import os
import psycopg2
from flask import Flask, render_template, jsonify, request
import random
import json

app = Flask(__name__)

# heroku部署
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# 本地部署
# DATABASE_URL = "postgresql://postgres:010128@localhost:5432/mydatabase"
# conn = psycopg2.connect(DATABASE_URL)

user_data = {} # 字典用于存储用户数据
current_set = -5
submission_count = 0



def load_json_data():
    with open('words.json', 'r') as file:
        return json.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_words/<set_number>', methods=['GET'])
def get_words(set_number):
    data = load_json_data()
    words = data['words'].get(f'Set{set_number}', [])
    selected_words = random.sample(words, 25) if len(words) >= 25 else words
    return jsonify(selected_words)

@app.route('/get_clue/<set_number>', methods=['GET'])
def get_clue(set_number):
    data = load_json_data()
    clues = data['clues'].get(f'Set{set_number}', [])
    return jsonify(clues)

@app.route('/get_ai_hint/<set_number>', methods=['GET'])
def get_ai_hint(set_number):
    data = load_json_data()
    ai_hints = data['AI'].get(f'Set{set_number}', {})
    return jsonify(ai_hints)

@app.route('/get_answers/<set_number>', methods=['GET'])
def get_answers(set_number):
    data = load_json_data()
    answers = data['answers'].get(f'Set{set_number}', {})
    return jsonify(answers)

@app.route('/submit_selected_words', methods=['POST'])
def submit_selected_words():
    global current_set, submission_count
    data = request.json
    selected_words = data.get('words')
    time_taken = data.get('timeTaken')
    print(selected_words, time_taken)  # 打印接收到的单词列表

    set_key = f'Set{current_set}'
    if set_key not in user_data:
        user_data[set_key] = {}

    # 检查是否为当前轮次的第一次或第二次提交
    if submission_count == 0:
        user_data[f'Set{current_set}']['selection1'] = selected_words
        user_data[f'Set{current_set}']['time_taken1'] = time_taken
        submission_count = 1
    else:
        user_data[f'Set{current_set}']['selection2'] = selected_words
        user_data[f'Set{current_set}']['time_taken2'] = time_taken

        # 重置计数器并移动到下一个轮次
        submission_count = 0
        current_set += 1
        if current_set == 0:
            current_set = 1

    return jsonify({"status": "success", "words": selected_words})

# @app.route('/save_data', methods=['POST'])
# def save_data():
#     data = request.json
#     level = data.get('level')

#     # 将 user_data 保存到 JSON 文件
#     with open(f'user_data_{level}.json', 'w') as file:
#         json.dump(user_data, file, indent=4)
    
#     print('save successful!')
#     return jsonify({"status": "data_saved", "level": level})

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    user_Id = data.get('userId')
    level = data.get('level')

    # 将 user_data 转换为 JSON 字符串
    user_data_json = json.dumps(user_data, indent=4)

    # 插入数据到 PostgreSQL 数据库
    with conn.cursor() as cur:
        cur.execute("INSERT INTO user_data (user_ID, level, data) VALUES (%s, %s, %s)", (user_Id, level, user_data_json))
        conn.commit()

    print('save successful!')
    return jsonify({"status": "data_saved", "level": level})


if __name__ == '__main__':
    app.run(debug=True)