import requests
import pandas as pd
import time

def fetch_mops_balance_sheet(year, season):
    """抓取公開資訊觀測站(MOPS)特定年季的上市資產負債表"""
    url = "https://mops.twse.com.tw/mops/web/ajax_t163sb05"
    
    # MOPS 查詢參數 (TYPEK=sii 代表上市，year 必須是民國年)
    payload = {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "TYPEK": "sii", 
        "year": str(year),
        "season": str(season).zfill(2)
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"[*] 正在向 MOPS 發送請求：民國 {year} 年 Q{season} ...")
    
    try:
        # MOPS 伺服器有時較慢，timeout 設稍微長一點
        res = requests.post(url, data=payload, headers=headers, timeout=25)
        res.encoding = 'utf-8' # 確保中文不亂碼
        
        # MOPS 找不到資料時會出現特定字串
        if "查詢無資料" in res.text or "資料庫中查無資料" in res.text:
            print(f"[-] {year} 年 Q{season} 尚無財報資料。")
            return pd.DataFrame()
        
        # 神器登場：使用 pandas 直接解析 HTML 中的所有表格
        dfs = pd.read_html(res.text)
        
        valid_dfs = []
        for df in dfs:
            # 處理 MOPS 常見的雙層表頭 (MultiIndex)
            if isinstance(df.columns, pd.MultiIndex):
                # 拍平表頭，只取最下層的欄位名稱
                df.columns = [col[-1] if isinstance(col, tuple) else col for col in df.columns]
            
            # 如果表格包含「公司代號」，代表是我們要的財報主體
            if '公司代號' in df.columns:
                valid_dfs.append(df)
        
        if not valid_dfs:
            print(f"[-] {year} 年 Q{season} 解析不到有效的表格結構。")
            return pd.DataFrame()
            
        # 將該季各產業的表格垂直合併成一張大表
        combined_df = pd.concat(valid_dfs, ignore_index=True)
        
        # 新增時間標籤，方便之後做時間序列分析
        combined_df['出表年度'] = year
        combined_df['出表季別'] = season
        
        print(f"[+] 成功抓取 {year} 年 Q{season} 資料！共 {len(combined_df)} 筆。")
        return combined_df
        
    except Exception as e:
        print(f"[-] 抓取 {year} 年 Q{season} 時發生錯誤: {e}")
        return pd.DataFrame()

def build_historical_database(start_year, end_year):
    all_seasons_data = []
    
    # 迴圈跑完指定的年份與季別 (1~4季)
    for year in range(start_year, end_year + 1):
        for season in range(1, 5):
            df = fetch_mops_balance_sheet(year, season)
            if not df.empty:
                all_seasons_data.append(df)
            
            # ⚠️ 極度重要：MOPS 防爬蟲機制非常嚴格，務必設定至少 5 秒的間隔！
            time.sleep(8)
            
    if all_seasons_data:
        # 合併所有歷史季報
        final_db = pd.concat(all_seasons_data, ignore_index=True)
        
        # 基礎資料清洗：移除夾雜在中間的重複表頭與空值
        final_db = final_db[final_db['公司代號'] != '公司代號']
        final_db = final_db.dropna(subset=['公司代號'])
        
        # 儲存為 CSV 資料庫
        filename = "mops_balance_sheet_history.csv"
        final_db.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n[+] 完美！歷史財報資料庫已建立，並儲存至：{filename}")
    else:
        print("\n[-] 未抓取到任何資料，請檢查年份設定或網路連線。")

if __name__ == "__main__":
    # 示範抓取 民國 111 年到 112 年 (2022-2023) 的資料
    # 注意：MOPS 必須使用「民國年」(西元年 - 1911)
    build_historical_database(111, 112)