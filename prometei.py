import sys
import time
import random
import re
import excelparsing
import test_solving
import prog_logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import NoSuchElementException

username = "79833207865"  # "Mikhailov_DA"  # Имя юзера (впоследствии получаемое через бота)
password = "0Jh#8GPT"  # "Bb-pGE58"  # Пароль юзера (впоследствии получаемый через бота)
d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}
files_path = "C:/Prometei/"  # путь к папке со всеми файлами (драйвер хрома, база данных и т.п.)
options = Options()
options.add_argument('--log-level=3')
driver = webdriver.Chrome(
    files_path + "chromedriver.exe", options=options)  # Это нужно чтобы можно было выгружать логи с браузера
# (первоначально для Promitei)

# _find_courses_link = "https://hiprof.irkutskoil.ru/mira/#&step=6&measureStageStatus=NOT_FINISHED&s=" \
#                      "Q3dQ3j2436tctmcfnJys&doaction=MyMeasureStatisticsAllPeriodNotFinished&id=&type=" \
#                      "mymeasurestatisticslist&measurePeriod=ALL_PERIOD"
_find_courses_link = 'https://hiprof.irkutskoil.ru/mira/#&stype=sb&sb=1&step=8&id=0&type=mymeasurestatisticslist&' \
                       'name=%D0%A1%D1%82%D0%B0%D1%82%D0%B8%D1%81%D1%82%D0%B8%D0%BA%D0%B0+' \
                     '%D0%BC%D0%BE%D0%B5%D0%B3%D0%BE+%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D1%8F'  # тестовая ссы
_auth_link = "https://hiprof.irkutskoil.ru/mira/Do?doaction=Go&s=YwSqVdexvj7jQdJp9sEs&id=0&type=customloginpage"
driver.maximize_window()


def login():
    global username
    global password
    username = input('Введи имя работяги: ')  # username
    password = input('Введи пароль работяги: ')  # password


# ищем поля для ввода логина и пароля и логинимся
def auth():
    driver.get(_auth_link)
    user_login_mask = "//input[@class='mira-widget-login-input mira-default-login-page-text-input' and @type='text']"
    user_password_mask = "//input[@class='mira-widget-login-input mira-default-login-page-text-input' and " \
                         "@type='password'] "
    user_login = driver.find_element(By.XPATH, user_login_mask)
    user_login.send_keys(username)
    user_password = driver.find_element(By.XPATH, user_password_mask)
    user_password.send_keys(password)
    user_password.submit()  # Подтверждение ввода логина/пароля

    # обработка исключения, когда неверный пароль или логин (костыль пздц)
    err_message = "Не удалось зарегестрироваться в HIPROF. Введи данные вручную мешок с костями. " \
                  "После этого для продолжения нажми Enter. Если хочешь выйти из прожки введи 'x'"
    while UnexpectedAlertPresentException != 0:
        try:
            driver.switch_to.alert.accept()
            driver.get(_auth_link)
            user_password = driver.find_element(By.XPATH, user_password_mask)
            wait_for_user(err_message)
            user_password.submit()
        except Exception:
            break


# применяем фильтры для поиска названий курсов и кнопки "Запустить"
def find_courses():
    courses_list_mask = '//*[@class="mira-grid-cell-action"]'
    courses_path_mask = '//*[@class="mira-grid-cell-operation border-box  primary  "]'
    driver.switch_to.window(driver.window_handles[0])  # переключаемся на основное окно браузера
    courses_list_text = []
    courses_url = []
    try:
        wait_element_load(courses_list_mask)  # Ждём пока загрузятся курсы
    except TimeoutException:
        print('[INFO] На странице незаврешенные курсы не найдены')
        sys.exit(0)
    try:
        courses_list = driver.find_elements(By.XPATH, courses_list_mask)
        courses_path = driver.find_elements(By.XPATH, courses_path_mask)
        amount_of_course = len(courses_path)
        if not courses_list:
            print('[INFO] Назначенных курсов нет')
            return
        for each_list in courses_list:
            courses_list_text.append(each_list.text)
        for each_path in range(amount_of_course):
            driver.find_elements(By.XPATH, courses_path_mask)[each_path].click()
            driver.implicitly_wait(10)  # ждем пока загрузится новая страница
            courses_url.append(driver.current_url)
            driver.get(_find_courses_link)  # Поиск курсов для сдачи
            driver.implicitly_wait(10)  # ждем пока загрузится новая страница
        return courses_url, courses_list_text
    except Exception:
        print('[INFO] Не удалось найти назначенные курсы и перейти к ним')
    print('_________________________________________________________________________________________')


