import os
import printx
from yandex_cloud_ml_sdk import YCloudML

from glob import glob
from tqdm.auto import tqdm
import pandas as pd

from yandex_cloud_ml_sdk.search_indexes import (
    StaticIndexChunkingStrategy,
    HybridSearchIndexType,
    ReciprocalRankFusionIndexCombinationStrategy,
)

message_1 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Север \nОтд7 пах с св 41/501\nОтд20 20/281 по пу 61/793\nОтд 3 пах подс.60/231\nПо пу 231\n\nДиск к. Сил отд 7. 32/352\nПу- 484\nДиск под Оз п езубов 20/281\nДиск под с. Св отд 10 83/203 пу-1065га"
message_2 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: Восход\nПосев кук-24/252га\n24%\nПредпосевная культ\nПод кук-94/490га46%\nСЗРоз пш-103/557га\n25%\nПодкормка оз рапс-\n152га , 100%, подкормка овса-97га, 50%\nДовсходовое боронование подсолнечника-524\nга, 100%."
message_3 = "Проанализируй сообщение и распредели по группам\n Вот пример сообщения: 23.10\nВнесение мин удобрений под оз пшеницу 2025 г ПУ Юг 216/7698\nОтд 17-216/1877"

#Пропускает 1 подкормку
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

#model = sdk.models.completions('yandexgpt')
###
#яндекс 5 лайт рс
#model = (sdk.models.completions("gpt://b1g6rjppcrrhq56lsqr0/yandexgpt-lite/rc@tamrur7jqgegos3foh0dd"))

#LLama
model = (sdk.models.completions("gpt://b1g6rjppcrrhq56lsqr0/llama-lite/latest@tamrv6si2nqsg5ea5srge"))
model = model.configure(temperature=0.5, max_tokens=3000)

def create_thread():
    return sdk.threads.create(ttl_days=1, expiration_policy="static")

def create_assistant(model, tools=None):
    kwargs = {}
    if tools and len(tools) > 0:
        kwargs = {"tools": tools}
    return sdk.assistants.create(
        model, ttl_days=1, expiration_policy="since_last_active", **kwargs
    )

# Создаем простого ассистента и беседу:
# thread = create_thread()
# assistant = create_assistant(model)


def get_token_count(filename):
    with open(filename, "r", encoding="utf8") as f:
        return len(model.tokenize(f.read()))


def get_file_len(filename):
    with open(filename, encoding="utf-8") as f:
        return len(f.read())


# Основной скрипт
if __name__ == "__main__":

    thread = create_thread()
    assistant = create_assistant(model)

    assistant.update(
        instruction="""Ты — помощник агронома, который должен распределить информацию из собщения по группам: Дата, Подразделение, Операция, Культура, За день га, С начала операции га,Вал за день ц, Вал с начала ц"""
    )

    print("\nПробная попытка ассистента...")
    # Пример взаимодействия
    thread = create_thread()
    messages = [message_1, message_2, message_3, message_4, message_5, message_6, message_7]
    for i in range(len(messages)):
       print(f'Пример {(i + 1)}\n')
       thread.write(messages[i])
       response = assistant.run(thread).wait()
       print(response.text)

    #thread.write(message_1)
    #response = assistant.run(thread).wait()
    #print(response.text)

    # messages = [
    #     {"role": "system",
    #      "text": "Ты — помощник агронома, который должен распределить информацию из собщения по группам: Дата, Подразделение, Операция, Культура, За день га, С начала операции га,Вал за день ц, Вал с начала ц"},
    #     {"role": "user", "text": message_1},
    #     {"role": "user", "text": "посему ты так думаешь?"}
    # ]
    #
    # print("\nПробная попытка чистой модели...")
    # result = model.run(messages)
    #
    # print(result.text)

    thread.delete()
    assistant.delete()
