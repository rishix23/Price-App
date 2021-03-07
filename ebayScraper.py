
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def create_webdriver_instance():
    print("starting ebay scrap")
    #Initialization method. 
    driver = webdriver.Chrome(executable_path=os.popen('which chromedriver').read().strip())
    driver.chrome_options = webdriver.ChromeOptions()
    driver.base_url = 'https://www.ebay.co.uk/'
    return driver

def search_criteria(driver, search_term):
    xpath = '//input[@id="gh-ac"]'
    search_input = driver.find_element_by_xpath(xpath)
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    return True

def get_cards(driver):
    xpath = '//*[@class="s-item    s-item--watch-at-corner"]'
    cards_found = driver.find_elements_by_xpath(xpath)
    print(len(cards_found))
    return cards_found

def get_card_info(driver, cards_found):
    cards_info = []
    # title_xpath = ('//h3[@class="s-item__title"]/@value').get_attribute("value")
    # price_xpath = ('//span[@class="s-item__price"]/@value').get_attribute("value")

    for card in cards_found:
        title = driver.find_element_by_xpath('//h3[@class="s-item__title"]')
        title = title.text
        print(title)
        price = driver.find_element_by_xpath('//span[@class="s-item__price"]')
    #     cards_info.append(title)
    # for info in cards_info:
    #     print(info)

def generate_ebay_card_id(card):
    return ''.join(card)

def main():
    # create driver instance 
    driver = create_webdriver_instance()
    driver.get(driver.base_url)
    driver.maximize_window()

    # enter search term 
    search_term = "galaxy s8"
    search_criteria(driver, search_term)
    sleep(2)

    # enter parameters possibly in search_criteria?

    # get cards
    cards_found = get_cards(driver)

    # get all cards title and price
    get_card_info(driver, cards_found)
    sleep(5)

    driver.quit()
    
if __name__ == '__main__':
    main()

