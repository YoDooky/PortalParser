import sys
import time
import excelparsing
import processing
#import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException

username = "79833207865"  # Имя юзера (впоследствии получаемое через бота)
password = "0Jh#8GPT"  # Пароль юзера (впоследствии получаемый через бота)
d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}
files_path = "C:/Prometei/"  # путь к папке со всеми файлами (драйвер хрома, база данных и т.п.)
options = Options()
options.add_argument('--log-level=3')
driver = webdriver.Chrome(
    files_path + "chromedriver.exe", options=options)  # Это нужно чтобы можно было выгружать логи с браузера (первоначально для Promitei)

_find_courses_link = "https://hiprof.irkutskoil.ru/mira/#&step=3&measureStageStatus=NOT_FINISHED&s" \
                     "=77qkVxPnc0fyBbAnvxXE&doaction=MyMeasureStatisticsAllPeriodNotFinished&id=&type" \
                     "=mymeasurestatisticslist&measurePeriod=ALL_PERIOD "
_auth_link = "https://hiprof.irkutskoil.ru/mira/Do?doaction=Go&s=YwSqVdexvj7jQdJp9sEs&id=0&type=customloginpage"
_auth_wrong = "https://hiprof.irkutskoil.ru/mira/Do?s=EdzhmqcF8wyvUuhXhq4B&errorMessage=%D0%9D%D0%B5%D0%B2%D0%B5%D1" \
              "%80%D0%BD%D1%8B%D0%B5+%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5+%D0%B4%D0%BB%D1%8F+%D0%B0%D0%B2%D1%82%D0%BE" \
              "%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8.&doaction=GoToFormAuthError&id=0&type=customloginpage" \
              "&actionsign=%242a%2410%24fP4S90TxnasJs6O8GqLLmOOWqlF4wn%2Fq0AQQhYkM.rkLkvNp.iiaC "

# res_x = int(input('Введи разрешение по Х: ') or "1920")  # разрешение по X
# res_y = int(input('Введи разрешение по Y: ') or "1080")  # разрешение по Y
# window_width = res_x / 2  # ширина окна
# window_height = res_y  # высота окна

# driver.set_window_position(res_x - window_width, 1)  # располагаем окно где надо
# driver.set_window_size(window_width, window_height)  # выбираем размеры окна
driver.maximize_window()


def login():
    global username
    global password
    username =username# input('Введи имя работяги: ')
    password =password# input('Введи пароль работяги: ')


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
    courses_list_mask = "//*[@data-mira-grid-row]//td//a[@class='mira-grid-cell-action']"  # Переделай более грамотно
    # как в find_course_url
    courses_path_mask = "//*[@data-mira-grid-row]//td//div[@class='mira-grid-cell-operation border-box  primary  ']"
    driver.switch_to.window(driver.window_handles[0])  # переключаемся на основное окно браузера
    driver.get(_find_courses_link)  # Поиск курсов для сдачи
    # time.sleep(5)
    courses_list = []
    wait_until_load(courses_list_mask)  # Ждём пока загрузятся курсы
    try:
        courses_list = driver.find_elements(By.XPATH, courses_list_mask)
        courses_path = driver.find_elements(By.XPATH, courses_path_mask)
        courses_list_count = len(
            courses_list)  # Костыль для for (python не может сам в цикле преобразовать тип данных)
        for each_course in range(0, courses_list_count):
            print(courses_list[each_course].text)
            # print(courses_path[each_course])
        return courses_path, courses_list
    except Exception:
        print('Не удалось найти назначенные курсы и перейти к ним')
    if not courses_list:
        print('Назначенных курсов нет')
    print('_________________________________________________________________________________________')


