from selenium import webdriver
import csv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Формируюем главную ссылку(вводим товар и город)
chrome_options = Options()


city = 'krasnodar'  # город
product = 'стиральныя машина'   # продукт
page = 1

main_link = f'https://{city}.rbt.ru/search/?search_provider=anyquery&page={page}&strategy=vectors_extended,zero_queries&q={product}&utm_referrer='

chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome('./chromedriver', options=chrome_options)
driver.get(main_link)

# кол-во страниц
last_page = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'paginator-pages__numbers')]/a/span"))
)
last_page = int(last_page[-1].text)
all_data = []


try:
    for pg in range(2, last_page+1):

        # блоки с сылками на продукты, но их нужно вытащить
        not_links_of_products = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'item-catalogue catalogue-list-item')]//div[@class='item-catalogue__item-name']/a"))
        )
        links_of_products = []

        # вытаскиваю ссылки на продукты
        for link in not_links_of_products:
            links_of_products.append(link.get_attribute('href'))

        product_data = []


        for link in links_of_products:
            driver.get(link)
            item_data = {}

            # Название продукта
            name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.page-item__title-h1.text'))
            )
            item_data['name'] = name.text

            # Артикул
            articul = driver.find_element_by_xpath("//div[contains(@class, 'page-item__articul')]").text
            articul = int(articul.split(' ')[1])
            item_data['articul'] = articul

            # Бренд и категория товара
            brend_product = driver.find_element_by_xpath("//div[@class='breadcrumbs page-item__breadcrumbs']/div[4]").text
            category_product = driver.find_element_by_xpath("//div[@class='breadcrumbs page-item__breadcrumbs']/div[3]").text
            item_data['category_product'] = category_product
            item_data['brend_product'] =brend_product

            # Ссылка на инсрукцию
            try:
                instruction_url = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='link item-support__file_type_pdf link_underline_disabled link_size_16 item-support__file']|//span[@class='flix-std-docs-title flix-docs-span flix-d-h3']/a"))
            )
                item_data['instruction'] = instruction_url.get_attribute('href')
            except:
                item_data['instruction'] = None

            # Достаем фотки
            # Выбираю целый блок фоток, т.к на странице присутсвует несколько
            # Мне нужен первый блок с фотками
            block_photos = driver.find_elements_by_xpath("//li[contains(@class, 'carousel__item')]/a")


            photo_links = []

            # достаю линки фотографий
            for photo_link in block_photos:
                photo_links.append(photo_link.get_attribute('data-img-big')[2:])

            item_data['photos'] = photo_links

            # Характеристики
            # Получаю ссылку на страницу с характеристиками
            # "//a[contains(@class, 'item-content__tabs_tab-characteristics')]"
            try:
                link_to_ch = driver.find_element_by_xpath("//a[contains(@class, 'item-content__tabs_tab-characteristics')]")
                link_to_ch = link_to_ch.get_attribute('href')
                driver.get(link_to_ch)

                char = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@class='item-characteristics__groups-el ']"))
                )


                ch = []
                for elm in char:
                    ch.append(elm.text.split('\n'))

                keys = []
                var = []
                chars = {}
                for el in ch:
                    for l in el:
                        if el.index(l) % 2 == 0 or el.index(l) == 0:
                            keys.append(l)
                        else:
                            var.append(l)



                chars = {k: v for k, v in zip(keys, var)}
                item_data['chars'] = chars
            except:
                item_data['chars'] = None
            all_data.append(item_data)
        page = pg
        driver.get(f'https://{city}.rbt.ru/search/?search_provider=anyquery&page={page}&strategy=vectors_extended,zero_queries&q={product}&utm_referrer=')
except:
    print(f'Произошла ошибка. Сделал - {len(all_data)}')

print(f'Успешно завершено. Выполнил - {len(all_data)}')
with open('hwdb', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for item in all_data:
       csv_writer.writerow([item])
