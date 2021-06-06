from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

PATH = "./chromedriver"
option = webdriver.ChromeOptions()

prefs = {
        'profile.default_content_setting_values':{
            'notifications': 2
        }
    }
option.add_experimental_option('prefs', prefs)
option.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
driver = webdriver.Chrome(options=option,executable_path='/Users/peiziwu/Downloads/chromedriver')

def login():
    driver.get("https://www.linkedin.com/login")
    # Log in to linkedin
    username = input("Please enter your Linkedln username: ")
    password = input("Please enter your Linkedln password: ")
    usernameInput = driver.find_element_by_id("username")
    usernameInput.send_keys(username)
    passwordInput = driver.find_element_by_id("password")
    passwordInput.send_keys(password)

    signinBtn = driver.find_element_by_class_name("from__button--floating")
    signinBtn.click()

def search(position, location):
    try:
        print("go to search job page...")
        messagingLink = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.ID, "ember23"))
        )
        messagingLink.click()
    except:
        print("fail to open job search page")
        driver.quit()
        return False

    # scrape the message content 
    try:
        print("start to search...")
        messagesPanel = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-box__text-input"))
        )
        inputs = driver.find_elements_by_class_name("jobs-search-box__text-input")
        inputs[0].send_keys(position)
        inputs[3].send_keys(location)

        search_button = driver.find_element_by_class_name("jobs-search-box__submit-button")
        search_button.click()
    except:
        print("fail to search job")
        driver.quit()
        return False
    return True

def fetchData(df, page = 1,loc="China"):
    print("Start to fetch data from page "+ str(page))
    tryCount = 0
    while(tryCount<3):
        try:
            items = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results__list-item"))
            )
            time.sleep(2)
            items = driver.find_elements_by_class_name("jobs-search-results__list-item")
            count = 0
            for item in items:
                try:
                    count += 1
                    time.sleep(2)
                    item.click()
                    item = {}
                    title = driver.find_element_by_class_name("jobs-details-top-card__job-title")
                    company = driver.find_element_by_class_name("jobs-details-top-card__company-url")
                    location = driver.find_element_by_class_name("jobs-details-top-card__bullet")
                    description = driver.find_element_by_class_name("jobs-description-content__text")
                    detail = driver.find_element_by_class_name("jobs-description-details")
                    description = description.text.replace(detail.text,"")
                    item = {"Title": title.text, "Company":company.text,"Location":location.text,"Description":description}
                    key = ""
                    value = ""
                    for info in detail.text.split("\n"):
                        info = info.strip()
                        print(info)
                        if info in ["Industry","Seniority Level","Employment Type","Job Functions"]:
                            if key != "":
                                item[key] = value
                            key = info
                            value = ""
                        else:
                            value += info
                    if key != "" and key not in item:
                        item[key] = value
                    print(item)
                    df = df.append([item], ignore_index=True)
                except Exception as e:
                    print(e)
                    time.sleep(2)
                    continue
            print(count)
            df.to_csv(loc+".csv",encoding="utf_8_sig",index=False)
            nextPages = driver.find_elements_by_class_name("artdeco-pagination__indicator--number")
            morePage = ""
            flag = False
            for pageObj in nextPages:
                if pageObj.text == "…":
                    morePage = pageObj
                elif int(pageObj.text) == page +1:
                    pageObj.click()
                    fetchData(df, page+1,loc)
                    flag = True
                    break
            if str(page) != nextPages[-1].text and not flag:
                morePage.click()
                fetchData(df, page+1, loc)
            return True
        except Exception as e:
            print(e)
            print("error: ")
            tryCount+=1
    
if __name__ == '__main__':    
    login()
    status = search("data analyst","china")
    df = pd.DataFrame(columns=('Title','Company','Location','Employment Type','Seniority Level','Industry','Job Functions','Description'))
    if status:
        fetchData(df,1,loc='china')

    driver.quit()

    login()
    status = search("data analyst","us")
    df = pd.DataFrame(columns=('Title','Company','Location','Employment Type','Seniority Level','Industry','Job Functions','Description'))
    if status:
        fetchData(df,1,loc='us')

    driver.quit()