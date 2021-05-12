import pickle
from selenium import webdriver
from creds import *
import time
from bs4 import BeautifulSoup
import json
import csv


def login(driver):
    link = "https://www.linkedin.com/login"
    driver.get(link)
    username = driver.find_element_by_xpath("//input[@id='username']")
    password = driver.find_element_by_xpath("//input[@id='password']")
    submit = driver.find_element_by_xpath("//button[@type='submit']")
    username.send_keys(user)
    password.send_keys(passwd)
    submit.click()
    time.sleep(2)
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))


def get_sale(link, driver, data):
    driver.get(link)
    time.sleep(4)
    html = driver.page_source
    # with open("test.txt", "w", encoding="utf-8") as f:
    #     f.write(html)
    soup = BeautifulSoup(html, "html.parser")
    try:
        name = soup.find("div", {"id": "ember57"}).text.strip()
    except:
        name = ""
    try:
        industry = soup.findAll(
            "div", {"class": "t-14"})[1].text.split("·")[0].strip()
    except:
        industry = ""
    try:
        employees = soup.findAll(
            "div", {"class": "t-14"})[1].text.split("·")[1].strip().split(" ")[0]
    except:
        employees = ""
    try:
        location = soup.find(
            "div", {"class": "t-12 t-black--light"}).text.strip()
    except:
        location = ""
    try:
        dec_makers = soup.find(
            "a", {"data-control-name": "decision_makers_search_link"}).contents[0].strip()
        dec_makers = dec_makers.split("(")[1].split(")")[0]
    except:
        dec_makers = ""
    try:
        website = soup.find(
            "a", {"data-control-name": "visit_company_website"})['href']
    except:
        website = ""
    try:
        code = json.loads(soup.findAll("code")[-3].text)
        linkedin_link = code['flagshipCompanyUrl']
    except:
        linkedin_link = ""
    try:
        growths = [x.text.strip()[:-1]
                   for x in soup.findAll("dt", {"class": "t-14"})][-3:]
    except:
        growths = ["", "", ""]

    if(len(growths) < 3):
        growths = ["", "", ""]

    if name in data.keys():
        for i in range(3):
            if growths[i] > data[name][i]:
                data[name][i] = growths[i]
                growths[i] += " ++"
            elif growths[i] < data[name][i]:
                data[name][i] = growths[i]
                growths[i] += " --"
    else:
        data[name] = growths
    ret = [name, industry, employees, location,
           dec_makers, website, linkedin_link]
    ret.extend(growths)
    print(name)
    return ret


def get_sales(driver):
    with open("urls.txt") as f:
        links = f.readlines()
    with open("data.json") as f:
        d = json.load(f)
    data = [["Name", "Industry", "Employees", "Location", "Decision Makers",
             "Website", "Linkedin Link", "Growth 6m", "Growth 1y", "Growth 2y"]]
    for link in links:
        link = link.strip()
        try:
            data.append(get_sale(link, driver, d))
        except:
            pass
    with open("data.json", "w", encoding='utf-8') as f:
        json.dump(d, f)
    with open("result.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.get("https://www.linkedin.com")
    # login(driver)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    get_sales(driver)
    driver.close()