# ищем URL страницы с самими вопросами
def find_course_url(course_path):
    run_test_button_mask = '//*[text()[contains(., "Итоговый тест")]]//ancestor::tr[1]//td//*[text()[contains(., ' \
                           '"Запустить")]] '
    course_path.click()  # Переход на страницу с выбранным тестом
    wait_until_load(run_test_button_mask)
    driver.get(driver.current_url)  # Получаем URL страницы с выбранным тестом
    wait_until_load(run_test_button_mask)
    try:
        run_course_button = driver.find_element(By.XPATH, run_test_button_mask)  # Ищем кнопку с запуском теста
        run_course_button.click()
        time.sleep(2)  # говно
        driver.switch_to.window(
            driver.window_handles[1])  # Перекл. на окно с тестом чтобы в дальнейшем получить его URL
    except Exception:
        print("Не удалось найти и запустить окно с тестом")
    driver.switch_to.frame(driver.find_element(By.XPATH,
                                               '//*[@id="Content"]'))  # Пидорги засунули весь контент в айфрейм,
    # поэтому переключаемся на него
    # сделай еще проверку на отрытие окна с подтверждением сдачи и нажатием там кнопки ОК


# # парсим текст с вопросом
# def get_question():
#     question_mask = '//*[@class="question-text"]'
#     wait_until_load(question_mask)
#     question_element = driver.find_elements(By.XPATH, question_mask)
#     return question_element
#
#
# # загружаем в массив ответы на странице для указанного вопроса
# def get_answer(question):
#     answer_mask = "//*[text()[contains(., '" + question + "')]]" + '//ancestor::div[2]//div//table//tbody//tr//td//div'
#     answer_element = driver.find_elements(By.XPATH, answer_mask)
#     current_answers_list = []  # список ответов на текущий вопрос
#     #    wait_until_load(answer_mask)
#     for each in answer_element:
#         current_answers_list.append(each.text)
#     return current_answers_list
# парсим текст с вопросом
def get_question():
    question_mask = '//*[@class="question-text"]'
    question_id_mask = '//*[@class="question-text"]//ancestor::div[3]'
    wait_until_load(question_mask)
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


# положить все вопросы, ответы, линки в один трехмерный массив
def get_category_array():
    question_element, question_id_list = get_question()
    category_list = []
    questions_list = []
    all_question_list = []  # массив с одним массивом, чтобы было проще проходиться по элементам в цикле
    all_answer_list = []
    all_answer_link_list = []
    for each in question_element:
        questions_list.append(each.text)
    for each in question_id_list:
        all_answer_list.append(get_answer(each))
        all_answer_link_list.append(get_answer_link(each))
    all_question_list.append(questions_list)
    category_list.append(all_question_list)
    category_list.append(all_answer_list)
    category_list.append(all_answer_link_list)
    return category_list


# кликаем по правильным ответам в тесте
def right_answer_click(course_theme):  # собираем массив с ссылками на правильные ответы и кликаем по ним
    category_list = get_category_array()
    database_array = excelparsing.get_array_from_database(
        course_theme)  # получаем массив с данными из базы данных Excel
    answer_link_click, wait_user, err_message, founded_questions = processing.find_answer_to_click(category_list,
                                                                                                   database_array)  # получаем массив ссылок на которые нужно кликать и строковую переменную 'wait' если нужно подождать ввод юзера и сообщение об ошибке
    # driver.set_window_position(res_x - window_width, 1)
    # driver.set_window_size(window_width, window_height)
    driver.maximize_window()

    for num, each in enumerate(answer_link_click):
        #
        try:
            wait_until_load('//*//div//table//tbody//tr//td//div//span')
            # each.location_once_scrolled_into_view
            # driver.execute_script("window.scrollTo(0, 2)")
            time.sleep(1)
            founded_questions_mask = "//*[text()[contains(., '" + founded_questions[num] + "')]]"
            question_select = driver.find_element(By.XPATH, founded_questions_mask)
            driver.execute_script("arguments[0].scrollIntoView();",
                                  question_select)  # прокрутка чтобы можно было кликнуть
            time.sleep(1)
            each.click()
        except:
            print('')
        # driver.execute_script("arguments[0].scrollIntoView();", each)  # прокрутка чтобы можно было кликнуть
    find_clicked_answer()
    if wait_user != "":
        return err_message
    else:
        return ""

