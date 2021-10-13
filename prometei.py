import sys
import time
import random
import re
import excelparsing
import test_solving
import prog_logging
from playsound import playsound
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

username = "79833207865"#"Mikhailov_DA"#"89120067386"  # "79140020797"#  Имя юзера (впоследствии получаемое через бота)
password = "0Jh#8GPT"#"Bb-pGE58"#"&RcXu*WD"  # "%@hrDv3Q"## Пароль юзера (впоследствии получаемый через бота)&RcXu*WD
general_log = []  # итоговый лог
course_log = []  # лог по окончании теста. 1 - неизвестные вопросы, 2 - неверные вопросы, 3 - неверные ответы
d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}
files_path = "C:/Prometei/"  # путь к папке со всеми файлами (драйвер хрома, база данных и т.п.)
music_path = 'heyuser.mp3'
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
    username = input('Введи имя работяги: ')  # username#
    password = input('Введи пароль работяги: ')  # password#


# ищем поля для ввода логина и пароля и логинимся
def auth():
    driver.get(_auth_link)
    user_login_mask = "//input[@class='mira-widget-login-input mira-default-login-page-text-input' and @type='text']"
    user_password_mask = "//input[@class='mira-widget-login-input mira-default-login-page-text-input' and " \
                         "@type='password'] "
    wait_element_load(user_login_mask)
    wait_element_load(user_password_mask)
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
            wait_element_load(user_password_mask)
            user_password = driver.find_element(By.XPATH, user_password_mask)
            wait_for_user(err_message)
            user_password.submit()
            continue
        except Exception as ex:
            print('[INFO] {0} Регистрационные данные верны'.format(ex))
            break


# парсим текст с вопросом
def get_question():
    question_mask = '//*[@class="question-text"]'
    question_id_mask = '//*[@class="question-text"]//ancestor::div[3]'
    wait_element_load(question_mask)
    wait_element_load(question_id_mask)
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
    wait_element_load(answer_mask)
    answer_element = driver.find_elements(By.XPATH, answer_mask)
    current_answers_list = []
    for each in answer_element:  # парсим текст из элементов (т.к. find_elements может извлекать только элементы)
        current_answers_list.append(each.text)
    return current_answers_list


# ищем ссылки на ответы и кладем в массив (для того чтобы по правильным ответам потом кликнуть)
def get_answer_link(question_id):
    answer_link_mask = "//*[@data-quiz-uid='" + question_id + "']//div//table//tbody//tr//td//div//span"
    wait_element_load(answer_link_mask)
    answer_link_element = driver.find_elements(By.XPATH, answer_link_mask)
    current_answers_link_list = []  # список ответов на текущий вопрос
    for each in answer_link_element:
        current_answers_link_list.append(each)
    return current_answers_link_list


# функция для определения был ли кликнут ответ
def get_answer_checkbox(question_id):
    answer_checkbox_mask = "//*[@data-quiz-uid='" + question_id + "']//tbody//*[@class[contains(.,'check-control')]]"
    wait_element_load(answer_checkbox_mask)
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


# применяем фильтры для поиска названий курсов и кнопки "Запустить"
def find_courses():
    courses_list_mask = '//*[@class="mira-grid-cell-action"]'
    courses_path_mask = '//*[@class="mira-grid-cell-operation border-box  primary  "]'
    wait_window_load_and_switch(0)
    courses_list_text = []
    courses_url = []
    passing_score_list = []
    try:
        wait_element_load(courses_list_mask)
        wait_element_load(courses_path_mask)
        courses_list = driver.find_elements(By.XPATH, courses_list_mask)
        courses_path = driver.find_elements(By.XPATH, courses_path_mask)
    except Exception as ex:
        print('[INFO] Не удалось найти назначенные курсы и перейти к ним. Описатель ошибки: \n {0}'.format(ex))
        sys.exit(0)
    amount_of_course = len(courses_path)
    for each_list in courses_list:
        courses_list_text.append(each_list.text)
    for each_path in range(amount_of_course):
        driver.get(_find_courses_link)  # Поиск курсов для сдачи
        driver.get(_find_courses_link)  # Поиск курсов для сдачи
        driver.implicitly_wait(10)
        time.sleep(2)
        WebDriverWait(driver, 10).until(ec.visibility_of(driver.find_elements(
            By.XPATH, courses_path_mask)[each_path]))
        driver.find_elements(By.XPATH, courses_path_mask)[each_path].click()
        driver.implicitly_wait(10)  # ждем пока загрузится новая страница
        try:  # попробуем найти проходной балл для теста
            passing_score_list.append(check_passing_score())
        except Exception as ex:
            print('[ERR] Произошла ошибка при добавлении проходного балла для курса {0}:\n {1}'
                  .format(courses_list_text[each_path], ex))
        courses_url.append(driver.current_url)
    return courses_url, courses_list_text, passing_score_list


