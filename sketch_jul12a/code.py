import serial
import time
import pandas as pd
import os

# 設置串口和波特率
ser = serial.Serial('COM6', 9600)  # 修改為你的Arduino所連接的串口，波特率與Arduino一致
time.sleep(2)  # 等待 Arduino 初始化

# 自動尋找當前目錄中的所有 CSV 檔案
def find_all_csv_files():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    return csv_files

# 尋找 CSV 檔案
csv_files = find_all_csv_files()

if not csv_files:
    print("找不到任何 CSV 檔案")
    ser.close()
    exit()
else:
    print(f"找到以下 CSV 檔案: {csv_files}")

# 發送命令給 Arduino
def send_command(command):
    ser.write(f"{command}\n".encode())  # 將命令發送給 Arduino
    time.sleep(1)  # 等待 Arduino 執行

try:
    for csv_file in csv_files:
        print(f"正在讀取 CSV 檔案: {csv_file}")
        data = pd.read_csv(csv_file)

        for index, row in data.iterrows():
            time_sec = row['Time (sec)']  # 時間列
            prediction = row['Prediction']  # 預測列

            print(f"時間: {time_sec}, 預測: {prediction}")

            if prediction == 0.0:
                send_command(1)  # 發送 1 給 Arduino
                print("發送 1 給 Arduino -> 舒服")
            else:
                send_command(2)
                print("發送 1 給 Arduino -> 不舒服")

            time.sleep(1)  # 每秒執行一次

except KeyboardInterrupt:
    print("程序停止")

finally:
    ser.close()
