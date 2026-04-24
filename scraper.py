import requests
from bs4 import BeautifulSoup
import time

class YahooTaiwanCrawler:
    def __init__(self, stock_id):
        # Yahoo 奇摩股市的網址一律使用 .TW 結尾（上市櫃皆同）
        self.stock_id = stock_id
        self.base_url = f"https://tw.stock.yahoo.com/quote/{self.stock_id}.TW"
        
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
        print(f"Fetching Daily Institutional Data for {self.stock_id}...")
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
                # 它會把這行變成像是 ['2026/04/23', '7,193', '754', '-1,379', '6,569', '70.95%']
                cols = list(row.stripped_strings)
                
                # 判斷這個陣列的第一個元素是不是日期 (包含 '/')
                if len(cols) >= 5 and '/' in cols[0] and len(cols[0]) >= 8:
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
        """抓取資券變化"""
        print(f"Fetching Margin Trading for {self.stock_id}...")
        soup = self.fetch_html("margin")
        if not soup: return None
        
        # 抓取融資融券餘額、增減比例等
        data = {}
        try:
            # 邏輯與法人相同：尋找特定表格列
            # 例：找到標題為「融資餘額」的區塊，並提取其下方的數字
            data = {"資券變化": "HTML 解析邏輯區塊"}
            return data
        except Exception as e:
            return None

    def get_major_holders(self):
        """抓取大戶、董監持股變化"""
        print(f"Fetching Major Holders for {self.stock_id}...")
        soup = self.fetch_html("major-holders")
        if not soup: return None
        
        # 董監持股比例通常會有一個大字體顯示
        data = {}
        try:
            # 尋找頁面中特定的百分比文字區塊
            data = {"大戶持股比例": "HTML 解析邏輯區塊"}
            return data
        except Exception as e:
            return None

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
    crawler = YahooTaiwanCrawler("2330")
    final_data = crawler.run_all()
    print(final_data)
