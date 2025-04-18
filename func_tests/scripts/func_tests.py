import os

from docx import Document

from model.assistant import func_tests_messages

from colorama import Fore, Style, init

#Тестовые записи для оценки точности нейросети
test_data_v1 = \
    [
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Пахота зяби под мн тр\nПо Пу 26/488\nОтд 12 26/221\n\nПредп культ под оз пш\nПо Пу 215/1015\nОтд 12 128/317\nОтд 16 123/529\n\n2-е диск сах св под пш\nПо Пу 22/627\nОтд 11 22/217\n\n2-е диск сои под оз пш\nПо Пу 45/1907\nОтд 12 45/299",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Пахота зяби под сою \nПо ПУ 7/1402\nОтд 17 7/141\n\nВырав-ие зяби под кук/силос\nПо ПУ 16/16\nОтд 12 16/16\n\nВырав-ие зяби под сах/свёклу\nПо ПУ 67/912\nОтд 12 67/376\n\n2-ое диск-ие сах/свёкла \nПо ПУ 59/1041\nОтд 17 59/349",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: 12.10\nВнесение мин удобрений под оз пшеницу 2025 г ПУ Юг 149/7264\nОтд 17-149/1443",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Север \nОтд7 пах с св 41/501\nОтд20 20/281 по пу 61/793\nОтд 3 пах подс.60/231\nПо пу 231\n\nДиск к. Сил отд 7. 32/352\nПу- 484\nДиск под Оз п езубов 20/281\nДиск под с. Св отд 10 83/203 пу-1065га",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Внесение удобрений под рапс отд 7 -138/270\nДисклвание под рапс 40/172\nДиск после Кук сил отд 7-32/352 по пу 484га",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: 10.03 день\n2-я подкормка озимых, ПУ \"Юг\" - 1749/2559\n(в т.ч Амазон-1082/1371\nПневмоход-667/1188)\n\nОтд11- 307/307 (амазон 307/307) \n\nОтд 12- 671/671( амазон 318/318; пневмоход 353/353) \n\nОтд 16- 462/1272( амазон 148/437; пневмоход 314/835) \n\nОтд 17- 309/309( амазон 309/309)",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Уборка свеклы 27.10.день\nОтд10-45/216\nПо ПУ 45/1569\nВал 1259680/6660630\nУрожайность 279,9/308,3\nПо ПУ 1259680/41630600\nНа завод 1811630/6430580\nПо ПУ 1811630/41400550\nПоложено в кагат 399400\nВввезено с кагата 951340\nОстаток 230060\nОз-9,04/12,58\nДигестия-14,50/15,05",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Пахота под сах св\nПо Пу 77/518\nОтд 12 46/298\nОтд 16 21/143\nОтд 17 10/17\n\nЧизел под оз ячмень \nПо Пу 22/640\nОтд 11 22/242\n\nЧизел под оз зел корм\nОтд 11 40/40\n\nДиск оз пшеницы\nПо Пу 28/8872\nОтд 17 28/2097\n\n2-е диск под сах св\nПо Пу 189/1763\nОтд 11 60/209\nОтд 12 122/540\nОтд 17 7/172\n\nДиск кук силос\nПо Пу 6/904\nОтд 11 6/229\n\nПрик под оз ячмень\nПо Пу 40/498\nОтд 11 40/100\n\nУборка сои (семенной)\nОтд 11 65/65\nВал 58720\nУрож 9",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Пахота под сах св\nПоПу 91/609\nОтд 11 13/73\nОтд 12 49/347\nОтд 16 20/163\nОтд 17 9/26\n\nЧизел под оз зел корм\nОтд 11 60/100\n\n2-е диск под сах св\nПо Пу 53/1816\nОтд 12 53/593\n\nДиск кук силос\nПо Пу 66/970\nОтд 11 66/295\n\nДиск сах св\nОтд 12 13/13\n\nПрикат под оз ячмень\nПо Пу 40/538\nОтд 11 40/140\n\nУборка сои семенной\nОтд 11 29/94\nВал 37400/96120\nУрож 12,9/10,2",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Пахота под сах св\nПо Пу 88/329\nОтд 11 23/60\nОтд 12 34/204\nОтд 16 31/65\n\nПахота под мн тр\nПо Пу 10/438\nОтд 17 10/80\n\nЧизел под оз ячмень\nПо Пу 71/528\nОтд 11 71/130\n\n2-е диск под сах св\nПо Пу 80/1263\nОтд 12 80/314\n\n2-е диск под оз ячмень\nПо Пу 97/819\nОтд 17 97/179\n\nДиск кук силос\nПо Пу 43/650\nОтд 11 33/133\nОтд 12 10/148\n\nВыкаш отц форм под/г\nОтд 12 10/22\n\nУборка сах св\nОтд 12 16/16\nВал 473920\nУрож 296,2\nДиг - 19,19\nОз - 5,33",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: 20.11 Мир\nПахота зяби под сою 100 га день, 1109 га от начала, 97%, 30 га остаток.\nРаботало 4 агрегата.\nВыравнивание зяби под подсолнечник 47 га день, 141 га от начала, 29 %, остаток 565 га. Работал 1 агрегат\n\nОсадки:\nБригада 1 Воронежская - 6 мм",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: ТСК\nВыравнивание зяби под сою 25 га/ с нарастающим 765 га ( 13%) Остаток 5332 га\nВыравнивание зяби под кукурузу 131га (3%) Остаток 4486 га\nОсадки 1мм",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Восход\nПосев кук-24/252га\n24%\nПредпосевная культ\nПод кук-94/490га46%\nСЗРоз пш-103/557га\n25%\nПодкормка оз рапс-\n152га , 100%, подкормка овса-97га, 50%\nДовсходовое боронование подсолнечника-524\nга, 100%.",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: 30.03.25г.\nСП Коломейцево\n\nпредпосевная культивация\n  -под подсолнечник\n    день 30га\n    от начала 187га(91%)\n\nсев подсолнечника\n  день+ночь 57га\n  от начала 157га(77%)\n\nВнесение почвенного гербицида по подсолнечнику\n день 82га\n  от начала 82га (38%)"
    ]