# функция для поиска и нажатия кнопкок запуска теории
def run_theory_on_page(course_url, course_name):
    run_theory_button_mask =\
        ['//*[@class="tree-node tree-node-type-containercontentsection"]//ancestor::tr[1]//td[7]//button',
         '//*[@class="tree-node tree-node-type-modulecontentsection"]//ancestor::tr[1]//td[7]//button',
         '//*[@class="tree-node tree-node-type-filecontentsection"]//ancestor::tr[1]//td[7]//button',
         '//*[@class="tree-node tree-node-type-resourcecontentsection"]//ancestor::tr[1]//td[7]//button']  # маски
    # для поиска теории
    exception_count = 0  # счетчик не найденных масок кнопок запуска теории
    wait_window_load_and_switch(0)
    driver.get(course_url)  # Переход на страницу с выбранным тестом
    driver.get(course_url)  # Сука тупорылый сайт не переходит по url с первого раза
    wait_window_load_and_switch(0)
    for each_mask in run_theory_button_mask:
        if wait_element_load(each_mask):
            run_all_elements = driver.find_elements(By.XPATH, each_mask)  # Ищем кнопки с запуском теории
            for each_element in range(0, len(run_all_elements)):  # кликаем по всем кнопкам запуска теории
                for i in range(10):  # делаем 10 попыток кликнуть
                    try:
                        time.sleep(2)  # пока такое гавно
                        driver.switch_to.window(driver.window_handles[0])
                        wait_element_load(each_mask)
                        driver.find_elements(By.XPATH, each_mask)[each_element].click()
                        break
                    except Exception as ex:
                        print('[ERR] {0} Не получилось кликнуть по кнопкам прочтения теории, пробую снова'.format(ex))
                        time.sleep(1)
                        continue
            WebDriverWait(driver, 10).until(ec.number_of_windows_to_be(len(run_all_elements)+1))  # ждем пока
            # откроются все окна с теорией
            time.sleep(5)  # пока такое гавно
            while len(driver.window_handles) > 1:  # закрываем все открытые окна, кроме основного
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                time.sleep(1)  # пока такое гавно
            wait_window_load_and_switch(0)
        else:
            exception_count += 1
            if exception_count == len(run_theory_button_mask):
                print('[INFO] <{0}> Не нашел кнопку для чтения теории'.format(course_name))
                general_log.append('[INFO] <{0}> Не нашел кнопку для чтения теории'.format(course_name))
            continue
    return 1


# функция для нахождения количества тестов в теме (матрёшка ЁПТ)
def find_amount_of_tests_on_page(course_url, course_name):
    run_test_button_mask = ['//*[@class="tree-node tree-node-type-testcontentsection"]//ancestor::tr[1]//td[7]',
                            '//*[@class="mira-horizontal-layout-wrapper clearfix"]//*'
                            '[@class="button mira-button-primary mira-button"]']  # маска для поиска кнопки запуска
    # не ПРВТ и ПРВТ тестирования соответственно. В итоговом тесте кнопка появлятся после прохождения преъидущих
    wait_window_load_and_switch(0)
    driver.get(course_url)  # Переход на страницу с выбранным тестом
    driver.get(course_url)  # Сука тупорылый сайт не переходит по url с первого раза
    wait_window_load_and_switch(0)
    tests_counter = 0  # Счетчик не найденных кнопок с запуском теста
    for each_button in run_test_button_mask:
        if wait_element_load(each_button):
            tests_counter += len(driver.find_elements(By.XPATH, each_button))  # ищем все тесты на странице и кол-во
            break
    print('[INFO] <{0}> В курсе всего {1} тестов'.format(course_name, tests_counter))
    general_log.append('[INFO] <{0}> В курсе всего {1} тестов'.format(course_name, tests_counter))
    return tests_counter


