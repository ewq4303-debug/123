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
            # 通常在一個包含 '資料時間' 字眼的 div 或 span 中
            time_element = soup.find('span', string=lambda t: t and '資料時間' in t)
            if not time_element:
                # 備案：搜尋所有文字包含資料時間的區塊
                time_text = soup.find(text=lambda t: t and '資料時間' in t)
                data['資料日期'] = time_text.split('：')[-1].strip() if time_text else "未找到日期"
            else:
                data['資料日期'] = time_element.text.split('：')[-1].strip()

            # 2. 抓取「法人逐日買賣超」表格的第一列
            # 我們尋找包含日期格式（如 2026/04/23）的列表項目
            rows = soup.find_all('li', class_='List(n)')
            
            for row in rows:
                cols = row.find_all('div')
                # 逐日表的特徵：第一欄通常是日期格式 (XXXX/XX/XX)
                if len(cols) >= 6:
                    date_val = cols[0].text.strip()
                    if '/' in date_val and len(date_val) >= 8:
                        # 這就是「法人逐日買賣超」的第一列
                        data["交易日期"] = date_val
                        data["外資(張)"] = cols[1].text.strip()
                        data["投信(張)"] = cols[2].text.strip()
                        data["自營商(張)"] = cols[3].text.strip()
                        data["合計(張)"] = cols[4].text.strip()
                        break # 抓到最新一筆（最上方那一列）就停止
            
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
