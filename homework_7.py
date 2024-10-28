from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from lxml import html
import requests
import time
import csv


options = Options()
options.add_argument('start-maximized')  # Опция, которая открывает окно на весь экран

driver = webdriver.Chrome(options=options)  # Создаем объект webdriver
driver.get('https://matchtv.ru/')  # Переходим на главную страницу

button = driver.find_element(By.XPATH, "//a[@href='/hockey']")  # Находим элемент на странице
button.click()  # Кликаем и переходим в раздел "Хоккей"
time.sleep(2)
button = driver.find_element(By.XPATH, "//a[@href='/hockey/khl?utm_source=ex&utm_medium=themes&utm_campaign=hockey']")
button.click()  # Кликаем и переходим в раздел "Чемпионат КХЛ"
time.sleep(2)
button = driver.find_element(By.XPATH, "//a[@href='/news/hockey/khl']")
button.click()  # Кликаем и переходим в раздел "Новости"

# Создаем бесконечный цикл и скроллим страницу до конца. Если новых элементов больше нет, выходим их цикла
while True:
    wait = WebDriverWait(driver, 30)
    news = wait.until(ec.presence_of_all_elements_located((By.XPATH, "//a[@class='node-news-list__item']")))
    count = len(news)
    driver.execute_script("window.scrollBy(0, 5000)")
    time.sleep(1)
    news = driver.find_elements(By.XPATH, "//a[@class='node-news-list__item']")

    if len(news) == count:
        break

news_links = []

for one_news in news:
    news_links.append(one_news.get_attribute('href'))  # Записываем ссылки в список

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'}

data = []

# Проходим по каждой ссылке в списке и парсим содержимое страницы. Записываем в список data
for link in news_links:
    time.sleep(1)
    response = requests.get(link, headers=header)
    dom = html.fromstring(response.text)

    if dom.xpath("//div[@itemprop= 'name']/text()"):
        author = dom.xpath("//div[@itemprop= 'name']/text()")[0].strip()
    else:
        author = 'Автор не известен'

    date_time = dom.xpath("//div[@class= 'WidgetArticle__time--3-hwC']/text()")[0]
    if len(date_time) < 6:
        date_time = f'Сегодня в {date_time}'

    title = dom.xpath("//h1/text()")[0]
    url = link

    data.append([date_time, author, title, url])

# Сохраняем данные в CSV-файл
with open('hockey_news.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date_Time', 'Author', 'Title', 'URL'])
    writer.writerows(data)
