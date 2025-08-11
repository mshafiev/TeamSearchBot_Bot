import requests
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class OlympsData:
    """Модель данных для олимпиады"""
    name: str
    profile: str
    level: int  # 1,2,3, 0-не реш
    user_tg_id: str
    result: int  # 0-победитель, 1-призер, 2-финалист, 3-участник
    year: str
    is_approved: Optional[bool] = False
    is_displayed: Optional[bool] = False


@dataclass
class UserData:
    """Модель данных для пользователя"""
    tg_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    phone_verified: Optional[bool] = False
    age: Optional[int] = None
    city: Optional[str] = None
    status: Optional[int] = None  # 0-свободен / 1-в отношениях
    goal: Optional[int] = None  # 0-совместный бот, 1-общение, 2-поиск команды, 3-отношения
    who_interested: Optional[int] = None  # 0-ж / 1-м / 2-все
    date_of_birth: Optional[str] = None  # ДД-ММ-ГГГГ
    face_photo_id: Optional[str] = None
    photo_id: Optional[str] = None
    description: Optional[str] = None
    gender: Optional[bool] = None # 0m 1g


@dataclass
class LikeData:
    """Модель данных для лайка"""
    from_user_tg_id: str
    to_user_tg_id: str
    is_like: bool
    text: Optional[str] = None
    is_readed: Optional[bool] = False