# запускаем окно с тестом, если это возможно
def find_test_page(course_url, course_name):
    # run_test_button_mask = ['//*[@class="tree-node tree-node-type-testcontentsection"]//ancestor::td[1]//ancestor
    # ::tr[1]//*[@class="button launchaction mira-button-primary mira-button"]',
    # '//*[@class="mira-horizontal-layout-wrapper clearfix"]//*[@class="button mira-button-primary mira-button"]']  #
    run_test_button_mask = ['//*[@class="button launchaction mira-button-primary mira-button"]',
                            '//*[@class="mira-horizontal-layout-wrapper clearfix"]//*'
                            '[@class="button mira-button-primary mira-button"]']  #
    # маска для кнопок запуск не ПРВТ и ПРВТ теста соответственно (также кнопки для прочтения теории)
    driver.switch_to.window(driver.window_handles[0])
    driver.get(course_url)  # Переход на страницу с выбранным тестом
    driver.get(course_url)  # Сука тупорылый сайт не переходит по url с первого раза
    no_test_button_counter = 0  # Счетчик не найденных кнопок с запуском теста
    try:
        for each_button in run_test_button_mask:
            try:
                if wait_element_load(each_button):
                    run_all_elements = driver.find_elements(By.XPATH, each_button)  # Ищем кнопки с запуском теста
                    for each_element in range(0, len(run_all_elements) - 1):  # кликаем по всем, кроме запуска теста
                        run_all_elements[each_element].click()
                    WebDriverWait(driver, 10).until(ec.number_of_windows_to_be(len(run_all_elements)))  # ждем пока
                    # откроются все окна с теорией
                    while len(driver.window_handles) > 1:  # закрываем все открытые окна, кроме основного
                        driver.switch_to.window(driver.window_handles[1])
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    wait_element_load(each_button)
                    driver.find_elements(By.XPATH, each_button)[-1].click()
                    break
                else:
                    no_test_button_counter += 1
                if no_test_button_counter == len(run_test_button_mask):  # если нет кнопок с запуском тогда off
                    print('[INFO] <{0}> Не нашел кнопку запуска тестирования'.format(course_name))
                    return 0
            except TimeoutException:
                continue
    except Exception:
        print('[INFO] <{0}> Произошла ошибка при переходе на страницу с тестом'.format(course_name))
        return 0
    WebDriverWait(driver, 10).until(ec.number_of_windows_to_be(2))  # ждем появления окна с тестом и главного окна
    driver.switch_to.window(driver.window_handles[1])
    if wait_element_load('//*[@id="btnOk"]', 10):  # проверяем вылезло ли окно с подтверждением начать тест и согл
        driver.find_element(By.XPATH, '//*[@id="btnOk"]').click()
    return 1


# парсим текст с вопросом
def get_question():
    question_mask = '//*[@class="question-text"]'
    question_id_mask = '//*[@class="question-text"]//ancestor::div[3]'
    wait_element_load(question_mask)
    question_element = driver.find_elements(By.XPATH, question_mask)
    question_id_element = driver.find_elements(By.XPATH, question_id_mask)
    question_id_list = []
    for each in question_id_element:
        question_id = each.get_attribute('data-quiz-uid')  # находим id вопроса
        if question_id:  # если результат не нулевой то добавляем в массив с id вопроса
            question_id_list.append(question_id)
    return question_element, question_id_list


# загружаем в массив ответы на странице для указанного вопроса
def get_answer(question_id):
    answer_mask = "//*[@data-quiz-uid='" + question_id + "']//div//table//tbody//tr//td//div"
    answer_element = driver.find_elements(By.XPATH, answer_mask)
    current_answers_list = []
    for each in answer_element:  # парсим текст из элементов (т.к. find_elements может извлекать только элементы)
        current_answers_list.append(each.text)
    return current_answers_list


