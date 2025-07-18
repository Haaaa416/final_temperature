# INTRODUCE
## 1.&nbsp;4CH_EEG (C#專案&nbsp;;收訊號以及處理執行檔)
&nbsp;&nbsp;&nbsp;(1)&nbsp;D:\temperature\4CH_EEG\NFT_BLE(expert).sln &nbsp;->&nbsp;點擊開啟 visual studio(紫色的) 專案可以透過右欄找需要更動的程式碼(應用)

<img width="1915" height="884" alt="image" src="https://github.com/user-attachments/assets/9f8fa3c9-54a1-4521-a56e-435a3b91f114" />

&nbsp;&nbsp;&nbsp;(2)主程式&nbsp;＝>&nbsp;Signalform.cs

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=>&nbsp;右鍵點擊Signalform.cs後有一個 **'檢視程式碼'**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=>&nbsp;主要作用:連線、處理收資料(位元數)、濾波、體動、計算stft(分為baseline、data)、平均數值、儲存到特定資料夾

&nbsp;&nbsp;&nbsp;(3)收資料主要介面&nbsp;=>&nbsp;Signalform.cs[設計]

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=>&nbsp;操作說明&nbsp;: &nbsp;(I)&nbsp;先連線後(CONNECT)，檢查資料是否寫入(這步驟教過)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(II)&nbsp;收baseline&nbsp;&nbsp;&nbsp;點擊 **'BASELINE'** 結束後點擊 **'STOP'**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;(III)&nbsp;收被照紅外線資料&nbsp;&nbsp;&nbsp;點擊 **'START'** 結束後點擊 **'STOP'**

&nbsp;&nbsp;&nbsp;(4)濾波參數設定&nbsp;＝>&nbsp;Filter.cs

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=>&nbsp;主要作用:寫濾波參數，設定低通濾波、高通濾波、帶阻濾波器

