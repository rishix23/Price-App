import csv
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common import exceptions
import datetime
import pandas as pd

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tweets(db.Model):
    __tablename__ = 'Tweets'
    id = db.Column(db.Integer, primary_key=True)
    User = db.Column(db.String(1000))
    Handle = db.Column(db.String(1000))
    TweetText = db.Column(db.String(1000))
    ReplyCount = db.Column(db.Integer())
    RetweetCount = db.Column(db.Integer())
    LikeCount = db.Column(db.Integer())

    def __init__(self, User, Handle, TweetText, ReplyCount, RetweetCount, LikeCount):
        self.User = User
        self.Handle = Handle
        self.TweetText = TweetText
        self.ReplyCount = ReplyCount
        self.RetweetCount = RetweetCount
        self.LikeCount = LikeCount

# def clearDatabase():
#     try:
#         number_rows_deleted = db.session.query(Tweets).delete()
#         print(number_rows_deleted)
#         db.session.commit()
#     except:
#         db.session.rollback()

def create_webdriver_instance():
    # driver = webdriver.Chrome(executable_path=os.popen('which chromedriver').read().strip())
    #webdriver.ChromeOptions.add_argument
    print("starting twitter scrap")
    #Initialization method. 
    driver = webdriver.Chrome(executable_path=os.popen('which chromedriver').read().strip())
    driver.chrome_options = webdriver.ChromeOptions()
    # driver.base_url = 'https://twitter.com/search?q='
    return driver

def find_search_input_and_enter_criteria(search_term, driver):
    xpath_search = '//input[@aria-label="Search query"]'
    search_input = driver.find_element_by_xpath(xpath_search)
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    return True


# def changeTab(tab_name, driver):
#     """Options for this program are `Latest` and `Top`"""
#     sleep(0.5)
#     tab = driver.find_element_by_link_text(tab_name)
#     tab.click()
#     xpath_tab_state = f'//a[contains(text(),\"{tab_name}\") and @aria-selected=\"true\"]'


def generate_tweet_id(tweet):
    return ''.join(tweet)


# def scroll_down_page(driver, last_position, num_seconds_to_load=1, scroll_attempt=0, max_attempts=5):
#     """The function will try to scroll down the page and will check the current
#     and last positions as an indicator. If the current and last positions are the same after `max_attempts`
#     the assumption is that the end of the scroll region has been reached and the `end_of_scroll_region`
#     flag will be returned as `True`"""
#     end_of_scroll_region = False
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     sleep(num_seconds_to_load)
#     curr_position = driver.execute_script("return window.pageYOffset;")
#     if curr_position == last_position:
#         if scroll_attempt < max_attempts:
#             end_of_scroll_region = True
#         else:
#             scroll_down_page(last_position, curr_position, scroll_attempt + 1)
#     last_position = curr_position
#     return last_position, end_of_scroll_region


# def save_tweet_data_to_csv(records, filepath, mode='a+'):
#     # header = ['User', 'Handle', 'TweetText', 'ReplyCount', 'RetweetCount', 'LikeCount']
#     # with open(filepath, mode=mode, newline='', encoding='utf-8') as f:
#     #     writer = csv.writer(f)
#     #     if mode == 'w':
#     #         writer.writerow(header)
#     #     if records:
#     #         writer.writerow(records)

def saveTweetInDatabase(tweet):
    if tweet is None:
        print("empty")
    else:
        user = tweet[0]
        handle = tweet[1]
        tweetText = tweet[2]

        #extract correct interger value for replies, retweets, and likes
        replyCount = 0
        retweetCount = 0
        LikeCount = 0

        data = Tweets(user, handle, tweetText, replyCount, retweetCount, LikeCount)
        db.session.add(data)
        db.session.commit()

def collect_all_tweets_from_current_view(driver, lookback_limit=30):
    """The page is continously loaded, so as you scroll down the number of tweets returned by this function will
     continue to grow. To limit the risk of 're-processing' the same tweet over and over again, you can set the
     `lookback_limit` to only process the last `x` number of tweets extracted from the page in each iteration.
     You may need to play around with this number to get something that works for you. I've set the default
     based on my computer settings and internet speed, etc..."""
    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]


