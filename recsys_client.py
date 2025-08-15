import requests
from typing import Optional, Dict, Any, List
from os import getenv
from dotenv import load_dotenv

load_dotenv()
RECSYS_SERVER_HOST = getenv("RECSYS_SERVER_HOST", "recsys")
RECSYS_SERVER_PORT = getenv("RECSYS_SERVER_PORT", "8000")

class RecSysClient:
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            base_url = f"http://{RECSYS_SERVER_HOST}:{RECSYS_SERVER_PORT}"
        self.base_url = base_url

    def get_recommendation(self, user_id: str, excluded: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Получить рекомендацию пользователя через эндпоинт /recommend/{user_id}.

        Аргументы:
            user_id: ID пользователя (строка)
            excluded: список ID пользователей (строки), которых нужно исключить

        Возвращает:
            tg_id рекомендованного пользователя или None
        """
        params = {}
        if excluded:
            params["excluded"] = ",".join(excluded)
        url = f"{self.base_url}/recommend/{user_id}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("recommendation")
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения с сервером рекомендаций: {e}")
            print("Проверьте, что сервер рекомендаций запущен и доступен по адресу "
                  f"{self.base_url}.")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"HTTP ошибка при получении рекомендации: {e}")
            return None
        except Exception as e:
            print(f"Неизвестная ошибка при получении рекомендации: {e}")
            return None

# Пример использования
if __name__ == "__main__":
    client = RecSysClient()
    user_id = "1008114047"  # замените на нужный ID пользователя
    excluded = ["2"]  # список ID, которых нужно исключить
    recommendation = client.get_recommendation(user_id, excluded)
    # Получаем информацию о пользователе по user_id
    print("Рекомендация:", recommendation)
