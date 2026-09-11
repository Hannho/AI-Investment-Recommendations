import requests
from collections import defaultdict

def find_high_debt_ratio_companies(debt_threshold=0.7):
    """
    找出各產業中，最新一季「負債比率 (負債總額/資產總額)」大於指定門檻的公司。
    :param debt_threshold: 負債比率門檻 (預設 0.7，即 70%)
    """
    
    industry_endpoints = {
        "一般業": "https://openapi.twse.com.tw/v1/opendata/t187ap07_L_ci",
        "金控業": "https://openapi.twse.com.tw/v1/opendata/t187ap07_L_fh",
        "保險業": "https://openapi.twse.com.tw/v1/opendata/t187ap07_L_ins",
        "證券期貨業": "https://openapi.twse.com.tw/v1/opendata/t187ap07_L_bd",
        "異業": "https://openapi.twse.com.tw/v1/opendata/t187ap07_L_mim"
    }

    # 定義要抓取的會計科目關鍵字
    debt_keys = ["負債總額", "負債總計"]
    asset_keys = ["資產總額", "資產總計"]

    print(f"[-] 開始分析各產業最新財報，尋找負債比率大於 {debt_threshold*100}% 的公司...\n")

    for industry_name, url in industry_endpoints.items():
        print(f"[*] 正在獲取【{industry_name}】財報資料...")
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"  [-] 獲取失敗 (狀態碼: {response.status_code})")
                continue
                
            data = response.json()
            if not data:
                print("  [-] 該產業目前無資料。")
                continue

            high_debt_companies = []
            
            for row in data:
                corp_id = row.get("公司代號")
                corp_name = row.get("公司名稱")
                year = row.get("出表年度", "未知")
                season = row.get("出表季別", "未知")
                
                # 取得負債總額
                debt_value = None
                for key in debt_keys:
                    if key in row and row[key]:
                        try:
                            debt_value = float(row[key].replace(",", ""))
                            break
                        except ValueError:
                            pass
                            
                # 取得資產總額
                asset_value = None
                for key in asset_keys:
                    if key in row and row[key]:
                        try:
                            asset_value = float(row[key].replace(",", ""))
                            break
                        except ValueError:
                            pass
                
                # 計算負債比
                if corp_id and debt_value and asset_value and asset_value > 0:
                    debt_ratio = debt_value / asset_value
                    
                    if debt_ratio >= debt_threshold:
                        # 為了版面乾淨，金額轉換為「億」元
                        debt_in_hundred_million = debt_value / 100000
                        high_debt_companies.append({
                            "id": corp_id,
                            "name": corp_name,
                            "period": f"{year}Q{season}",
                            "ratio": debt_ratio,
                            "debt_amt": debt_in_hundred_million
                        })

            # 依照負債比率由高到低排序
            high_debt_companies.sort(key=lambda x: x["ratio"], reverse=True)

            if high_debt_companies:
                print(f"  [+] 發現 {len(high_debt_companies)} 家高負債比公司 (列出前 10 名)：")
                # 只印出前 10 名避免洗版
                for comp in high_debt_companies[:10]:
                    print(f"      - {comp['id']} {comp['name']} ({comp['period']}): 負債比 {comp['ratio']*100:.2f}% (負債總額約 {comp['debt_amt']:.2f} 億)")
            else:
                print(f"  [-] 無公司負債比率超過 {debt_threshold*100}%。")
                
            print("-" * 60)

        except Exception as e:
            print(f"  [-] 處理發生錯誤: {e}")

    print("\n[+] 財報掃描完畢！")

if __name__ == "__main__":
    find_high_debt_ratio_companies(debt_threshold=0.7)