# функция для поиска и нажатия кнопкок запуска тестирования
def run_tests_on_page(course_url, course_name, test_number):
    run_test_button_mask = ['//*[@class="tree-node tree-node-type-testcontentsection"]//ancestor::tr[1]//td[7]//button',
                       '//*[@class="mira-horizontal-layout-wrapper clearfix"]//*'
                       '[@class="button mira-button-primary mira-button"]//*'
                       '[contains(text(),"Запустить тест")]',
                        '//*[@class="mira-horizontal-layout-wrapper clearfix"]//*'
                        '[@class="button mira-button-primary mira-button"]//*'
                        '[contains(text(),"Продолжить предыдущую попытку")]']  # маска для поиска кнопки запуска не ПРВТ
    # и ПРВТ тестирования соответственно. В итоговом тесте кнопка появлятся после прохождения преъидущих
    button_ok = '//*[@id="btnOk"]'
    wait_window_load_and_switch(0)
    driver.get(course_url)  # Переход на страницу с выбранным тестом
    driver.get(course_url)  # Сука тупорылый сайт не переходит по url с первого раза
    wait_window_load_and_switch(0)
    no_test_button_counter = 0  # Счетчик не найденных кнопок с запуском теста
    for each_button in run_test_button_mask:
        if wait_element_load(each_button):
            if each_button == run_test_button_mask[0]:  # если это не ПРВТ
                for i in range(10):  # делаем 10 попыток кликнуть
                    try:
                        wait_window_load_and_switch(0)
                        driver.find_elements(By.XPATH, each_button)[test_number].click()  # кликаем по кнопке начала
                        # тестирования
                        break
                    except Exception as ex:
                        print('[ERR] {0} Не получилось кликнуть по кнопке запуска теста, пробую снова'.format(ex))
                        time.sleep(1)
                        continue
                wait_window_load_and_switch(1)
            else:  # если это ПРВТ
                for i in range(10):  # делаем 10 попыток кликнуть
                    try:
                        wait_window_load_and_switch(0)
                        driver.find_elements(By.XPATH, each_button)[-1].click()  # кликаем по кнопке начала
                        # тестирования
                        break
                    except Exception as ex:
                        print('[ERR] {0} Не получилось кликнуть по кнопке запуска теста, пробую снова'.format(ex))
                        time.sleep(1)
                        continue
                wait_window_load_and_switch(1)
                if wait_element_load('//*[@id="btnOk"]'):  # проверяем вылезло ли окно с подтверждением начать тест
                    # и соглашаемся
                    for i in range(10):  # делаем 10 попыток кликнуть
                        try:
                            wait_element_load(button_ok)
                            driver.find_element(By.XPATH, button_ok).click()
                            break
                        except Exception as ex:
                            print('[ERR] <{0}> Не смог кликнуть кнопку подтверждения списания попытки, пробую снова'.
                                  format(ex))
                            time.sleep(1)
                            continue
                return 1
        else:
            no_test_button_counter += 1
        if no_test_button_counter == len(run_test_button_mask):  # если нет кнопок с запуском тогда off
            print('[INFO] <{0}> Не нашел кнопок запуска тестирования №{1}'.format(course_name, test_number + 1))
            general_log.append('[INFO] <{0}> Не нашел кнопок запуска тестирования №{1}'.
                               format(course_name, test_number + 1))
            return 0
    return 1


