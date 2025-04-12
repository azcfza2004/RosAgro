import requests
import json
import time
from datetime import datetime


class AgroModelTrainer:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def load_test_cases(self, file_path):
        """Загрузка тестовых данных из JSON-файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def send_training_request(self, messages):
        """Отправка запроса к API"""
        payload = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": messages,
            "temperature": 0.3  # Для более детерминированных ответов
        }

        try:
            response = requests.post(
                f"{self.base_url}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            return None

    def validate_response(self, response, expected):
        """Сравнение ответа с эталонным"""
        if not response or 'choices' not in response:
            return False, "Invalid API response"

        actual_content = response['choices'][0]['message']['content']

        try:
            # Пытаемся распарсить JSON если ответ структурированный
            actual_data = json.loads(actual_content)
            return actual_data == expected, ""
        except json.JSONDecodeError:
            # Для текстовых ответов
            return actual_content.strip() == str(expected).strip(), ""

    def train_on_dataset(self, test_cases, output_file="training_log.json"):
        """Основной цикл обучения"""
        results = []

        for case in test_cases:
            #print(f"\nProcessing test case {case.get('id', 'unknown')}")

            # Отправка запроса
            api_response = self.send_training_request(case['messages'])

            # Валидация
            is_valid, error_msg = self.validate_response(
                api_response,
                case['expected_response']
            )

            # Логирование
            result = {
                "test_case_id": case.get("id"),
                "timestamp": datetime.now().isoformat(),
                "success": is_valid,
                "error": error_msg if not is_valid else None,
                "expected": case['expected_response'],
                "actual": api_response['choices'][0]['message']['content'] if api_response else None
            }

            results.append(result)
            print(f"Result: {'SUCCESS' if is_valid else 'FAILED'} {error_msg}")

            # Задержка между запросами
            time.sleep(1)

        # Сохранение логов
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return results


# Конфигурация
CONFIG = {
    "api_key": "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImMzNWMyODBhLWUyYTYtNDdjOS1hNDI3LTgyODVkMTI3ZDIxYiIsImV4cCI6NDg5Nzk3NDk5Mn0.ZdllhvoIWoaZNAFTOVnf8CqC2-PRjo0QFvFGViGlScNUN4lN5w5uhBG0gDYYGQK3v6vm4QLXs_gbNoTJFGJOYg",
    "api_url": "https://api.intelligence.io.solutions/api/v1/chat/completions",
    "test_data_file": "training_data.json"
}

if __name__ == "__main__":
    trainer = AgroModelTrainer(CONFIG['api_key'], CONFIG['api_url'])

    # Загрузка тестовых данных
    test_cases = trainer.load_test_cases(CONFIG['test_data_file'])

    # Запуск обучения
    training_results = trainer.train_on_dataset(test_cases)

    # Статистика
    success_rate = sum(1 for r in training_results if r['success']) / len(training_results)
    print(f"\nTraining complete. Success rate: {success_rate:.1%}")