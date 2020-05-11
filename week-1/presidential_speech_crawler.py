from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import bs4
import time


BASE_URL = "https://millercenter.org"


def scroll_page(browser):
    """Automatically control to scroll the webpage to the bottom."""
    SCROLL_PAUSE_TIME = 2

    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = browser.execute_script(
            "return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return None


def get_speech_urls(browser, init_url):
    """Retrive url links for every presidential speech."""
    browser.get(init_url)
    time.sleep(3)
    scroll_page(browser)
    soup = bs4.BeautifulSoup(browser.page_source, features="lxml")

    speeches = soup.find_all(class_="field-content")

    speech_urls = []
    for index, speech in enumerate(speeches):
        if not index % 2:
            rel_url = speech.find("a").get("href")
            abs_url = BASE_URL + rel_url
            speech_urls.append(abs_url)

    return speech_urls


def speech_crawler(browser, url):
    """Construct dataframe for each presidential speech."""
    speech_info = {}
    browser.get(url)

    time.sleep(3)

    try:
        view_action = ActionChains(browser)
        view_button = browser.find_element_by_class_name(
            "transcript-btn-inner")
        view_action.click(view_button).perform()
        time.sleep(2)
        view_soup = bs4.BeautifulSoup(browser.page_source, features="lxml")

        title = view_soup.find(
            class_="presidential-speeches--title").get_text()

        about = view_soup.find(class_="about-this-episode")
        try:
            name = about.find(class_="president-name").get_text()
        except Exception:
            name = None
        try:
            date = about.find(class_="episode-date").get_text()
        except Exception:
            date = None
        try:
            source = about.find(class_="speech-loc").get_text()
        except Exception:
            source = None

        script = view_soup.find(class_="transcript-inner").get_text()

    except NoSuchElementException:
        view_soup = bs4.BeautifulSoup(browser.page_source, features="lxml")

        title = view_soup.find(
            class_="presidential-speeches--title").get_text()

        about = view_soup.find(class_="about-this-episode")
        try:
            name = about.find(class_="president-name").get_text()
        except Exception:
            name = None
        try:
            date = about.find(class_="episode-date").get_text()
        except Exception:
            date = None
        try:
            source = about.find(class_="speech-loc").get_text()
        except Exception:
            source = None

        script = view_soup.find(class_="view-transcript").get_text()

    speech_info = {
        "link": browser.current_url,
        "title": title,
        "date": date,
        "name": name,
        "source": source,
        "script": script
    }
    speech_df = pd.DataFrame([speech_info])

    return speech_df


def main():
    """Run the web crawling process."""
    result_df = pd.DataFrame(
        columns=["link", "title", "date", "name", "source", "script"])

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    browser = webdriver.Chrome()

    init_url = "https://millercenter.org/the-presidency/presidential-speeches"
    links = get_speech_urls(browser, init_url)

    for link in links:
        speech_df = speech_crawler(browser, link)
        result_df = result_df.append(speech_df, ignore_index=True)
    browser.close()

    # Save the resulting dataframe into a csv file
    result_df.to_csv("presidential_speech.csv", header=True)

    return None

if __name__ == '__main__':
    main()