# кликаем по правильным ответам в тесте
def right_answer_click():  # собираем массив с ссылками на правильные ответы и кликаем по ним
    weblist_array = get_weblist_array()
    database_array = excelparsing.get_array_from_database()  # получаем массив с данными из базы Excel
    answer_link_click, founded_questions_id, founded_database_question, founded_database_answer, unidentified_question \
        = test_solving.find_answer_to_click(weblist_array, database_array)
    unknown_question_amount = 0  # переменная для подсчета не найденных вопросов и последующего ожидания ввода юзера,
    # если прога не нашла ответ в базе и нужно подождать экран с результатом теста, чтобы выяснил юзер правильно ли он
    # ткнул вручную
    driver.maximize_window()
    for num, each in enumerate(answer_link_click):
        try:
            wait_element_load('//*//div//table//tbody//tr//td//div//span')
            founded_questions_mask = "//*[@data-quiz-uid='" + founded_questions_id[num] + "']"
            wait_element_load(founded_questions_mask)
            question_select = driver.find_element(By.XPATH, founded_questions_mask)
            driver.execute_script("arguments[0].scrollIntoView();", question_select)  # прокрутка
            # чтобы можно было кликнуть
            WebDriverWait(driver, 10).until(ec.visibility_of(each))  # ждем чтобы элемент был виден и кликаем по нему
            each.click()
        except Exception as ex:
            print('[INFO] {0} Произошла проблема при прокликивании вариантов ответа'.format(ex))
    # логгируем всякую еботню для братка
    weblist_array = get_weblist_array()  # обновляем данные с сайта (в частности для проверки checkbox)
    prog_logging.get_logs(weblist_array, founded_database_question, founded_database_answer, unidentified_question)
    # считаем кол-во не отвеченных вопросов
    unknown_answer_list = []
    unknown_question_list = []  # массив вопросов которые не нашла в базе прога
    for num_question, each_question in enumerate(weblist_array[4]):
        if not sum(each_question):
            unknown_answer_list.append(num_question + 1)
            unknown_question_list.append(weblist_array[0][0][num_question])

    course_log.append(unknown_question_list)
    print("\nОстались не отвечеными {0} вопросов из {1}. Это вопросы №{2}".format(
        len(unknown_answer_list), len(weblist_array[4]), unknown_answer_list))
    if unknown_answer_list:  # если есть не кликнутые ответы то ждем указаний юзера
        wait_for_user(
            '[ALARM] OMG!!!Прога кликнула не все варианты! Выбери ответ и нажми Enter чтобы продолжить, "x" для выхода')
        unknown_question_amount = len(unknown_answer_list)
    return unknown_question_amount


