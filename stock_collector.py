import requests
import csv

def get_all_market_stock_data():
    # 改用證交所 OpenAPI 官方專用網址！(穩定、不擋 IP)
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"

    print("[-] 正在從證交所 OpenAPI 拉取全市場所有個股資料...")

    try:
        # OpenAPI 不太需要複雜的 headers
        response = requests.get(url, timeout=25)

        if response.status_code != 200:
            print(f"[-] 請求失敗，HTTP 狀態碼: {response.status_code}")
            return

        # OpenAPI 直接回傳乾淨的 JSON Array (List of Dictionaries)
        data = response.json()

        if not data:
            print("[-] 沒有抓取到資料。")
            return

        total_count = len(data)
        print(f"[-] 成功拉取資料，共計 {total_count} 筆股票資訊。")

        # 取得表頭 (從第一筆資料的字典 keys 提取)
        fields = list(data[0].keys())

        # --- 將資料儲存成 CSV 檔案 ---
        filename = "twse_all_stocks_latest.csv"
        with open(filename, mode='w', encoding='utf-8-sig', newline='') as file:
            # 使用 DictWriter 直接寫入字典資料
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)

        print(f"\n[+] 完美！資料已成功儲存至檔案: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"[-] 網路請求發生錯誤: {e}")
    except Exception as e:
        print(f"[-] 發生未知錯誤: {e}")

if __name__ == "__main__":
    get_all_market_stock_data()