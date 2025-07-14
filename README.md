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

&nbsp;&nbsp;&nbsp;(2)&nbsp;baseline開始後每秒產生一個檔案(250個點),為原始訊號？(忘ㄌ),取幾筆出來？


&nbsp;&nbsp;&nbsp;(3)&nbsp;

## 3.&nbsp;predict_web(網頁&nbsp;;物理治療師使用介面)
&nbsp;&nbsp;&nbsp;(1)&nbsp;D:\temperature\predict_web&nbsp;分為如下
## 4.&nbsp;sketch_jul12a(python與c&nbsp;;arduino與繼電器控制檔案)
&nbsp;&nbsp;&nbsp;(1)&nbsp;D:\temperature\sketch_jul12a&nbsp;分為&nbsp;**'code.py'** 與 **'sketch_jul12a.ino'**
## 5.&nbsp;model.py(python&nbsp;;檢查數值預測)
D:\temperature\immediate_data\data
## 6.&nbsp;numbers.txt(python&nbsp;;模擬資料)
D:\temperature\predict_web\num.py中模擬資料可以進行預測，可替代&nbsp;'D:\temperature\immediate_data\'

# TEST
## 分為四種測試&nbsp; 
### 1.**'4CH_EEG專案是否可以運行'** 
### 2.**'predict_web是否可以預測以及儲存資料給資料庫'** 
### 3.**'sketch_jul12a是否可以讓紅外線切換(邏輯正確)'** 
### 4.**'一整套流程串起來'**


# START