# ищем и кликаем по кнопке "Ответить" и ищем следуйщий раздел и переходим на него
def end_test_click(course_name, passing_score):
    answer_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                         'check_button quiz_models_components_button_check_button")]]'  # кнопка Ответить
    endtest_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                          'next_button quiz_models_components_button_next_button")]]'  # кнопка Завершить тестирование
    section_mask = '//div[@class="section-title-area"]//div[@class="before-title"]'  # маска для определения № раздела
    frame_mask = '//*[@id="Content"]'
    first_section_mask = '//div[@class="section-title-area"]//*[contains(text(),"Раздел 1")]'
    unknown_question_amount = 0  # переменная для ожидания ввода юзера, если прога не нашла ответ в базе то нужно
    # подождать экран  результатом теста, чтобы выяснил юзер правильно ли он ткнул вручную
    wait_window_load_and_switch(1)
    wait_element_load(frame_mask)
    driver.switch_to.frame(driver.find_element(By.XPATH, frame_mask))  # Пидорги засунули
    # весь контент в айфрейм, поэтому переключаемся на него сделай еще проверку на отрытие окна с
    # подтверждением сдачи и нажатием там кнопки ОК
    wait_element_load(answer_button_mask)
    try:  # пытаемся узнать сколько разделов в тесте
        wait_element_load(section_mask)
        section_text = str(driver.find_element(By.XPATH, section_mask).text)
        section_amount = int(re.findall(r'\d+', section_text)[1]) - int(re.findall(r'\d+', section_text)[0]) + 1  #
        # выясняем количество  оставшихся разделов по фильтру
        for each in range(section_amount):
            time.sleep(10)  # пока вот такое гавно
            wait_window_load_and_switch(1)
            wait_element_load(frame_mask)
            driver.switch_to.frame(driver.find_element(By.XPATH, frame_mask))
            unknown_question_amount += right_answer_click()
            if each == 0 and wait_element_load(first_section_mask) and passing_score <= 90:  # делаем ошибки только если
                # проходной балл < 90% и 1й раздел ПРВТ
                make_wrong_answers(1, unknown_question_amount)
            # wait_for_user(*** Доверяешь ли ты проге? Нажми Enter чтобы продолжить, "x" для выхода ***')
            time.sleep(5)  # пока вот такое гавно
            # Считаем количество символов во всех вопросах и делаем соответствующую задержку
            weblist_array = get_weblist_array()
            questions_symbols_count = 0
            for every in weblist_array[0][0]:  # считаем общее количество символов во всех вопросах
                questions_symbols_count += len(every)
            random_delay_timer(questions_symbols_count)  # в зависимости от количества символово делаем соотв. задержку
            for i in range(10):  # делаем 10 попыток кликнуть на кнопку Ответить
                try:
                    driver.find_element(By.XPATH, answer_button_mask).click()
                    break
                except Exception as ex:
                    print('[ERR] <{0}> Не смог кликнуть кнопку Ответить, пробую снова'.format(ex))
                    time.sleep(1)
                    continue
    except NoSuchElementException:
        print('[INFO] <{0}> В данном тесте только один раздел'.format(course_name))
        general_log.append('[INFO] <{0}> В данном тесте только один раздел'.format(course_name))
        wait_window_load_and_switch(1)
        wait_element_load(frame_mask)
        driver.switch_to.frame(driver.find_element(By.XPATH, frame_mask))
        unknown_question_amount = right_answer_click()
        if passing_score <= 90:  # делаем ошибки только если проходной балл < 90%
            make_wrong_answers(0, unknown_question_amount)
        # wait_for_user('*** Доверяешь ли ты проге? Нажми Enter чтобы продолжить, "x" для выхода ***')
        time.sleep(5)  # пока вот такое гавно
        # Считаем количество символов во всех вопросах и делаем соответствующую задержку
        weblist_array = get_weblist_array()
        questions_symbols_count = 0
        for every in weblist_array[0][0]:  # считаем общее количество символов во всех вопросах
            questions_symbols_count += len(every)
        random_delay_timer(questions_symbols_count)  # в зависимости от количества символово делаем соотв. задержку
        for i in range(10):  # делаем 10 попыток кликнуть на кнопку Ответить
            try:
                driver.find_element(By.XPATH, answer_button_mask).click()
                break
            except Exception as ex:
                print('[ERR] <{0}> Не смог кликнуть кнопку Ответить, пробую снова'.format(ex))
                time.sleep(1)
                continue
    wait_element_load('//*[contains(.,"Тестирование завершено")]')
    driver.find_element(By.XPATH, endtest_button_mask).click()
    if unknown_question_amount:  # если был ткнут вариант ответа вручную, то ждем подтверждения
        wait_for_user('[ALARM] <[0]> Непонятно правильный ли вариант юзер ткнул. Нажми Enter если чекнул все варианты,'
                      ' или x чтобы выйти'.format(course_name))
        try:
            for each in course_log[0]:
                print('Неизвестный вопрос: {0}'.format(each))
        except Exception as ex:
            print('{0} Нет неизвестных вопросов'.format(ex))
        try:
            for num, each in enumerate(course_log[1]):
                print('Неверно кликнутый вопрос и ответы на него: {0}\n-->{1}'.format(each, course_log[2][num]))
        except Exception as ex:
            print('{0} Нет неверно кликнутых вопросов'.format(ex))
        playsound(music_path)
    if wait_element_load('//*[@class="testing_success"]'):
        print('[INFO] <{0}> Назначенный тест сдан'.format(course_name))
        general_log.append('[INFO] <{0}> Назначенный тест сдан'.format(course_name))
    else:
        print('[INFO] <{0}> Назначенный тест НЕ сдан'.format(course_name))
        general_log.append('[INFO] <{0}> Назначенный тест НЕ сдан'.format(course_name))
    driver.close()
    wait_window_load_and_switch(0)