def extract_data_from_current_tweet_card(card):
    try:
        user = card.find_element_by_xpath('.//span').text
    except exceptions.NoSuchElementException:
        user = ""
    except exceptions.StaleElementReferenceException:
        return
    try:
        handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except exceptions.NoSuchElementException:
        handle = ""
    # try:
    #     """
    #     If there is no post date here, there it is usually sponsored content, or some
    #     other form of content where post dates do not apply. You can set a default value
    #     for the postdate on Exception if you which to keep this record. By default I am
    #     excluding these.
    #     """
    #     postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    # except exceptions.NoSuchElementException:
    #     return
    try:
        _comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        _comment = ""
    try:
        _responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except exceptions.NoSuchElementException:
        _responding = ""
    tweet_text = _comment + _responding
    try:
        reply_count = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
    except exceptions.NoSuchElementException:
        reply_count = ""
    try:
        retweet_count = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    except exceptions.NoSuchElementException:
        retweet_count = ""
    try:
        like_count = card.find_element_by_xpath('.//div[@data-testid="like"]').text
    except exceptions.NoSuchElementException:
        like_count = ""

    tweet = (user, handle, tweet_text, reply_count, retweet_count, like_count)
    return tweet

def extractTweetsFromDatabase():
    #df = pd.read_csv('tweetsFound.csv')
    #tweetList = list(df.TweetText)

    tweetList = []
    tweets = Tweets.query.all()
    for tweet in tweets:
        tweetList.append(tweet.TweetText)

    return tweetList

def main(username, password, search_term, filepath, tweetLimit, tab):
    #save_tweet_data_to_csv(None, filepath, 'w')  # create file for saving records
    last_position = None
    end_of_scroll_region = False
    unique_tweets = set()
    RequestedTweetLimit = tweetLimit
    driver = create_webdriver_instance()

    tweetReachedflag = False

    print(datetime.datetime.now())

    if tab == "Top":
        url = 'https://twitter.com/search?lang=en&q=' + search_term
    else:
        url = 'https://twitter.com/search?lang=en&q=' + search_term + "&f=live"

    driver.get(url)
    sleep(3)
    driver.maximize_window()

    sleep(2)

    # logged_in = login_to_twitter(username, password, driver)
    # if not logged_in:
    #     return

    #search_found = find_search_input_and_enter_criteria(search_term, driver)

    # if not search_found:
    #     return

    # changeTab(tab, driver)

    last_height = driver.execute_script("return document.body.scrollHeight")

    # while not end_of_scroll_region:
    while len(unique_tweets) <= RequestedTweetLimit:
        print(len(unique_tweets))   
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        # Wait to load page
        sleep(3)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        # break condition
        if new_height == last_height:
            if tweetReachedflag == False:
                print("new height = last height")
                driver.execute_script("window.scrollBy(0, -500)")
                new_height = driver.execute_script("window.scrollBy(0, -250)")
                driver.execute_script("window.scrollTo(0, 50)")
                #driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            else:
                break
        last_height = new_height
        #driver.execute_script("window.scrollBy(0, -100)";

        cards = collect_all_tweets_from_current_view(driver)
        for card in cards:
            try:
                tweet = extract_data_from_current_tweet_card(card)
            except exceptions.StaleElementReferenceException:
                continue
            if not tweet:
                continue
            tweet_id = generate_tweet_id(tweet)
            if tweet_id not in unique_tweets:
                unique_tweets.add(tweet_id)
                #save_tweet_data_to_csv(tweet, filepath)
                saveTweetInDatabase(tweet)
        #last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
    print(len(unique_tweets))
    tweetReachedflag = True
    driver.quit()
    print(datetime.datetime.now())

# if __name__ == '__main__':
#     usr = "rp00463@surrey.ac.uk"
#     pwd = "sleezy"
#     path = 'tweetsFound.csv'
#     term = 'trump'
#     tweetLimit = 1

#     main(usr, pwd, term, path, tweetLimit)
