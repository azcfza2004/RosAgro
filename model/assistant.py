from docx import Document
import json
import os
import re

import printx
from yandex_cloud_ml_sdk import YCloudML

from glob import glob

message_1 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Север \nОтд7 пах с св 41/501\nОтд20 20/281 по пу 61/793\nОтд 3 пах подс.60/231\nПо пу 231\n\nДиск к. Сил отд 7. 32/352\nПу- 484\nДиск под Оз п езубов 20/281\nДиск под с. Св отд 10 83/203 пу-1065га"

#Пропускает 1 подкормку
message_2 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Восход\nПосев кук-24/252га\n24%\nПредпосевная культ\nПод кук-94/490га46%\nСЗРоз пш-103/557га\n 25% \n  Подкормка оз рапс- \n152га , 100%, подкормка овса-97га, 50%\nДовсходовое боронование подсолнечника-524\nга, 100%."
message_3 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: 23.10\nВнесение мин удобрений под оз пшеницу 2025 г ПУ Юг 216/7698\nОтд 17-216/1877"
message_4 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Пахота зяби под сою \nПо Пу 13/1464\nОтд 17 13/203\n\nДисков сах св\nПо Пу 36/1391\nОтд 16 25/25\nОтд 17 11/664\n\n2-е диск сах св под пш\nПо Пу 111/1288\nОтд 17 111/596\n\nВыравн зяби под сах св\nПо Пу 30/1395\nОтд 11 30/491"

#не распознает выравнивание зяби
message_5 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: ТСК \n Вырав-ие зяби под сою 187 га/ с нарастающим 740 га (13%) Остаток 5357 га\nОсадки 1 мм"

##не видит выравнивание зяби - пишет пахота
message_6 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: \n Вырав-ие зяби под сах/свёклу По ПУ 67/912 Отд 12 67/376"

##не видит выравнивание зяби - пишет пахота
message_7 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: ТСК \n Выравниваниеие зяби под сою 187 га/ с нарастающим 740 га (13%) Остаток 5357 га\nОсадки 1 мм"
#message_8

# Получение учетных данных из переменных окружения
#folder_id = os.environ["folder_id"]
#api_key = os.environ["api_key"]
# Инициализация SDK Яндекс.Облака
#sdk = YCloudML(folder_id=folder_id, auth=api_key)

sdk = YCloudML(folder_id="b1g6rjppcrrhq56lsqr0", auth="AQVNxTuU2_Efl4APdsHSsNBwMzOpuLziy4TeHEr2")

#яндекс 5 лайт рс
#model = (sdk.models.completions("gpt://b1g6rjppcrrhq56lsqr0/yandexgpt-lite/rc@tamrur7jqgegos3foh0dd"))

#LLama
model = (sdk.models.completions("gpt://b1g6rjppcrrhq56lsqr0/llama-lite/latest@tamrv6si2nqsg5ea5srge"))
#model = (sdk.models.completions("gpt://b1g6rjppcrrhq56lsqr0/llama-lite/latest@tamr074gv096dpj8fpg52"))
model = model.configure(temperature=0.1, max_tokens=3000)

def create_thread():
    return sdk.threads.create(ttl_days=1, expiration_policy="static")

def create_assistant(model, tools=None):
    kwargs = {}
    if tools and len(tools) > 0:
        kwargs = {"tools": tools}
    return sdk.assistants.create(
        model, ttl_days=1, expiration_policy="since_last_active", **kwargs
    )


def get_token_count(filename):
    with open(filename, "r", encoding="utf8") as f:
        return len(model.tokenize(f.read()))


def get_file_len(filename):
    with open(filename, encoding="utf-8") as f:
        return len(f.read())


def parse_messages_files(data_dir="messages"):
    files = []

    for filepath in glob(f"{data_dir}/*.docx", recursive=True):
        try:
            #print(f"Обработка файла: {filepath}")
            doc = Document(filepath)

            content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])

            filename = os.path.basename(filepath)

            parts = filename.split('_')
            user_name = parts[0]
            id = parts[1]
            date = parts[2].replace('.docx', '')

            files.append({
                "content": content,
                "user_name": user_name,
                "id": id,
                "date": date
            })

        except Exception as e:
            print(f"\nОшибка при обработке файла {filepath}: {str(e)}")
            continue

    return files

def clear_file(filename):
    with open(filename, 'w') as file:
        file.write('')