# ищем ссылки на ответы и кладем в массив (для того чтобы по правильным ответам потом кликнуть)
def get_answer_link(question_id):
    answer_link_mask = "//*[@data-quiz-uid='" + question_id + "']//div//table//tbody//tr//td//div//span"
    answer_link_element = driver.find_elements(By.XPATH, answer_link_mask)
    current_answers_link_list = []  # список ответов на текущий вопрос
    for each in answer_link_element:
        current_answers_link_list.append(each)
    return current_answers_link_list


# функция для определения был ли кликнут ответ
def get_answer_checkbox(question_id):
    answer_checkbox_mask = "//*[@data-quiz-uid='" + question_id + "']//tbody//*[@class[contains(.,'check-control')]]"
    answer_checkbox_element = driver.find_elements(By.XPATH, answer_checkbox_mask)
    current_answer_checkbox_list = []  # список 1 (чекбокс кликнут) и 0 (чекбокс НЕ кликнут)
    for each in answer_checkbox_element:
        checkbox = each.get_attribute('class')
        if checkbox == 'check-control checked' or checkbox == 'check-control  checked':
            current_answer_checkbox_list.append(1)
        else:
            current_answer_checkbox_list.append(0)
    return current_answer_checkbox_list


# положить все вопросы, ответы, линки в один трехмерный массив
def get_weblist_array():
    question_element, question_id_list = get_question()
    weblist_array = []
    questions_list = []
    all_question_list = []  # массив с одним массивом, чтобы было проще проходиться по элементам в цикле
    all_answer_list = []
    all_answer_link_list = []
    all_answer_checkbox_list = []
    for each in question_element:
        questions_list.append(each.text)
    for each in question_id_list:
        all_answer_list.append(get_answer(each))
        all_answer_link_list.append(get_answer_link(each))
        all_answer_checkbox_list.append(get_answer_checkbox(each))
    all_question_list.append(questions_list)
    weblist_array.append(all_question_list)
    weblist_array.append(all_answer_list)
    weblist_array.append(all_answer_link_list)
    weblist_array.append(question_id_list)
    weblist_array.append(all_answer_checkbox_list)
    return weblist_array


# кликаем по правильным ответам в тесте
def right_answer_click():  # собираем массив с ссылками на правильные ответы и кликаем по ним
    weblist_array = get_weblist_array()
    database_array = excelparsing.get_array_from_database()  # получаем массив с данными из базы Excel
    answer_link_click, founded_questions_id, founded_database_question, founded_database_answer, unidentified_question \
        = test_solving.find_answer_to_click(weblist_array, database_array)
    # получаем массив ссылок на которые нужно кликать и строковую переменную 'wait'
    # если нужно подождать ввод юзера и сообщение об ошибке
    driver.maximize_window()
    for num, each in enumerate(answer_link_click):
        try:
            wait_element_load('//*//div//table//tbody//tr//td//div//span')
            founded_questions_mask = "//*[@data-quiz-uid='" + founded_questions_id[num] + "']"
            question_select = driver.find_element(By.XPATH, founded_questions_mask)
            driver.execute_script("arguments[0].scrollIntoView();", question_select)  # прокрутка
            # тобы можно было кликнуть
            WebDriverWait(driver, 10).until(ec.visibility_of(each))  # ждем чтобы элемент был виден и кликаем по нему
            each.click()
        except Exception:
            print('[INFO] Произошла проблема при прокликивании вариантов ответа')
    # логгируем всякую еботню для братка
    weblist_array = get_weblist_array()  # обновляем данные с сайта (в частности для проверки checkbox)
    prog_logging.get_logs(weblist_array, founded_database_question, founded_database_answer, unidentified_question)
    # считаем кол-во не отвеченных вопросов
    wrong_answer_list = []
    for num_question, each_question in enumerate(weblist_array[4]):
        if not sum(each_question):
            wrong_answer_list.append(num_question + 1)
    print("\nОстались не отвечеными {0} вопросов из {1}. Это вопросы №{2}".format(
        len(wrong_answer_list), len(weblist_array[4]), wrong_answer_list))
    if wrong_answer_list:  # если есть не кликнутые ответы то ждем указаний юзера
        wait_for_user(
            '[ALARM] OMG!!!Прога кликнула не все варианты! Выбери ответ и нажми Enter чтобы продолжить, "x" для выхода')
    random_delay_timer(len(weblist_array[0][0]))


# кликаем неверные ответы если требуется
def wrong_answer_click():
    pass


