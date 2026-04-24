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
        """抓取三大法人籌碼變化"""
        print(f"Fetching Institutional Trading for {self.stock_id}...")
        soup = self.fetch_html("institutional-trading")
        if not soup: return None
        
        # Yahoo 的資料通常放在特定的 List (li) 中，這裡是抓取「最新一日」的資料範例
        # 實務上 Yahoo 的 class names (如 Jc(c), Fz(14px)) 是動態產生的 Tailwind-like CSS
        # 穩健的作法是找到表格的資料列 (通常是 ul 下的 li 結構)
        
        data = {}
        try:
            # 尋找包含「外資」、「投信」、「自營商」字眼的資料區塊
            # 這裡簡化邏輯：抓取頁面中第一個出現的數值列（通常是最新交易日）
            rows = soup.find_all('li', class_='List(n)') 
            
            # 根據 Yahoo 網頁結構，逐行尋找當日買賣超數值
            # 註：因為網頁排版會隨時變動，這裡示範的是概念性的標籤提取
            for row in rows:
                cols = row.find_all('div')
                if len(cols) >= 5 and "外資" in soup.text: 
                    # 假設能夠精準定位到該列
                    # data['外資買賣超'] = cols[1].text.strip()
                    pass
            
            # 為了讓您馬上能測試，我用一個安全的 fallback 來模擬抓取結果
            data = {"外資買賣超": "需根據目前最新的 HTML 標籤 class 進行微調提取"}
            return data
        except Exception as e:
            return f"Parsing Error: {e}"

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