```
%matlab程式碼
%從MATLAB獲取濾波係數
Fs=250;

lpFilt = designfilt('lowpassiir', ...
'FilterOrder',15, ...
'HalfPowerFrequency',100, ...
'DesignMethod','butter', ...
'SampleRate',Fs);

hpFilt = designfilt('highpassiir', ...
'FilterOrder',8, ...
'HalfPowerFrequency',1.0, ...
'DesignMethod','butter', ...
'SampleRate',Fs);

notch_EMG = designfilt('bandstopiir','FilterOrder',8, ...
'HalfPowerFrequency1',59,'HalfPowerFrequency2',61, ...
'DesignMethod','butter','SampleRate',Fs);

round(lpFilt.Coefficients, 6)
round(hpFilt.Coefficients, 6)
round(notch_EMG.Coefficients, 6)
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=>&nbsp;獲取係數後寫進去Filter.cs做參數處理，最終使用 **'SportIIRFilter'** 進行濾波

&nbsp;&nbsp;&nbsp;(5)執行的話可以點擊 **'開始'**，或者 **'D:\temperature\4CH_EEG\NFT_BLE(expert)\bin\Debug\NFT_BLE(expert).exe'**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=>&nbsp;操作說明&nbsp;: &nbsp;如 **'Signalform.cs[設計]'** 介紹

<img width="1377" height="829" alt="image" src="https://github.com/user-attachments/assets/d8b30260-a991-4f28-aa5a-53799b8641cc" />

## 2.&nbsp;immediate_data(資料夾檔案&nbsp;;4CH_EEG輸出後的檔案&nbsp;->&nbsp;txt)

&nbsp;&nbsp;&nbsp;(1)&nbsp;D:\temperature\immediate_data&nbsp;分為&nbsp;**'baseline'** 與 **'data'**

&nbsp;&nbsp;&nbsp;(2)&nbsp;baseline又分為&nbsp;**'CH1'** 與 **'CH2'**

&nbsp;&nbsp;&nbsp;(3)&nbsp;baseline開始後每秒產生一個檔案,為計算後(STFT的結果)有129行對應到(SX)，只取第6個到第21個檔案取平均進行後續運算

&nbsp;&nbsp;&nbsp;(4)&nbsp;data裡面是開始收照光的資料後每秒資料被baseline平均除以後進行計算STFT取特定頻段出來，如下圖範圍

<img width="937" height="294" alt="image" src="https://github.com/user-attachments/assets/0f01d272-741b-4e6d-9a40-a3590ab8cea0" />

## 3.&nbsp;predict_web(網頁&nbsp;;物理治療師使用介面)

&nbsp;&nbsp;&nbsp;(1)&nbsp;D:\temperature\predict_web&nbsp;分為很多檔案

&nbsp;&nbsp;&nbsp;(2)&nbsp;D:\temperature\predict_web\templates\index.html &nbsp;&nbsp;是物理治療師使用介面的網頁設計(包含html、css、js)

&nbsp;&nbsp;&nbsp;(3)&nbsp;D:\temperature\predict_web\1.py &nbsp;&nbsp;是額外檢查計算收到的資料狀況

&nbsp;&nbsp;&nbsp;(4)&nbsp;D:\temperature\predict_web\num.py &nbsp;&nbsp;是模擬被照光後處理過的資料，介於[0 1]之間，產生numbers.txt檔案當模擬資料

&nbsp;&nbsp;&nbsp;(5)&nbsp;D:\temperature\predict_web\*.h5 &nbsp;&nbsp;是訓練過後的不同部位以及全部的部位一起訓練後的模型參數

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; =>&nbsp;&nbsp; 依序為 **左手、右手、雙手、左肩、右肩、後背、後腰、左大腿、右大腿、左小腿、右小腿**

&nbsp;&nbsp;&nbsp;(6)&nbsp;D:\temperature\predict_web\predictions.csv &nbsp;&nbsp;是web.py執行後讀取資料進行訓練後的結果

&nbsp;&nbsp;&nbsp;(7)&nbsp;D:\temperature\predict_web\web.py &nbsp;&nbsp;是**物理治療師使用介面**最主要的程式，透過讀取/templates/index.html的結果傳到此程式碼進行後端計算、畫圖、將資料存到資料庫

## 4.&nbsp;sketch_jul12a(python與c&nbsp;;arduino與繼電器控制檔案)

&nbsp;&nbsp;&nbsp;(1)&nbsp;D:\temperature\sketch_jul12a&nbsp;分為&nbsp;**'code.py'** 與 **'sketch_jul12a.ino'**

&nbsp;&nbsp;&nbsp;(2)&nbsp;D:\temperature\sketch_jul12a\code.py &nbsp;是python程式碼控制紅外線的程式，arduino得到資料後控制繼電器進行切換

&nbsp;&nbsp;&nbsp;(3)&nbsp;D:\temperature\sketch_jul12a\sketch_jul12a.ino &nbsp;是arduino程式碼控制繼電器的程式，同時會把程式碼寫入檔案裡

## 5.&nbsp;model.py(python&nbsp;;檢查數值預測)

D:\temperature\immediate_data\data，檢查計算收到的資料狀況

## 6.&nbsp;numbers.txt(python&nbsp;;模擬資料)

D:\temperature\predict_web\num.py中模擬資料可以進行預測，可替代&nbsp;'D:\temperature\immediate_data\'

# TEST

## 分為四種測試&nbsp; 

### 1.**'4CH_EEG專案是否可以運行'** 

&nbsp;&nbsp;&nbsp;(1)&nbsp;更改Signalform.cs這段程式碼中路徑位置（immediate_data），看想放哪吧，有很多段都要改。

&nbsp;&nbsp;&nbsp;(2)&nbsp;執行Signalform.cs程式碼，步驟可以抄上面的，檢查是否有產**'baseline'** **'data'**中的txt檔案

### 2.**'predict_web是否可以預測以及儲存資料給資料庫'** 

### 3.**'sketch_jul12a是否可以讓紅外線切換(邏輯正確)'** 

### 4.**'一整套流程串起來'**


# START
