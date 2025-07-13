from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    selected_options = []
    data = None

    # 讀取 CSV 數據
    try:
        data = pd.read_csv('predictions7.csv')  # 假設 CSV 檔案與 app.py 同一目錄下
    except Exception as e:
        print(f"Error reading CSV file: {e}")

    if request.method == 'POST':
        input_name = request.form.get('input_name')
        input_age = request.form.get('input_age')
        options = request.form.getlist('options')  # 獲取所有選中的選項

        result = {
            'input_name': input_name,
            'input_age': input_age
        }

        # 根據選中的選項生成 "是" 或 "否"
        if 'option1' in options:
            selected_options.append('是')
        if 'option2' in options:
            selected_options.append('否')

    return render_template('web.html', result=result, selected_options=selected_options, data=data)

if __name__ == '__main__':
    app.run(debug=True)
