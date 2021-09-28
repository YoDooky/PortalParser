# функция для логирования: 1-вопрос найденный в базе, 2-ответ найденный в базе, 3-вопрос найденный в тесте,
# 4-ответ найденный в тесте, 5-не найденный в базе ответ
def get_logs(weblist_array, founded_database_question, founded_database_answer, unidentified_question):
    unidentified_answer = []  # варианты ответов в тесте на ненайденные вопросы в базе

    # -----выводим найденные в базе вопросы и ответы в базе на них-----
    try:
        print('\n', "----- Найденные вопросы и ответы в базе -----")
        message_number = 0
        for i in range(len(founded_database_question)):
            message_number += 1
            print(' ', message_number, '. ', founded_database_question[i], sep='', end='\n')
            for z in range(len(founded_database_answer[i])):
                print(*founded_database_answer[i][z], sep='\n')
    except Exception:
        print("[INFO] Произошел трабл при логгировании вопроса: ", founded_database_question[-1])

    # -----выводим совпадающие с базой вопросы, но не совпадающие с базой ответы на эти вопросы-----
    # находим вопрос с несовпадающими ответами
    # try:
    #     for each_database, num_database in enumerate(database_question):
    #         answer_found = 0
    #         for each_weblist, num_weblist in enumerate(weblist_data[0][0]):
    #             if each_database == each_weblist:
    #                 for each_database_answer in database_answer
    #                 answer_found = 1
    #         if answer_found == 0:
    #             unmatched_question.append(each_database)
    #     # находим ответы на странице с тестом на этот несовпадающий вопрос
    #     for num_weblist_data, each_weblist_data in enumerate(weblist_data[0][0]):
    #         for each_unmatched in unmatched_question:
    #             if each_unmatched == each_weblist_data:
    #                 unmatched_answer.append(weblist_data[1][num_weblist_data])
    #     message_number = 0
    #     print('\n', "----- Вопросы, найденые в базе, но не совпали ответы с тестом -----")
    #     for i in range(len(unmatched_question)):
    #         message_number += 1
    #         print(' ', message_number, '. ', unmatched_question[i], sep='', end='\n')
    #         print(*unmatched_answer[i], sep='\n')
    # except Exception:
    #     print("Произошел трабл при логгировании вопроса: ", unmatched_question[-1])

    # -----выводим не найденные вопросы в базе и варианты ответов на них в тесте-----
    # находим ненайденные вопросы
    try:
        for num_weblist_array, each_weblist_array in enumerate(weblist_array[0][0]):
            for each_unidentified in unidentified_question:
                if each_unidentified == each_weblist_array:
                    unidentified_answer.append(weblist_array[1][num_weblist_array])
        message_number = 0
        print('\n', "----- Вопросы не найденные в базе и варианты ответов на эти вопросы -----")
        for i in range(len(unidentified_question)):
            message_number += 1
            print(' ', message_number, '. ', unidentified_question[i], sep='', end='\n')
            print(*unidentified_answer[i], sep='\n')
    except Exception:
        print("[INFO] Произошел трабл при логгировании вопроса: ", unidentified_question[-1])

    # -----выводим вопросы которые прога выбрала и какие не выбрала-----
    try:
        clicked_question = []
        unclicked_question = []
        all_clicked_answer = []
        unclicked_answer = []
        for num_question, each_question in enumerate(weblist_array[0][0]):
            clicked_answer = []
            last_each_question = ''
            unclicked_counter = 0  # счетчик количества некликнутых вопросов
            for num_answer, each_answer in enumerate(weblist_array[1][num_question]):
                if weblist_array[4][num_question][num_answer] == 1:  # 5й вложенный список в weblist_array
                    # это состояние чекбоксов (1-активен, 0-неактивен)
                    clicked_answer.append(each_answer)
                    if each_question != last_each_question:
                        clicked_question.append(each_question)
                        last_each_question = each_question
                else:
                    unclicked_counter += 1
                if unclicked_counter == len(weblist_array[1][num_question]):  # если кол-во некликнутых = количеству
                    # ответов, то фиксируем вопрос как не кликнутый
                    unclicked_question.append(each_question)
                    unclicked_answer.append(weblist_array[1][num_question])
            if clicked_answer:
                all_clicked_answer.append(clicked_answer)
        message_number = 0
        print('\n', "----- Вопросы и ответы, которые прога выбрала -----")
        for i in range(len(clicked_question)):
            message_number += 1
            print(' ', message_number, '. ', clicked_question[i], sep='', end='\n')
            print(*all_clicked_answer[i], sep='\n')

        message_number = 0
        print('\n', "----- Вопросы и ответы, которые прога НЕ выбрала -----")
        for i in range(len(unclicked_question)):
            message_number += 1
            print(' ', message_number, '. ', unclicked_question[i], sep='', end='\n')
            print(*unclicked_answer[i], sep='\n')
    except Exception:
        print("[INFO] Проблема при логгировании кликнутого/некликнутого вопроса")