# делаем ошибки смотря на проходной бал кроме ПРВТ. Везде где меньше 100% делаем 0-1 ошибку, но чтобы было не менее 90%
# в ПРВТ делаем 2-4 ошибки рандомно в 1м разделе
def make_wrong_answers(test_type, unknown_question_amount):  # если принимаемое значени = 1, то это ПРВТ иначе не ПРВТ
    weblist_array = get_weblist_array()
    if test_type:  # если тест ПВРТ делаем минимум 2 ошибки с 80% результат
        passing_score = 80
        min_mistakes_count = 2
    else:   # если тест не ПВРТ делаем минимум 0 ошибок с 90% результат
        passing_score = 90
        min_mistakes_count = 0
    max_mistakes_count = int(len(weblist_array[0][0]) - (passing_score / (100 / len(weblist_array[0][0]))))
    min_mistakes_count = 2  # для тестирования
    max_mistakes_count = 4  # для тестирования
    wrong_answers_count = random.randint(min_mistakes_count, max_mistakes_count) - unknown_question_amount  # считаем
    # рандомное количество ошибок которое нужно сделать в тесте за вычетом ненайденных ответов
    if wrong_answers_count <= 0:
        print('[INFO] Ошибок делать не нужно, т.к. разница м/у рандомным кол-вом ошибок и ненайденным вопросами <= 0')
        return
    wrong_counter = 0  # количество уже сделанных ошибок
    wrong_answer_link_click = []  # лист с рандомно выбранными неправильными ответами
    wrong_question_id = []  # лист с ID неверно кликнутых вопросов
    wrong_answer_number_list = []  # лист с номерами вопросов на которые даны неверные ответы
    wrong_question = []  # неправильные вопросы, которые прога кликнула
    wrong_answer = []  # неправильные ответы, которые прога кликнула
    # Симметрично рандомно мешаем элементы в массивах с checkbox, ID вопросов и ссылками на ответы
    random_weblist = list(zip(weblist_array[4], weblist_array[3], weblist_array[2], weblist_array[1],
                              weblist_array[0][0]))
    random.shuffle(random_weblist)

    weblist_array[4], weblist_array[3], weblist_array[2], weblist_array[1], weblist_array[0][0] = zip(*random_weblist)
    for num_answer, each_answer in enumerate(weblist_array[4]):
        temp_wrong_answer = []
        if wrong_counter >= wrong_answers_count:
            break
        if sum(each_answer) > 1:  # если вопрос с несколькими вариантами ответов, то
            wrong_counter += 1
            for num, every in enumerate(each_answer):  # читаем каждый вариант ответа
                if every:  # если был выбран, то добавляем в массив чтобы выбора не было
                    wrong_answer_link_click.append(weblist_array[2][num_answer][num])  # снимаем checkbox
                    wrong_question_id.append(weblist_array[3][num_answer])  # добавляем ID вопроса как неправильного
                    # c верного ответа
                    if not weblist_array[0][0][num_answer] in wrong_question:  # добавляем название неверноклик. вопроса
                        wrong_question.append(weblist_array[0][0][num_answer])
                    if not weblist_array[1][num_answer][num] in wrong_answer:  # добавляем неверноклик. ответ
                        temp_wrong_answer.append(weblist_array[1][num_answer][num] + '*убрал выбор*')
                    if not num_answer + 1 in wrong_answer_number_list:  # добавляем № невернокликнутого вопроса
                        wrong_answer_number_list.append(num_answer + 1)
                    break
            for num, every in enumerate(each_answer):  # читаем каждый вариант ответа
                if not every:  # если не был выбран ответ и сумма неверных
                    # ответов не превышает сумму верных, то добавляем в массив чтобы сделать неверные ответы
                    wrong_answer_link_click.append(weblist_array[2][num_answer][num])
                    wrong_question_id.append(weblist_array[3][num_answer])  # добавляем ID вопроса как неправильного
                    if not weblist_array[0][0][num_answer] in wrong_question:  # добавляем название неверноклик. вопроса
                        wrong_question.append(weblist_array[0][0][num_answer])
                    if not weblist_array[1][num_answer][num] in wrong_answer:  # добавляем неверноклик. ответ
                        temp_wrong_answer.append(weblist_array[1][num_answer][num] + '*выбрал*')
                    if not num_answer + 1 in wrong_answer_number_list:  # добавляем № невернокликнутого вопроса
                        wrong_answer_number_list.append(num_answer + 1)
                    break
            wrong_answer.append(temp_wrong_answer)  # добавляем временный набор ответов, чтобы индекс вопроса в
            #  wrong_question соответствовал индексу массива ответов
    if wrong_counter < wrong_answers_count:
        for num_answer, each_answer in enumerate(weblist_array[4]):
            temp_wrong_answer = []
            if wrong_counter >= wrong_answers_count:
                break
            for num, every in enumerate(each_answer):  # читаем каждый вариант ответа
                if every and not weblist_array[2][num_answer][num] in wrong_answer_link_click:  # если был выбран,
                    # и такого же елемента нет в листе то добавляем в массив чтобы выбора не было
                    wrong_answer_link_click.append(weblist_array[2][num_answer][num])  # снимаем checkbox
                    # c верного ответа
                    wrong_question_id.append(weblist_array[3][num_answer])  # добавляем ID вопроса как неправильного
                    if not weblist_array[0][0][num_answer] in wrong_question:  # добавляем название неверноклик. вопроса
                        wrong_question.append(weblist_array[0][0][num_answer])
                    if not weblist_array[1][num_answer][num] in wrong_answer:  # добавляем неверноклик. ответ
                        temp_wrong_answer.append(weblist_array[1][num_answer][num] + '*убрал выбор*')
                    if not num_answer + 1 in wrong_answer_number_list:  # добавляем № невернокликнутого вопроса
                        wrong_answer_number_list.append(num_answer + 1)
                    break
            for num, every in enumerate(each_answer):  # читаем каждый вариант ответа
                if not every and not weblist_array[2][num_answer][num] in wrong_answer_link_click:  # если не был выбран
                    # и такого же елемента нет в листе то добавляем в массив чтобы сделать неверные ответы
                    wrong_answer_link_click.append(weblist_array[2][num_answer][num])
                    wrong_question_id.append(weblist_array[3][num_answer])  # добавляем ID вопроса как неправильного
                    if not weblist_array[0][0][num_answer] in wrong_question:  # добавляем название неверноклик. вопроса
                        wrong_question.append(weblist_array[0][0][num_answer])
                    if not weblist_array[1][num_answer][num] in wrong_answer:  # добавляем неверноклик. ответ
                        temp_wrong_answer.append(weblist_array[1][num_answer][num] + '*выбрал*')
                    if not num_answer + 1 in wrong_answer_number_list:  # добавляем № невернокликнутого вопроса
                        wrong_answer_number_list.append(num_answer + 1)
                    break
            wrong_counter += 1
            wrong_answer.append(temp_wrong_answer)  # добавляем временный набор ответов, чтобы индекс вопроса в
            #  wrong_question соответствовал индексу массива ответов
    for num, each in enumerate(wrong_answer_link_click):
        try:
            wait_element_load('//*//div//table//tbody//tr//td//div//span')
            wrong_questions_mask = "//*[@data-quiz-uid='{0}']".format(wrong_question_id[num])
            wait_element_load(wrong_questions_mask)
            question_select = driver.find_element(By.XPATH, wrong_questions_mask)
            driver.execute_script("arguments[0].scrollIntoView();", question_select)  # прокрутка
            # чтобы можно было кликнуть
            WebDriverWait(driver, 10).until(ec.visibility_of(each))  # ждем чтобы элемент был виден и кликаем по нему
            each.click()
        except Exception as ex:
            print('[INFO] Произошла проблема при прокликивании неверных вариантов ответа:\n {0}'.format(ex))
    course_log.append(wrong_question)
    course_log.append(wrong_answer)
    print('[INFO] Сделаны ошибки в вопросах №{0}'.format(wrong_answer_number_list))