test_data_v2 =\
    [
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"23.10\nВнесение противозлакового гербецида на оз рапсе ПУ Юг 134/578\nОтд 11-134/253\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Пахота зяби под сою\nПо Пу 13/1440\nОтд 17 13/179\n\nПахота зяби под кук с\nПо Пу 26/471\nОтд 11 26/206\n\nДисков сах св\nПо Пу 85/1237\nОтд 17 85/535\n\nВыравн зяби под сах св\nПо Пу 45/1314\nОтд 11 10/410\nОтд 12 35/661\n\nВыравн зяби под подс\nОтд 11 41/41\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Пахота зяби под сою\nПо Пу 29/1367\nОтд 16 29/760\n\nПредп культ под оз пш\nПо Пу 146/1217\nОтд 11 146/233\n\nДисков сах св\nПо Пу 64/934\nОтд 17 64/232\n\n2-е диск сах св под пш\nПо Пу 25/775\nОтд 12 25/475\"\\",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"ТСК\nВыравнивание зяби под сою 25 га/ с нарастающим 765 га ( 13%) Остаток 5332 га\nВыравнивание зяби под кукурузу 131га (3%) Остаток 4486 га\nОсадки 1мм\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Восход\nПосев кукурузы\nДень-86/107га, 10%\nПредпосевная культ\nДень-177/396га, 37%\n2-я подкорм оз пш\nДень-739/1431га65%\nСЗР по оз пш\nДень-136/272га12%\nСЗР по оз ячм\nДень-71/71га22%\nДовсходовое боронование подсолнечника\nДень-184/289га55%\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Выравн под кук зерно\nПоПу 82/1042\nОтд 12 82/549\nВыравн под кук силос\nПоПу 30/907\nОтд 11 30/437\nПредп культ под сах св\nПоПу 531/1184\nОтд 11 80/174\nОтд 12 260/467\nОтд 16 101/348\nОтд 17 90/195\nСев сах св\nПоПу 357/579\nОтд 11 80/97\nОтд 12 85/130\nОтд 16 81/231\nОтд 17 111/121\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"15.10\nВнесение мин удобрений под оз пшеницу 2025 г ПУ Юг 117/7381\nОтд 17-117/1560\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"ТСК \nВыравнивание зяби под сою 199 га/ с нарастающим 533 га (8%) Остаток 5564 га\nОсадки 2 мм\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"12.10\nВнесение мин удобрений под оз пшеницу 2025 г ПУ Юг 149/7264\nОтд 17-149/1443\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Вырав зяби под подсол\nПо Пу 199/923\nОтд 11 108/241\nОтд 17 91/133\nВырав зяби под сах/ св\nПо Пу 78/2827\nОтд 17 78/857\nВырав зяби под сою\nПо Пу 121/580\nОтд 11 80/80\nОтд 16 41/381\nВырав зяби под Кук/сил\nПо Пу 43/528\nОтд 11 43/149\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Пахота зяби под мн тр\nПо Пу 26/488\nОтд 12 26/221\n\nПредп культ под оз пш\nПо Пу 215/1015\nОтд 12 128/317\nОтд 16 123/529\n\n2-е диск сах св под пш\nПо Пу 22/627\nОтд 11 22/217\n\n2-е диск сои под оз пш\nПо Пу 45/1907\nОтд 12 45/299\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Пахота зяби под мн тр\nПо Пу 13/579\nОтд 12 13/312\n\n2-е дисков сах св\nПо Пу 35/957\nОтд 17 35/290\n\nВыравн зяби под мн тр\nПо Пу 101/438\nОтд 12 101/171\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Пахота зяби под мн тр\nПо Пу 26/514\nОтд 12 26/247\n\nПахота зяби под сою\nПо Пу 13/1351\nОтд 16 13/731\n\nПредп культ под оз пш\nПо Пу 56/1071\nОтд 16 56/585\n\nДисков сах св\nПо Пу 85/870\nОтд 17 85/168\n\n2-е диск сах св под пш\nПо Пу 123/750\nОтд 12 123/450\n\n2-е диск сои под оз пш\nПо Пу 82/1989\nОтд 11 82/993\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Диск оз пшеницы \nПо Пу 95/8627\nОтд 17 95/1923\n\n2-е диск под сах св\nПо Пу 151/1065\nОтд 16 151/842\n\n2-е диск под оз ячмень \nПо Пу 136/605\nОтд 11 70/219\nОтд 11 66/285\n\n2-е диск под рапс\nПо ПУ 60/202\nОтд 16 60/89\n\nПахота под мн тр\nПо Пу 25/386\nОтд 17 25/28\n\nПахота под сах св\nОтд 12 24/105\n\nЧизел под оз ячмень\n(дракула)\nПо Пу 64/350\nОтд 12 64/219\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"26.07\nВнесение мин удобрений под сах свёклу 2025 г ПУ Юг- 80/1157\n\nОтд 12-80/314\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"19.11 Мир\nПахота зяби под кукурузу 8 га день, 672 га от начала, 100%\nПахота зяби под сою 70 га день, 1009 га от начала, 89%, 130 га остаток.\nРаботало 3 агрегата.\nВыравнивание зяби под подсолнечник 15 га день, 15 га от начала, 2%, остаток 691га. Работал 1 агрегат\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"28.03.25г.\nСП Коломейцево\n\nпредпосевная культивация  \n  -под подсолнечник\n    день 40га\n    от начала 60га(29%)\n\nСев сахарной свеклы: \nДень 30га\nОт начала 295га(94%)\n\nсев подсолнечника \n  день 25га\n  от начала 25га(12%)\n\nСплошная культивация под сою:\n  день 55га \n  от начала 200га (80%)\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"АО Кропоткинское\n28.03.25\n2 подкормка озимой пшеницы - 622/6975\nПредпосевная культивация под сах.свеклу - 426/1628\nСев сах.свеклы - 285/1229 (57%) 7ед.\nОсталось 912га\nВыравнивание зяби под кукурузу - 161/2804\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"14.11 Мир\nПахота зяби под кукурузу 57 га день, 562 га от начала, 83%, 110 га остаток.\nПахота зяби под сою 60 га день, 799 га от начала, 70%, 340 га остаток.\nРаботало 5 агрегатов.\nВыравнивание зяби под сахарную свёклу 130 га день, 874 га от начала, 92 %, 78 га остаток.\nРаботал 1 агрегат.\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"30.03.25г Мир.\nПредпосевная культивация под подсолнечник 50/97 - 14%\nСев подсолнечника 17/47 - 6%\n2-я подкормка озимой пшеницы 371/5118 - 97%\nНа данный момент осадки в 2х районах до 3мм\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"АО Кропоткинское\n30.03.2024\n2 подкормка озимой пшеницы 504/7758\nСев сах.свеклы 241/1806 87% (7ед)\nОсталось 335га\nВыравнивание зяби под кукурузу 70/2874\nПредпосевная культивация под подсолнечник 70/70\"",
        "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \"Вырав под сою\nПоПу 24/1481\nОтд 11 24/712\nПредп культ под сах св\nПоПу 369/2656\nОтд 11 156/639\nОтд 12 48/795\nОтд 17 163/751\nСев сах св\nПоПу 355/2287\nОтд 11 80/481\nОтд 12 133/659\nОтд 17 142/678\""
    ]


