import pickle
from selenium import webdriver
from creds import *
import time
from bs4 import BeautifulSoup
import json
from pprint import pprint
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


def get_sale(link, driver):
    driver.get(link)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    try:
        name = soup.find("div", {"id": "ember57"}).text.strip()
    except:
        name = ""
    try:
        industry = soup.findAll("div", {"class": "t-14"})[1].text.split("·")[0].strip()
    except:
        industry = ""
    try:
        employees = soup.findAll("div", {"class": "t-14"})[1].text.split("·")[1].strip().split(" ")[0]
    except:
        employees = ""
    try:
        dec_makers = soup.find("a", {"data-control-name": "decision_makers_search_link"}).contents[0].strip()
        dec_makers = dec_makers.split("(")[1].split(")")[0]
    except:
        dec_makers = ""
    try:
        website = soup.find("a", {"data-control-name": "visit_company_website"})['href']
    except:
        website = ""
    try:
        code = json.loads(soup.findAll("code")[-3].text)
        linkedin_link = code['flagshipCompanyUrl']
    except:
        linkedin_link = ""
    try:
        growths = [x.text.strip() for x in soup.findAll("dt", {"class": "t-14"})][-3:]
    except:
        growths = []
    ret = [name, industry, employees, dec_makers, website, linkedin_link]
    ret.extend(growths)
    return ret
    


def get_sales(driver):
    with open("urls.txt") as f:
        links = f.readlines()
    
    data = [["Name", "Industry", "Employees", "Decision Makers", "Website", "Linkedin Link", "Growth 6m", "Growth 1y", "Growth 2y"]]
    for link in links:
        link = link.strip()
        data.append(get_sale(link, driver))

    with open("result.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == "__main__":
    driver = webdriver.Chrome('./chromedriver')
    driver.get("https://www.linkedin.com")
    # login(driver)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies: 
        driver.add_cookie(cookie)
    get_sales(driver)
    driver.close()
