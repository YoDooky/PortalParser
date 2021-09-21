# модуль для обработки данных с базы данных Excel и Web страницы теста с выводом массива элементов для клика


def find_answer_to_click(weblist_array, database_array):
    err_message = "В твоей дырявой базе ответов чуть менее чем нихуя. Выбери правильные ответы и заверши тест. " \
                  "После этого для продолжения введи 'y' и нажми Enter. Если хочешь выйти из прожки введи 'x'"
    unidentified_question = []  # массив c ответами, которые не были найдены
    answer_link_to_click = []
    founded_questions_id = []  # массив с вопросами которые были найдены и в базе и в тесте и ответы на эти вопросы были найдены и в базе и в тесте
    founded_weblist_questions = []  # массив с вопросами которые были найдены и в базе и в тесте и ответы на эти вопросы были найдены и в базе и в тесте (вопросы в массиве не повторяются)
    founded_weblist_answers = []  # массив с ответами которые были найдены и в базе и в тесте
    current_answers = []  # массив с ответами на текущий в цикле вопрос. Сделан чтобы каждому элементу массива "founded answers" соответствовали ответы
    founded_database_question = []  # массив с вопросами которые были найдены в базе
    founded_database_answer = []  # массив с ответами которые были найдены в базе
    clear_weblist_array = clear_symbols(weblist_array)  # данные (вопросы и ответы) с веб страницы
    clear_database_array = clear_symbols(database_array)  # данные (вопросы и ответы) с базы данных
    last_num = 10  # костыль для того чтобы отслеживать сменился ли вопрос в следующем ниже цикле, чтобы не было повторяющихся найденных вопросов в массиве "founded_questions"

    for num, each in enumerate(clear_weblist_array[0][0]):  # перебираем вложенный массив с вопросами в массиве с данными
        next_question = 0  # флаг того что ответ на вопрос дан верный и нужно перейти к следующему (если = 1)
        try:
            correct_answer = []
            answer_list_index = clear_database_array[0].index(each)  # ищем индекс вопроса во вложенном массиве с вопросами в базе данных (по сути является и индексом ответа)
            correct_answer.append(clear_symbols((get_answer(database_array[1][answer_list_index]))))
            founded_database_answer.append((get_answer(database_array[1][answer_list_index])))
            founded_database_question.append(database_array[0][answer_list_index])  # добавляем в массив с вопросами найденный в базе вопрос
            for answer_count in range(len(correct_answer[0])):  # перебираем все "или" в базе
                suggest_answer_link_to_click = []
                if next_question:
                    break
                answer_correct = 0  # счетчик правильных ответов (когда он = кол-ву вар-ов в базе цикл прерывается)
                for num_answer, each_answer in enumerate(clear_weblist_array[1][num]):  # перебираем все ответы из web
                    if next_question:
                        break
                    for num_correct_answer, each_correct_answer in enumerate(correct_answer[0][answer_count]): # перебираем все варианты правильных ответов
                        if next_question:
                            break
                        if each_answer == each_correct_answer:
                            answer_correct += 1
                            suggest_answer_link_to_click.append(clear_weblist_array[2][num][num_answer])
                            founded_questions_id.append(weblist_array[3][num]) #добавляем ID найденного вопроса
                            if last_num != num:  # если вопрос тот же самый не добавляем его по новой в массив с вопросами для лога
                                founded_weblist_questions.append(weblist_array[0][0][num])
                            current_answers.append(weblist_array[1][num][num_answer])
                            last_num = num
                            if answer_correct == len(correct_answer[0][answer_count]): # если ответ и количество ответов совпало с базой то следующий вопрос
                                answer_link_to_click.extend(suggest_answer_link_to_click)
                                next_question = 1
            # добавляем массив с текущими ответами на вопрос в общий массив со всеми ответами на вопросы
            if current_answers:
                founded_weblist_answers.append(current_answers)
                current_answers = []

        except:
            unidentified_question.append(weblist_array[0][0][num])  # помещаем в массив ответы, которые не были найдены
            continue
    if len(unidentified_question) != 0:
        return answer_link_to_click, "wait", err_message, founded_questions_id, founded_database_question, founded_database_answer, unidentified_question
    else:
        return answer_link_to_click, "", err_message, founded_questions_id, founded_database_question, founded_database_answer, unidentified_question


# пытаемся перевести в конкретный текст из базы данных в значение ответа
def get_answer(answer):
    answer_array = []
    answer_list = []
    last_index = -2
    symbol = '*)'
    for every_answer in answer:
        length = len(every_answer)
        delimiter_index = []  # обнуляем массив с индексами, чтобы не засунуть те же самые элементы из первого елемента массива "answer"
        if every_answer.find(symbol) != -1:  # если нашел в строке разделитель
            x = 0
            while x <= length:  # цикл для прохождения по всем символам строки
                index = every_answer.find(symbol, x)
                if index != -1:  # если нашел порядковый номер первого символа строки содержащего разделитель, то
                    x = index + 1  # начинаем итерацию в следующем цикле с этого символа
                elif last_index == index or index == -1:  # если больше нет новых символов с разделителем то выходим из цикла :
                    # x += 1
                    break
                last_index = index
                delimiter_index.append(index)
            for each in range(
                    len(delimiter_index)):  # цикл для помещения всех символов до разделителя в массив с ответами
                if each == len(delimiter_index) - 1:  # если последний элемент массива, то добавляем все остальные символы после разделителя до конца строки
                    answer_list.append(every_answer[delimiter_index[each]: len(every_answer)])
                    break
                else:
                    answer_list.append(every_answer[delimiter_index[each]: delimiter_index[
                        each + 1]])  # добавляем в массив символы между разделителями и до первого разделителя
        else:
            answer_list.append(every_answer)
        answer_array.append(answer_list)
        answer_list=[]
    return answer_array


# функция для удаления спецсимволов из входного массива(не более чем трехмерного) или строки
def clear_symbols(
        string_object):
    if isinstance(string_object, list):
        each_array = []
        for each in string_object:
            every_array = []
            if isinstance(each, list):
                for every in each:
                    i_array = []
                    if isinstance(every, list):
                        for i in every:
                            i_array.append(del_specific_symbols(i))
                        every_array.append(i_array)
                    else:
                        every_array.append(del_specific_symbols(every))
                each_array.append(every_array)
            else:
                each_array.append(del_specific_symbols(each))
        clean_string = each_array
    else:
        clean_string = del_specific_symbols(string_object)
    return clean_string


# проверка на строку и удаление всех спец символов и пробелов и lowercase в строке
def del_specific_symbols(
        string_object):
    if isinstance(string_object, str):
        output_variable = string_object.lower().translate(
            {ord(c): None for c in '*); \xa0'})  # игнорируем спец символы и пробелы
    else:
        output_variable = string_object
    return output_variable