def read_docx(file_path):
    """
    Читает весь текст из DOCX файла
    :param file_path: путь к файлу .docx

    :return: строка со всем текстом документа
    """
    doc = Document(file_path)
    return '\n'.join(paragraph.text for paragraph in doc.paragraphs if paragraph.text)


def compare_response(model_response, correct_response):
    """
        Сравнивает два ответа - от модели и правильный ответ

        :param model_response: ответ, полученный от модели
        :param correct_response: эталонный правильный ответ

        :return: True, если ответы совпадают, иначе False
    """
    return model_response.replace('\n', '').replace(' ', '') == correct_response.replace('\n', '').replace(' ', '')


def func_tests():
    """
        Функция для проведения функционального тестирования нейросети.
        Тестирует модель на позитивных тест-кейсах.
    """
    i = 1

    print("\nФункциональное тестирование нейросети: \n")

    while True:
        pos_case_in_name = f"../data/pos_{i}_in.docx"
        pos_case_out_name = f"../data/pos_{i}_out.docx"

        if not os.path.isfile(pos_case_in_name):
            break  # Выход из цикла, если файл не существует

        text = read_docx(pos_case_in_name)
        model_response = func_tests_messages(text)

        correct_response = read_docx(pos_case_out_name)
        if compare_response(model_response, correct_response):
            print("pos_case_" + str(i) + ": " + Fore.GREEN + "SUCCESS" + Style.RESET_ALL)
        else:
            print("pos_case_" + str(i) + ": " + Fore.RED + "ERROR" + Style.RESET_ALL)
        i += 1  # Переходим к следующему файлу

    print("\nТестирование завершено!")

if __name__ == '__main__':
    try:
        # Запускаем функциональное тестирование
        func_tests()
    except Exception as e:
        # Обрабатываем возможные ошибки в процессе тестирования
        print(f"Ошибка обработки сообщения: {str(e)}")
