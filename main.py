from flask import Flask, render_template, jsonify
import json
import os
import sys

# 确保能导入同目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# 解决 Vue.js 和 Jinja2 语法冲突
# 将 Flask/Jinja2 的变量标记改为 '[[ ]]'，这样 {{ }} 就会被忽略，原样传给 Vue.js
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

# 数据文件路径
DATA_FILE = 'papers_data.json'

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/api/papers')
def get_papers():
    """API: 获取论文数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            print(f"Error reading data file: {e}")
            return jsonify([])
    return jsonify([])

if __name__ == '__main__':
    print("启动 Flask 服务器...")
    print("请在浏览器访问: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
