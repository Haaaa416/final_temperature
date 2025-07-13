import pandas as pd 
import numpy as np
import glob
import os
import time
from tensorflow.keras.models import load_model

# 載入模型
loaded_model = load_model(r'C:\EEG\arduino\LSTM_model_2.h5')


# 初始化變數
output_file = 'predictions.csv'
file_line_counts = {}  # 用來記錄每個檔案已讀取的行數

# 資料夾路徑
folder_path = r"C:\Users\user\OneDrive\桌面\immediate_data\data"

# 構建滑動窗口方法
def create_val_sequences(data, time_steps=3):
    X_val = []
    for i in range(0, len(data) - time_steps + 1):  # 確保i從0開始
        X_val.append(data.iloc[i:i + time_steps][['gamma1_Cz', 'gamma2_Cz', 'gamma3_Cz', 'gamma4_Cz', 'gamma5_Cz', 'gamma6_Cz', 
                                                   'gamma1_Fz', 'gamma2_Fz', 'gamma3_Fz', 'gamma4_Fz', 'gamma5_Fz', 'gamma6_Fz']].values)
    return np.array(X_val)

while True:
    # 搜尋資料夾中所有 .txt 檔案
    txt_files = glob.glob(f"{folder_path}/*.txt")
    
    for file in txt_files:
        # 讀取檔案的資料
        data_val = pd.read_csv(file)
        total_lines = len(data_val)

        # 如果是新檔案或資料增加，處理新增的資料
        if file not in file_line_counts:
            file_line_counts[file] = 0  # 初始化行數為0

        # 檢查新資料
        if file_line_counts[file] < total_lines:
            new_data = data_val.iloc[file_line_counts[file]:total_lines]  # 正確取得新資料範圍

            # 構建驗證資料集
            X_val_new = create_val_sequences(new_data, time_steps=3)
            print(new_data)
            # 如果有新的資料進行預測
            if len(X_val_new) > 0:
                y_pred_val = loaded_model.predict(X_val_new)
                print(y_pred_val)

                # 設置預測的時間點，這裡假設從第 1 秒開始預測第 4 秒，依此類推
                start_time = file_line_counts[file] + 4

                # 儲存預測結果
                predictions_df = pd.DataFrame({
                    'Time (sec)': range(start_time, start_time + len(y_pred_val)),
                    'Prediction': y_pred_val.flatten()
                })

                # 將預測結果轉換為二進位類別 (0 或 1)
                predictions_df['Prediction'] = (predictions_df['Prediction'] > 0.5).astype(int)

                # 將預測結果追加儲存至 CSV
                predictions_df.to_csv(output_file, index=False, mode='a', header=not os.path.exists(output_file))
                print(f"檔案 {file} 的新資料已處理並儲存預測至 {output_file}")

            # 更新行數記錄
            file_line_counts[file] = total_lines
    
    # 等待1秒再檢查新資料（確保每次預測間隔為1秒）
    time.sleep(1)