# функция для нахождения проходного бала
def check_passing_score():
    passing_score_mask = '//*[@class="state mira-data-view-table-state-list"]//*[contains(text(),"%")]'
    wait_element_load(passing_score_mask)
    try:
        passing_score_value = driver.find_elements(By.XPATH, passing_score_mask)[-1].get_attribute('innerText')  # суки
        # скрыли текст, а эта штука как говорится working like a charm
        passing_score_value = int(re.findall(r'\d+', passing_score_value)[0])  # находим значение проходного балла
    except Exception as ex:
        print('[ERR] {0} Нет значения проходного балла. Вписываю значение 90 чи как'.format(ex))
        passing_score_value = 90
    return passing_score_value


# задержка для того чтобы загрузились скрипты, ajax и прочее гавно
def wait_element_load(_courses_list_filter, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(ec.presence_of_element_located((By.XPATH, _courses_list_filter)))
        return 1
    except TimeoutException:
        return 0


# функция ожидания загрузки окон и переключения на целевое окно (1й аргумент функции)
def wait_window_load_and_switch(window_number, timeout=1):
    try:
        driver.implicitly_wait(timeout)
        WebDriverWait(driver, timeout).until(ec.number_of_windows_to_be(window_number + 1))
        driver.switch_to.window(driver.window_handles[window_number])
        driver.implicitly_wait(timeout)
        return 1
    except TimeoutException:
        return 0


# рандомная задержка с отображением оставшегося времени
def random_delay_timer(timer_multiply=1000):
    delay = timer_multiply
    for remaining in range(delay, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} секунд осталось из {:2d} секунд.".format(remaining, delay))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rТаймер кончил за {:2d} секунд!            \n".format(delay))


