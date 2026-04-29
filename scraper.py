import requests
from bs4 import BeautifulSoup
import time
import json # 在檔案最上方加入這個 import
import os
import sys # 記得在檔案最上面 import sys
import datetime

class YahooTaiwanCrawler:
    def __init__(self, stock_id):
        # Yahoo 奇摩股市的網址一律使用 .TW 結尾（上市櫃皆同）
        self.stock_id = stock_id
        self.base_url = f"https://tw.stock.yahoo.com/quote/{self.stock_id}.TW"
        # 儲存目標日期，例如 "2026/04/23"
        self.target_date = target_date
        
        # 必須偽裝 User-Agent，否則 Yahoo 會阻擋爬蟲並回傳 404 或要求驗證
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_html(self, endpoint):
        """共用的 HTTP 請求模組"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_institutional_trading(self):
        """抓取『法人逐日買賣超』最新一筆資料與資料日期"""
        print(f"Fetching Institutional Trading Data for {self.stock_id}... Target Date: {self.target_date}")
        soup = self.fetch_html("institutional-trading")
        if not soup: return None
        
        data = {}
        try:
            # 1. 抓取網頁右上角的「資料時間」
            # bs4 建議使用 string 來搜尋純文字節點
            time_element = soup.find(string=lambda t: t and '資料時間' in t)
            if time_element:
                data['資料日期'] = time_element.split('：')[-1].strip()
            else:
                data['資料日期'] = "抓取不到"

            # 2. 抓取「法人逐日買賣超」表格的第一列
            rows = soup.find_all('li', class_='List(n)')
            
            for row in rows:
                # 🚀 爬蟲必殺技：stripped_strings 自動剝除所有 HTML 標籤，只留下乾淨的陣列
                cols = list(row.stripped_strings)
                
                # 判斷這個陣列的第一個元素是不是日期 (包含 '/')
                if len(cols) >= 5 and '/' in cols[0] and len(cols[0]) >= 8:
                    row_date = cols[0] # 抓出這行的日期
                    # 🚀 關鍵邏輯：如果有指定日期，且這行的日期不等於指定日期，就跳過繼續找下一行！
                    if self.target_date and row_date != self.target_date:
                        continue
                        
                    data["交易日期"] = cols[0]
                    data["外資(張)"] = cols[1]
                    data["投信(張)"] = cols[2]
                    data["自營商(張)"] = cols[3]
                    data["合計(張)"] = cols[4]
                    break # 抓到最新一筆就跳出迴圈
            
            if not data:
                data = {"Error": "找不到符合格式的資料列"}
                
            return data
        except Exception as e:
            return {"Error": f"解析失敗: {str(e)}"}

    def get_margin_trading(self):
        """抓取『資券餘額逐日增減』最新一筆資料"""
        print(f"Fetching Margin Data for {self.stock_id}... Target Date: {self.target_date}")
        soup = self.fetch_html("margin")
        if not soup: return None
        
        data = {}
        try:
            # 尋找包含資料的表格列
            rows = soup.find_all('li', class_='List(n)')
            
            for row in rows:
                # 再次使用必殺技：剝除標籤，只取純文字陣列
                cols = list(row.stripped_strings)
                
                # 判斷第一個元素是不是日期，並且確認陣列長度足夠 (至少要能抓到 index 7)
                if len(cols) >= 8 and '/' in cols[0] and len(cols[0]) >= 8:
                    row_date = cols[0] # 抓出這行的日期
                    # 🚀 關鍵邏輯：如果有指定日期，且這行的日期不等於指定日期，就跳過繼續找下一行！
                    if self.target_date and row_date != self.target_date:
                        continue
                    # 依照我們剛剛分析的索引位置，把數字抓出來
                    data["資料日期"] = cols[0]
                    data["融資增減"] = cols[1]
                    data["融資使用率"] = cols[3]
                    data["融券餘額"] = cols[5]
                    data["券資比"] = cols[7]
                    break # 抓到最新一日的資料就跳出迴圈
            
            if not data:
                data = {"Error": "找不到符合格式的資券資料"}
                
            return data
        except Exception as e:
            return {"Error": f"解析失敗: {str(e)}"}

    def get_major_holders(self):
        """抓取『大戶籌碼』最新一筆資料"""
        print(f"Fetching Major Holders Data for {self.stock_id}... Target Date: {self.target_date}")
        soup = self.fetch_html("major-holders")
        if not soup: return None
        
        data = {}
        try:
            # 尋找包含資料的表格列
            rows = soup.find_all('li', class_='List(n)')
            
            for row in rows:
                # 使用 stripped_strings 剝除標籤，轉為乾淨的純文字陣列
                cols = list(row.stripped_strings)
                
                # 判斷第一個元素是不是日期，並且確認陣列長度足夠
                if len(cols) >= 4 and '/' in cols[0] and len(cols[0]) >= 8:
                    row_date = cols[0] # 抓出這行的日期
                    
                    # 🚀 關鍵邏輯：如果有指定日期，且這行的日期不等於指定日期，就跳過繼續找下一行！
                    if self.target_date and row_date != self.target_date:
                        continue
                    data["資料日期"] = cols[0]
                    data["外資籌碼"] = cols[1]
                    data["大戶籌碼"] = cols[2]
                    data["董監持股"] = cols[3]
                    break # 抓到最新一筆資料就跳出迴圈
            
            if not data:
                data = {"Error": "找不到符合格式的持股資料"}
                
            return data
        except Exception as e:
            return {"Error": f"解析失敗: {str(e)}"}

    def run_all(self):
        result = {"Stock ID": self.stock_id}
        
        # 加入延遲避免被鎖 IP
        result['Institutional'] = self.get_institutional_trading()
        time.sleep(1)
        result['Margin'] = self.get_margin_trading()
        time.sleep(1)
        result['Holders'] = self.get_major_holders()
        
        return result

# 測試執行
if __name__ == "__main__":
    # 接收 GitHub 傳進來的參數，如果沒有就留白
    target_date = sys.argv[1] if len(sys.argv) > 1 else ""
    
    # 把目標日期傳進爬蟲裡 (我們等一下要修改 Crawler 的寫法)
    crawler = YahooTaiwanCrawler("2330", target_date)
    final_data = crawler.run_all()
    
    # 存檔邏輯... (如果 target_date 有值，就用 target_date 當 Key，否則用今天)
    save_key = target_date.replace("/", "-") if target_date else datetime.datetime.now().strftime("%Y-%m-%d")
    
    file_path = "stock_data.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try: history_data = json.load(f)
            except: history_data = {}
    else:
        history_data = {}
        
    history_data[save_key] = final_data
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
        
    print(f"資料已成功儲存至 {file_path}")
