from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time


SLEEP_TIME = 5


def check_missing_index(K, n_rows, n_rows_per_page, n_rows_total):
    if n_rows == n_rows_per_page:
        return []

    if K + n_rows - 1 == n_rows_total:
        return []

    if K + n_rows_per_page - 1 >= n_rows_total:
        return [i-1 for i in range(K+n_rows, n_rows_total+1)]

    return [i-1 for i in range(K+n_rows, K+n_rows_per_page)]


def get_data(wait: WebDriverWait):
    table = wait.until(EC.presence_of_element_located((By.ID, "scr-res-table")))
    html = table.get_attribute("outerHTML")
    return pd.read_html(html)[0]


def get_csv(SLEEP_TIME):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    WEB_URL = "https://finance.yahoo.com/screener/unsaved/16bfab57-05ce-4488-bb85-95370abf8416?count=100&offset=0"
    driver = webdriver.Chrome(options, service)
    driver.get(WEB_URL)
    time.sleep(SLEEP_TIME)

    wait = WebDriverWait(driver, 10)

    CSS_SORT_BY_SYMBOL = "#scr-res-table > div.Ovx\(a\).Ovx\(h\)--print.Ovy\(h\).W\(100\%\) > table > thead > tr > th.Ta\(start\).Pstart\(6px\).Pend\(10px\).Miw\(90px\).Fz\(xs\).Py\(5px\)\!.Bgc\(\$lv3BgColor\).Va\(m\).Cur\(p\).Bgc\(\$hoverBgColor\)\:h.Fw\(400\)\!.Ta\(start\).Start\(0\).Pend\(10px\).Pos\(st\).Bgc\(\$lv3BgColor\).Z\(1\).Ta\(start\)\!"
    CSS_SHOW_N_ROWS = "#scr-res-table > div.W\(100\%\).Mt\(15px\).Ta\(end\) > span > div > span"
    CSS_DATA_INDICES = "#fin-scr-res-table > div.W\(100\%\) > div.D\(ib\).Fz\(m\).Fw\(b\).Lh\(23px\).W\(75\%\)--mobp > span.Mstart\(15px\).Fw\(500\).Fz\(s\) > span"

    sort_by_symbol = driver.find_element(By.CSS_SELECTOR, CSS_SORT_BY_SYMBOL)
    driver.execute_script("arguments[0].click();", sort_by_symbol)
    time.sleep(SLEEP_TIME)

    show_n_rows = driver.find_element(By.CSS_SELECTOR, CSS_SHOW_N_ROWS)
    n_rows_per_page = int(show_n_rows.text.split("Show ")[1].split(" rows")[0])

    data_indices = driver.find_element(By.CSS_SELECTOR, CSS_DATA_INDICES)
    n_rows_total = int(data_indices.text.split(" of ")[1].split(" results")[0])

    K = int(driver.current_url.split("https://finance.yahoo.com/screener/unsaved/16bfab57-05ce-4488-bb85-95370abf8416?count=100&offset=")[1]) + 1
    n_rows = int(data_indices.text.split(" of ")[0].split("-")[1]) - K + 1
    CSS_BUTTON_NEXT = "#scr-res-table > div.W\(100\%\).Mt\(15px\).Ta\(end\) > button.Va\(m\).H\(20px\).Bd\(0\).M\(0\).P\(0\).Fz\(s\).Pstart\(10px\).O\(n\)\:f.Fw\(500\).C\(\$linkColor\)"
    list_missing_index = []
    button_next = driver.find_element(By.CSS_SELECTOR, CSS_BUTTON_NEXT)

    while True:
        df = get_data(wait)
        try:
            df_old
            if len(df) == 0 or df_old.iloc[0]["Symbol"] == df.iloc[0]["Symbol"]:
                driver.refresh()
                time.sleep(SLEEP_TIME)
                sort_by_symbol = driver.find_element(By.CSS_SELECTOR, CSS_SORT_BY_SYMBOL)
                driver.execute_script("arguments[0].click();", sort_by_symbol)
                time.sleep(SLEEP_TIME)
                print("Refreshed")
                button_next = driver.find_element(By.CSS_SELECTOR, CSS_BUTTON_NEXT)
                df = get_data(wait)
        except:
            pass

        try:
            data = pd.concat([data, df])
        except:
            data = df

        df_old = df

        print(K, len(df))
        n_rows = len(df)
        list_missing_index += check_missing_index(K, n_rows, n_rows_per_page, n_rows_total)

        try:
            driver.execute_script("arguments[0].click();", button_next)
            time.sleep(SLEEP_TIME)
            K_OLD = K
            K = int(driver.current_url.split("https://finance.yahoo.com/screener/unsaved/16bfab57-05ce-4488-bb85-95370abf8416?count=100&offset=")[1]) + 1
            if K_OLD == K:
                raise
        except:
            break

    driver.quit()
    return data.drop_duplicates(subset=["Symbol"]).reset_index(drop=True), n_rows_total, list_missing_index


for i in range(10):
    data, n_rows_total, list_missing_index = get_csv(SLEEP_TIME)
    if len(data) + len(list_missing_index) != n_rows_total:
        SLEEP_TIME += 1
        print("Sleep time:", SLEEP_TIME)
    else:
        break
else:
    raise

print(len(data))
data.to_csv("Italy_coms.csv", index=False)