# ожидание ввода пользователя
def wait_for_user(err_message):
    print(err_message)
    playsound(music_path)
    accept = input()
    if accept == 'x':
        sys.exit()
    else:
        return 1


# запускаем скрипта с полным автоматическим решением теста (включая поиск тем и переключение по темам)
def start_script():
    change_timezone_button_mask = '//*[@class="button mira-button"]//*[contains(text(),"Отменить")]'
    working_place_button_mask = '//*[@class="button mira-button-primary mira-button"]'
    login()
    auth()
    if wait_element_load(working_place_button_mask):  # смотрим есть ли кнопка смены рабочего места и согл-ся
        for i in range(0, 10):
            try:
                driver.find_elements(By.XPATH, working_place_button_mask)[-1].click()
                break
            except Exception as ex:
                print('[ERR] {0} Не могу кликнуть кнопку смены рабочего места, пробую снова'.format(ex))
                time.sleep(1)
                continue
    if wait_element_load(change_timezone_button_mask):  # смотрим есть ли кнопка отмены смены часового пояса и отменяем
        for i in range(0, 10):
            try:
                driver.find_elements(By.XPATH, change_timezone_button_mask)[-1].click()
                break
            except Exception as ex:
                print('[ERR] {0} Не могу кликнуть кнопку смены часового пояса, пробую снова'.format(ex))
                time.sleep(1)
                continue
    courses_url = 0
    courses_list_text = 0
    passing_score_list = 100
    for i in range(0, 10):  # делаем 10 попыток найти курсы, если не получается, выходим из проги
        try:
            driver.get(_find_courses_link)  # Поиск курсов для сдачи
            driver.get(_find_courses_link)  # Поиск курсов для сдачи
            courses_url, courses_list_text, passing_score_list = find_courses()  # Найти курсы
            break
        except Exception as ex:
            print('[ERR] {0} Не могу найти URL и названия назначенных тем'.format(ex))
            time.sleep(1)
            if i == 9:
                playsound(music_path)
                return
            continue
    if not courses_url:
        print('Нет назначенных курсов')
        sys.exit()
    print('---Всего назначенных курсов---')
    for num, each in enumerate(courses_list_text):
        print(num + 1, '<{0}>'.format(each))
    # Ждем от юзера ввода номеров курсов
    selected_courses = []  # курсы которые выбрал юзер
    playsound(music_path)
    course_num = input('Выбери номера курсов через пробел и нажми Enter:')
    for each in re.findall(r'\d+', course_num):  # находим из введеного юзера только числа
        selected_courses.append(int(each))
    wait_for_user('Ты выбрал курсы №{0}. Нажми Enter для подтверждения, для выхода "x"'.format(selected_courses))
    for each_selected in selected_courses:  # перебираем тесты которые выбрал юзер находим количество тестов в курсе
        amount_of_tests = find_amount_of_tests_on_page(courses_url[each_selected-1], courses_list_text[each_selected-1])
        run_theory_on_page(courses_url[each_selected - 1], courses_list_text[each_selected - 1])  # прокликиваем теорию
        for each_test in range(0, amount_of_tests):  # проходимся по всем тестам в курсе (матрёшка бля)
            try:
                if run_tests_on_page(courses_url[each_selected-1], courses_list_text[each_selected-1], each_test):
                    course_log.clear()  # обнуляем массив с логом от предъидущего курса
                    end_test_click(courses_list_text[each_selected-1], passing_score_list[each_selected-1])
            except StaleElementReferenceException:
                print("[ERR] <{0}> Не везде кликнул".format(courses_list_text[each_selected-1]))
                general_log.append("[ERR] <{0}> Не везде кликнул".format(courses_list_text[each_selected-1]))
            except NoSuchWindowException:
                print('[INFO] <{0}> Не удалось перейти на страницу со всеми тестами'.
                      format(courses_list_text[each_selected-1]))
                general_log.append('[INFO] <{0}> Не удалось перейти на страницу со всеми тестами'.
                                   format(courses_list_text[each_selected-1]))
    print('************************************')
    print('В общем чо по итогу кожаный ублюдок:')
    print(*general_log, sep='\n')
    playsound(music_path)


def main():
    start_script()
    wait_for_user('За {0} курсы пройдены. Нажми Enter для завершения'.format(username))
    sys.exit()


main()
sys.exit()
# if __name__ == '__main__':
#     main()

