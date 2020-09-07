from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
from data import User


# авторизация на сайте
def do_login():
    # вводим в форму логин
    login = driver.find_element_by_id('fm-login-id')
    login.send_keys(User.login)
    # вводим пароль
    password = driver.find_element_by_id('fm-login-password')
    password.send_keys(User.password)
    # нажимаем кнопку "войти"
    btn_login = driver.find_element_by_class_name('fm-button')
    btn_login.click()
    time.sleep(3)


# получение списока заказов
def do_find_orders():
    # переходим во вкладку "мои заказы"
    driver.get('https://trade.aliexpress.ru/orderList.htm')

    # переход во вкладку "заказ отправлен"
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "remiandTips_waitBuyerAcceptGoods"))).click()

    # списки идут по 10 заказов, необходимо отобразить все
    select_page_size = Select(WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "full-pager-page-size"))))
    index_page_size = len(select_page_size.options)-1
    select_page_size.select_by_index(index_page_size)

    # возврат список заказов
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, "order-item-wraper")))


# вывод информации по заказам
def print_info(orders_wrapper):
    # количество заказов
    num_orders = len(orders_wrapper)
    for i in range(num_orders):
        driver.switch_to.window(window_ali_main)
        # наименование товаров в заказе
        orders_name = orders_wrapper[i].find_elements_by_class_name('product-title')
        # ссылка на данные товара
        link_order_info = orders_wrapper[i].find_element_by_class_name('view-detail-link').get_attribute("href")
        # информация по поддержке заказа
        order_support = orders_wrapper[i].find_element_by_class_name('left-sendgoods-day').text

        print("%s заказ:" % (i + 1))
        for order_name in orders_name:
            print(order_name.text)

        # перевод из дней в точную дату
        date = get_date(order_support)
        print(date)

        # получение номера отслеживания
        # print(link_order_info)
        tracking_num = get_tracking_num(link_order_info)
        print('Номер отслеживания: ' + tracking_num)
        print('-------------')


# получение даты завершения поддержки заказа
def get_date(support):
    day = support.split(': ')[1][:5]
    if day[-2:] == 'дн':
        date = 'Закрытие заказа: ' + (datetime.today() + timedelta(days=int(day[:2]))).strftime("%d/%m/%Y")
    else:
        date = support
    return date


# получение номера отслеживания заказа
def get_tracking_num(link):
    driver.execute_script("window.open('%s', 'new window')" % link)
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)
    tracking_num = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, "logistics-num")))[-1].text
    driver.close()
    return tracking_num


# получает информацию по всем активным заказам
def info_my_active_orders():
    orders = do_find_orders()
    print_info(orders)


# подсчет общей потраченной суммы
# to do
# учет был ли в итоге оплачен товар!!!!!
def cost_of_all_orders():
    driver.get('https://trade.aliexpress.ru/orderList.htm')
    # изменение кол-ва отоброжаемого товара на 30
    select_page_size = Select(WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "full-pager-page-size"))))
    index_page_size = len(select_page_size.options) - 1
    select_page_size.select_by_index(index_page_size)
    time.sleep(20)
    # поиск количетсва страниц с товаром
    total_pages = int(driver.find_elements_by_class_name('ui-goto-page')[-2].text)
    print('total pages: %d' % total_pages)
    total_price_ru = 0
    total_price_d = 0
    # цикл обхода страниц с товаром
    i = 1
    while i <= total_pages:
        print('current page: %d' % i)
        # выбор цен на товары
        prices = WebDriverWait(driver, 20).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "amount-num")))

        for price in prices:
            # если цена в долларах
            if '$' in price.text:
                p = float(price.text[2:].replace(' ', '').replace(',', '.'))
                total_price_d += p
            # если цена в рублях
            else:
                p = float(price.text[:-5].replace(' ', '').replace(',', '.'))
                total_price_ru += p
            # print(p)
            time.sleep(1)
        # кнопка перехода на следующую страницу
        # по каким-то причинам работает нестабильно
        # btn_next = driver.find_elements_by_class_name('ui-pagination-next.ui-goto-page')
        # поэтому переход осуществляктся через ввод нужного листа
        input_page = driver.find_element_by_id('gotoPageNum')
        i += 1
        input_page.send_keys(i)

        # на последней странице ничего не делаем
        if i <= total_pages:
            # btn_next[-1].click()
            driver.find_element_by_id('btnGotoPageNum').click()
            time.sleep(10)

    # вывод полученной информации
    print()
    print('%d рублей' % total_price_ru)
    print('%d долларов' % total_price_d)


if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.get('http://login.aliexpress.ru/')
    # инициализация первой вкладки
    window_ali_main = driver.window_handles[0]

    #  авторизация на сайте
    do_login()
    # информация по активным заказам
    # info_my_active_orders()
    time.sleep(2)

    # после закрытия вкладок необходим переход на первую
    driver.switch_to.window(window_ali_main)
    # подсчет потраченной суммы за все время
    cost_of_all_orders()

    # завершение программы
    time.sleep(10)
    driver.close()