# функция для отслеживания прокликанных ответов в web
def find_clicked_answer():
    selector_mask = ['//*[@class="check-control checked"]', '//*[@class="check-control  checked"]']  # маска для нахождения кликнутого check-box
    question_name_mask = './/ancestor::div[3]//*[@class="question-text"]'  # маска для поиска названия вопроса где был кликнут check-box
    answer_name_mask = './/ancestor::div[1]' # маска для поиска названия ответа где был кликнут check-box
    answer_name_list = []  # массив хранящий названия всех кликнутых ответов
    answer_name_intermed = []  # промежуточный массив с ответами
    question_name_list = []  # массив хранящий названия всех кликнутых вопросов
    for each_mask in selector_mask:  # прохождение по массиву с возможными масками кликнутыв check-box
        try:
            selector_elements = driver.find_elements(By.XPATH, each_mask)
            for each_element in selector_elements:  # цикл для поиска ответов и вопросов для каждого check-box
                question_name = each_element.find_element(By.XPATH, question_name_mask)
                answer_name = each_element.find_element(By.XPATH, answer_name_mask)
                answer_name_intermed.append(answer_name.text)
                if selector_elements.index(each_element) < len(selector_elements)-1:  # находим наименоание следующего
                    # вопроса для исключения добавления в массив одного и того же вопроса и для соотношения каждого
                    # вопроса каждому массиву ответов на этот вопрос
                    next_question_name = selector_elements[selector_elements.index(each_element) + 1].find_element(By.XPATH, question_name_mask).text
                else:
                    next_question_name = ''
                if question_name.text != next_question_name:
                    question_name_list.append(question_name.text)
                    answer_name_list.append(answer_name_intermed)
                    answer_name_intermed = []
        except Exception:
            continue

    # -----выводим вопросы которые прога нашла и ответы которые она кликнула-----
    try:
        message_number = 0
        print('\n', "----- Вопросы и ответы которые прога кликнула -----")
        for i in range(len(question_name_list)):
            message_number += 1
            print(' ', message_number, '. ', question_name_list[i], sep='', end='\n')
            for z in range(len(answer_name_list[i])):
                print(answer_name_list[i][z], sep='\n')
    except Exception:
        print("Произошел трабл при логгировании вопроса: ", question_name_list[-1])


# задержка для того чтобы загрузились скрипты, ajax и прочее гавно
def wait_until_load(_courses_list_filter):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, _courses_list_filter)))
    time.sleep(1)


# ожидание ввода пользователя
def wait_for_user(err_message):
    print(err_message)
    accept = input()
    if accept == 'x':
        sys.exit()
    else:
        return 1


# запускаем скрипта с полным автоматическим решением теста (включая поиск тем и переключение по темам)
def start_script(each_course):
    courses_path, courses_list = find_courses()  # Найти курсы
    # global courses_path, courses_list
    value = []
    for each in courses_list:
        value.append(each.text)
    find_course_url(courses_path[each_course])  # передаем путь до страницы со всеми назначенными тестами
    # и до конкретного теста соответственно
    try:
        err_message = right_answer_click(value[each_course])
        if err_message != "":
            wait_for_user(err_message)
    except StaleElementReferenceException:
        print("Не везде кликнул лох")


# запуск лайт скрипта (только прокликивание правильных ответов, юзер сам открывает страницу с вопросами)
def start_light_script():
    solving_repeat = 1
    wait_for_user('Открой окно с тестом. Для продолжения нажми нажми Enter, для выхода "x"')
    while solving_repeat == 1:
        WebDriverWait(driver, 30).until(EC.number_of_windows_to_be(2))
        # driver.current_window_handle
        driver.switch_to.window(driver.window_handles[1])
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="Content"]'))
        right_answer_click("Го катку заебал!")
        solving_repeat = wait_for_user(
            'Для перехода к следующим вопросам, открой окно с тестом и нажми Enter, для выхода "x"')


login()
auth()
start_light_script()
# courses_path, courses_list = find_courses()  # Найти курсы
# for each_course in range(0, len(courses_path)):
#    start_script(each_course)
