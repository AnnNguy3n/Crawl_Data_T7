from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time


df_coms = pd.read_csv("Italy_coms.csv")


def get_shares_outstanding(driver, wait: WebDriverWait, com):
    try:
        driver.get(f"https://finance.yahoo.com/quote/{com}/key-statistics?p={com}")
        shares_outstanding = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#Col1-0-KeyStatistics-Proxy > section > div.Mstart\(a\).Mend\(a\) > div.Fl\(end\).W\(50\%\).smartphone_W\(100\%\) > div > div:nth-child(2) > div > div > table > tbody > tr:nth-child(3)")))
        if not shares_outstanding.text.startswith("Shares Outstanding"):
            raise

        value = shares_outstanding.find_element(By.CSS_SELECTOR, "#Col1-0-KeyStatistics-Proxy > section > div.Mstart\(a\).Mend\(a\) > div.Fl\(end\).W\(50\%\).smartphone_W\(100\%\) > div > div:nth-child(2) > div > div > table > tbody > tr:nth-child(3) > td.Fw\(500\).Ta\(end\).Pstart\(10px\).Miw\(60px\)")
        return value.text
    except:
        return None

def get_sectors_and_industry(driver, wait: WebDriverWait, com):
    try:
        driver.get(f"https://finance.yahoo.com/quote/{com}/profile?p={com}")
        infor = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#Col1-0-Profile-Proxy > section > div.asset-profile-container > div > div > p.D\(ib\).Va\(t\)")))
        temp = infor.text.split("\n")
    except:
        return None, None

    try:
        assert temp[0].startswith("Sector(s):")
        if1 = temp[0].split("Sector(s): ")[1]
    except:
        if1 = None

    try:
        assert temp[1].startswith("Industry:")
        if2 = temp[1].split("Industry: ")[1]
    except:
        if2 = None

    return if1, if2


def get_csv(K, n, df_coms):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options, service)

    wait = WebDriverWait(driver, 10)

    Done = []
    IF1 = []
    IF2 = []
    IF3 = []
    for i in range(K*n, n+K*n):
        if i >= len(df_coms):
            break

        com = df_coms.iloc[i]["Symbol"]
        Done.append(com)
        if1 = get_shares_outstanding(driver, wait, com)
        if2, if3 = get_sectors_and_industry(driver, wait, com)
        IF1.append(if1)
        IF2.append(if2)
        IF3.append(if3)
        print(i, com, if1, if2, if3)

    driver.quit()
    return pd.DataFrame({"Symbol": Done,
                         "Shares Outstanding": IF1,
                         "Sector(s)": IF2,
                         "Industry": IF3})

K = 0
data = get_csv(K, len(df_coms), df_coms)
data.to_csv(f"Data_{K}.csv", index=False)