def process_data(data_str, message):
    key_names = ["Дата", "Подразделение", "Операция", "Культура", "За день, га", "С начала операции, га",
                 "Вал за день, ц", "Вал с начала, ц"]
    # Создаем директорию, если ее нет

    os.makedirs('processed_data', exist_ok=True)

    with open('processed_data/data.jsonl', 'a+', encoding='utf-8') as jsonl_file:
        data_lines = data_str.strip().split("\n")
        data_dict = {}
        data_dict["message"] = message
        jsonl_file.write(json.dumps(data_dict, ensure_ascii=False) + '\n')
        data_dict = {}

        for line in data_lines:
            line = line.strip()

            if not line and not data_dict:
                continue

            if line:
                if ": " in line:
                    parts = line.split(": ", 1)
                    key = parts[0].strip()
                    value = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ""
                    if key in key_names:
                        data_dict[key] = value
                elif line.endswith(":"):
                    data_dict[line[:-1].strip()] = ""
                else:
                    data_dict[line.strip()] = ""
            else:
                if data_dict:
                    jsonl_file.write(json.dumps(data_dict, ensure_ascii=False) + '\n')
                    data_dict = {}

        if data_dict:
            jsonl_file.write(json.dumps(data_dict, ensure_ascii=False) + '\n')

    #print(f"Обработка завершена. Данные сохранены в processed_data/data.jsonl")


def process_data_v2(data_str, message):
    key_names = ["Дата", "Подразделение", "Операция", "Культура", "За день, га", "С начала операции, га",
                 "Вал за день, ц", "Вал с начала, ц"]

    # Создаем директорию, если ее нет
    os.makedirs('processed_data', exist_ok=True)

    with open('processed_data/data.jsonl', 'a+', encoding='utf-8') as jsonl_file:
        data_lines = data_str.strip().split("\n")
        data_dict = {}
        data_dict["message"] = message

        # Сохраняем сообщение в файл
        jsonl_file.write(json.dumps(data_dict, ensure_ascii=False) + '\n')

        for line in data_lines:
            line = line.strip()
            if not line:
                continue

            # Разделяем строку по пробелам и двоеточиям
            pairs = line.split(" ")
            for i in range(0, len(pairs), 2):
                if i + 1 < len(pairs):  # Проверяем, чтобы не выйти за пределы списка
                    key = pairs[i].rstrip(':')  # Удаляем двоеточие в конце ключа
                    value = pairs[i + 1]
                    data_dict[key] = value

            # Записываем данные в файл, если они есть
            if data_dict:
                jsonl_file.write(json.dumps(data_dict, ensure_ascii=False) + '\n')
                data_dict = {}  # Очищаем словарь для следующей строки

    print(f"Обработка завершена. Данные сохранены в processed_data/data.jsonl")


# Основной скрипт
if __name__ == "__main__":

    thread = create_thread()
    assistant = create_assistant(model)

    assistant.update(
        instruction="""
        Ты — помощник агронома, который должен распределить информацию из собщения по группам, каждая группа выводится с новой строки: 
        Дата, 
        Подразделение, 
        Операция, 
        Культура, 
        За день га, 
        С начала операции га,
        Вал за день ц, 
        Вал с начала ц
        """
    )

    #files = parse_messages_files("messages")
    #for i in range(len(files)):
    #    print(files[i]['number_file'])
    #print(len(files))
    print("\nПробная попытка ассистента...")
    # Пример взаимодействия
    messages = [message_1, message_2, message_3, message_4, message_5, message_6, message_7]
    clear_file('processed_data/data.jsonl')


    files_data = parse_messages_files()
    #for i in range(len(files_data)):
    for i in range(len(files_data)):
          print(f'Пример {files_data[i]["id"]}  Выполнено: {i + 1}\n')
          thread = create_thread()
          thread.write(files_data[i]["content"])
          response = assistant.run(thread).wait()
          print(response.text)
          process_data(response.text, files_data[i]["content"])
          thread.delete()

    # for i in range(len(messages)):
    #       print(f'Пример {i + 1}\n')
    #       thread.write(messages[i])
    #       response = assistant.run(thread).wait()
    #       print(response.text)
    #       process_data(response.text, messages[i][71:])



    # thread.write(messages[0])
    # response = assistant.run(thread).wait()
    # print(response.text)
    # process_data(response.text, messages[0][71:])

    assistant.delete()