class APIClient:
    """Клиент для работы с API сервиса"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL сервиса
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE, PATCH)
            endpoint: Эндпоинт API
            data: Данные для отправки
            params: Параметры запроса
            
        Returns:
            Ответ от сервера
            
        Raises:
            requests.RequestException: При ошибке запроса
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, params=params)
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса к API: {e}")
    
    # ==================== ОЛИМПИАДЫ ====================
    
    def get_user_olymps(self, user_tg_id: str) -> List[Dict[str, Any]]:
        """
        Получить все олимпиады пользователя
        
        Args:
            user_tg_id: Telegram ID пользователя
            
        Returns:
            Список олимпиад пользователя
        """
        return self._make_request("GET", f"/olymp/{user_tg_id}")
    
    def create_olymp(self, olymp_data: OlympsData) -> Dict[str, Any]:
        """
        Создать новую запись олимпиады
        
        Args:
            olymp_data: Данные олимпиады
            
        Returns:
            Созданная запись олимпиады
        """
        data = {
            "name": olymp_data.name,
            "profile": olymp_data.profile,
            "level": olymp_data.level,
            "user_tg_id": olymp_data.user_tg_id,
            "result": olymp_data.result,
            "year": olymp_data.year,
            "is_approved": olymp_data.is_approved,
            "is_displayed": olymp_data.is_displayed
        }
        return self._make_request("POST", "/olymp/create/", data=data)
    
    def set_olymp_display(self, olymp_id: int) -> Dict[str, Any]:
        """
        Установить флаг отображения олимпиады (is_displayed)

        Args:
            olymp_id: ID олимпиады

        Returns:
            Обновлённая запись олимпиады
        """
        return self._make_request("POST", f"/olymp/set_display/?olymp_id={olymp_id}")

    def delete_olymp(self, olymp_id: int) -> Dict[str, Any]:
        """
        Удалить олимпиаду по ID
        
        Args:
            olymp_id: ID олимпиады
            
        Returns:
            Сообщение об успешном удалении
        """
        return self._make_request("DELETE", f"/olymp/delete/{olymp_id}")
    
    # ==================== ПОЛЬЗОВАТЕЛИ ====================
    
    def create_user(self, tg_id: str) -> Dict[str, Any]:
        """
        Создать нового пользователя
        
        Args:
            tg_id: Telegram ID пользователя
            
        Returns:
            Статус создания пользователя
        """
        return self._make_request("POST", f"/user/create/?tg_id={tg_id}")
    
    def get_user(self, tg_id: str) -> Dict[str, Any]:
        """
        Получить пользователя по tg_id
        
        Args:
            tg_id: Telegram ID пользователя
            
        Returns:
            Данные пользователя
        """
        return self._make_request("GET", f"/user/get/{tg_id}")
    
    def update_user(self, user_data: UserData) -> Dict[str, Any]:
        """
        Обновить данные пользователя
        
        Args:
            user_data: Данные пользователя для обновления
            
        Returns:
            Обновлённые данные пользователя
        """
        data = {k: v for k, v in user_data.__dict__.items() if v is not None}
        return self._make_request("PUT", "/user/update/", data=data)
    
    def delete_user(self, tg_id: str) -> Dict[str, Any]:
        """
        Удалить пользователя по tg_id
        
        Args:
            tg_id: Telegram ID пользователя
            
        Returns:
            Сообщение об успешном удалении
        """
        return self._make_request("DELETE", f"/user/delete/{tg_id}")
    
    # ==================== ЛАЙКИ ====================
    
    def create_like(self, like_data: LikeData) -> Dict[str, Any]:
        """
        Создать новый лайк
        
        Args:
            like_data: Данные лайка
            
        Returns:
            Созданная запись лайка
        """
        data = {
            "from_user_tg_id": like_data.from_user_tg_id,
            "to_user_tg_id": like_data.to_user_tg_id,
            "text": like_data.text,
            "is_like": like_data.is_like,
            "is_readed": like_data.is_readed
        }
        return self._make_request("POST", "/like/create/", data=data)
    
    def delete_like(self, like_id: int) -> Dict[str, Any]:
        """
        Удалить лайк по ID
        
        Args:
            like_id: ID лайка
            
        Returns:
            Сообщение об успешном удалении
        """
        return self._make_request("DELETE", "/like/delete/", params={"id": like_id})
    
    def set_like_readed(self, from_user_tg_id: str, to_user_tg_id: str) -> Dict[str, Any]:
        """
        Изменить статус "прочитано" у лайка
        
        Args:
            from_user_tg_id: Telegram ID пользователя, который поставил лайк
            to_user_tg_id: Telegram ID пользователя, которому поставлен лайк
            
        Returns:
            Обновленная запись лайка
        """
        params = {
            "from_user_tg_id": from_user_tg_id,
            "to_user_tg_id": to_user_tg_id
        }
        return self._make_request("PATCH", "/like/set_read/", params=params)
    
    def get_last_likes(self, user_tg_id: str, count: int) -> List[Dict[str, Any]]:
        """
        Получить последние X лайков пользователя
        
        Args:
            user_tg_id: Telegram ID пользователя, для которого ищем лайки
            count: Количество последних лайков для возврата
            
        Returns:
            Список последних лайков
        """
        params = {
            "user_tg_id": user_tg_id,
            "count": count
        }
        return self._make_request("GET", "/like/get_last/", params=params)
    
    def like_exists(self, from_user_tg_id: str, to_user_tg_id: str, is_like: bool = True) -> Dict[str, Any]:
        """
        Проверить, существует ли лайк между пользователями

        Args:
            from_user_tg_id: кто поставил лайк
            to_user_tg_id: кому поставили лайк
            is_like: True для лайка, False для дизлайка
        Returns:
            {"exists": bool}
        """
        params = {
            "from_user_tg_id": from_user_tg_id,
            "to_user_tg_id": to_user_tg_id,
            "is_like": is_like
        }
        return self._make_request("GET", "/like/exists/", params=params)
    
    def get_incoming_likes(self, user_tg_id: str, only_unread: bool = True, count: int = 50) -> List[Dict[str, Any]]:
        params = {"user_tg_id": user_tg_id, "only_unread": only_unread, "count": count}
        return self._make_request("GET", "/like/get_incoming/", params=params)
    
    # ==================== ТЕСТОВЫЙ ЭНДПОИНТ ====================
    
    def test_endpoint(self, test_value: int) -> int:
        """
        Тестовый эндпоинт
        
        Args:
            test_value: Тестовое значение
            
        Returns:
            Переданное значение
        """
        return self._make_request("GET", f"/test/{test_value}")


from os import getenv
from dotenv import load_dotenv
load_dotenv()
DB_SERVER_HOST = getenv("DB_SERVER_HOST")
DB_SERVER_PORT = getenv("DB_SERVER_PORT")

client = APIClient(f"http://{DB_SERVER_HOST}:{DB_SERVER_PORT}")


# Примеры использования
if __name__ == "__main__":
    try:
        result = client.create_olymp(OlympsData(
            user_tg_id="1008114047",
            name = "Всероссийская междисциплинарная олимпиада школьников 8-11 класса «Национальная технологическая олимпиада»",
            profile = "виртуальные миры: разработка компьютерных игр, технологии виртуальной реальности, технологии дополненной реальности",
            level = 3,
            result = 1,
            year = "2025",
            is_approved = True,
            is_displayed = False
        ))
        print(result)
    except Exception as e:
        print(e)
    
    # try:
    #     result = client.get_user(tg_id="1008114047")
    #     print(result)
    # except Exception as e:
    #     print(e)
        
    # client.update_user(
    #         UserData(
    #             tg_id="1008114047",
    #             photo_id="test",
    #         )
    #     )
        
    

