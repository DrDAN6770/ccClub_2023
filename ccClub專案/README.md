# Final Project

# 主題 : 電影推薦
## 總攬
1. 依使用者偏好的**電影類型及分類等等**，從**資料庫進行動態篩選**，得到隨機推薦 3 部電影。
2. 依照使用者的位置，透過 **GoogleMap API** 與**全台電影院位置數據庫**取得資料，回傳離使用者**交通距離最近的前 3 個戲院路線規劃(當下最佳路線)**。
3. 依照使用者指定電影，**爬取相關電影資訊及最新評論**。
4. 透過 **Flask** 在 **LINE Bot** 呈現上述功能

## 結果
* [Project Report](https://github.com/DrDAN6770/ccClub_2023/blob/main/ccClub%E5%B0%88%E6%A1%88/report.pdf)

* [Youtube Video](https://www.youtube.com/watch?v=6yp2f9DsdUk)
    * **歡迎訊息與選單**
  
    ![image](https://github.com/DrDAN6770/ccClub_2023/assets/118630187/f7b4ef1b-89a5-4fd4-a076-42e6e2cb3708)

    * **附近戲院功能**
     
    ![image](https://github.com/DrDAN6770/ccClub_2023/assets/118630187/fde70628-5cb0-4ea5-9a8d-537ce602cf05)

    * **隨機推薦功能**

    ![image](https://github.com/DrDAN6770/ccClub_2023/assets/118630187/e421a83a-1dd6-46f3-bef8-c3b21587fa54)

    * **搜尋電影資訊與評論功能**
  
    ![image](https://github.com/DrDAN6770/ccClub_2023/assets/118630187/8c83e4cc-26da-4c4a-a6d0-723d86c235b1)


## 進度
1. Yahoo & IMDb 電影評論、基本資料爬蟲
2. 全台電影院名稱地址建立資料庫
3. 透過GoogleMap API 計算經緯度並求得兩點距離(戲院、使用者位置)
4. 全台電影院資料串接經緯度、GoogleMap 頁面
5. 透過GoogleMap API，預估使用者到附近戲院的時間、路線規劃
6. 電影資料庫建立、電影類別、中文片名爬蟲
7. 建立LINE Bot互動介面，導入各項功能
8. 清理DB、處理動態篩選功能
9. 整理report、各功能及輸出介面修正
9. 佈署雲端

## 問題
1. 希望讓LINE Bot 紀錄使用者輸入的內容，一收一發，評論出不來 **(已解決)**
2. LINE Bot GoogleMap連結出不來 **(已解決)**
3. 電影隨機推薦，國家語言連在一起問題 **(已解決)**
4. 電影資料庫，部分電影無中文翻譯 **(已解決)**
5. LINE Bot 部署雲端
6. 原計畫有串聯chat GTP，但無法限制回覆格式，且資訊多為2021以前，故決定取消 **(已解決)**

## 作者
組員：[DAN](https://github.com/DrDAN6770)、[C06NOEL](https://github.com/C06NOEL)、[Natalie](https://www.linkedin.com/in/yi-ling-wu-b0957816a/)、[ysirene](https://github.com/ysirene)