# ищем и кликаем по кнопке "Ответить" и ищем следуйщий раздел и переходим на него
def end_test_click(course_name):
    answer_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                         'check_button quiz_models_components_button_check_button")]]'  # кнопка Ответить
    endtest_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                          'next_button quiz_models_components_button_next_button")]]'  # кнопка Завершить тестирование
    section_mask = '//div[@class="section-title-area"]//div[@class="before-title"]'  # маска для определения № раздела
    driver.switch_to.window(driver.window_handles[1])
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="Content"]'))  # Пидорги засунули
    # весь контент в айфрейм, поэтому переключаемся на него сделай еще проверку на отрытие окна с
    # подтверждением сдачи и нажатием там кнопки ОК
    button_element = driver.find_element(By.XPATH, answer_button_mask)
    try:
        section_text = str(driver.find_element(By.XPATH, section_mask).text)
        section_amount = int(re.findall(r'\d+', section_text)[1]) - int(re.findall(r'\d+', section_text)[0])  # выясняем
        # количество  оставшихся разделов по фильтру
        for each in range(section_amount):
            driver.switch_to.window(driver.window_handles[1])
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="Content"]'))
            right_answer_click()
            wait_for_user(
                '*** Доверяешь ли ты проге мешок с костями? Нажми Enter чтобы продолжить, "x" для выхода ***')
            button_element.click()
    except NoSuchElementException:
        print('[INFO] <{0}> В данном тесте только один раздел'.format(course_name))
        driver.switch_to.window(driver.window_handles[1])
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="Content"]'))
        right_answer_click()
        wait_for_user(
            '*** Доверяешь ли ты проге мешок с костями? Нажми Enter чтобы продолжить, "x" для выхода ***')
        button_element.click()
    wait_element_load('//*[contains(.,"Тестирование завершено")]')
    driver.find_element(By.XPATH, endtest_button_mask).click()
    driver.close()
    print('[INFO] <{0}> Назначенный тест сдан'.format(course_name))


# задержка для того чтобы загрузились скрипты, ajax и прочее гавно
def wait_element_load(_courses_list_filter, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(ec.presence_of_element_located((By.XPATH, _courses_list_filter)))
        return 1
    except TimeoutException:
        return 0


def wait_window_load():
    pass


# рандомная задержка с отображением оставшегося времени
def random_delay_timer(timer_multiply=1):
    delay = random.randint(59, 119) * timer_multiply
    for remaining in range(delay, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} секунд осталось из {:2d} секунд.".format(remaining, delay))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rТаймер кончил за {:2d} секунд!            \n".format(delay))


# ожидание ввода пользователя
def wait_for_user(err_message):
    print(err_message)
    accept = input()
    if accept == 'x':
        sys.exit()
    else:
        return 1


# запуск лайт скрипта (только прокликивание правильных ответов, юзер сам открывает страницу с вопросами)
def start_light_script():
    login()
    auth()
    solving_repeat = 1
    wait_for_user('Открой окно с тестом. Для продолжения нажми нажми Enter, для выхода "x"')
    while solving_repeat == 1:
        WebDriverWait(driver, 30).until(ec.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[1])
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="Content"]'))
        right_answer_click()
        solving_repeat = wait_for_user(
            'Для перехода к следующим вопросам, открой окно с тестом и нажми Enter, для выхода "x"')


# запускаем скрипта с полным автоматическим решением теста (включая поиск тем и переключение по темам)
def start_script():
    login()
    auth()
    driver.get(_find_courses_link)  # Поиск курсов для сдачи
    courses_url, courses_list_text = find_courses()  # Найти курсы
    print('---Всего назначенных курсов---')
    print(*courses_list_text, sep='\n')
    course_number = 0  # Номер курса
    for each_url in courses_url:
        if find_test_page(each_url, courses_list_text[course_number]):  # передаем путь до конкретного теста. Если не
            # находит кнопки запуска теста то переходит к следующему
            try:
                end_test_click(courses_list_text[course_number])
            except StaleElementReferenceException:
                print("Не везде кликнул лох")
            except NoSuchWindowException:
                print('[INFO] Не удалось перейти на страницу со всеми тестами')
        course_number += 1
    sys.exit()


def main():
    start_script()
    # start_light_script()


if __name__ == '__main__':
    main()
