import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

API_URL = "https://xn--80aafeyru5a.xn--p1ai/api/v2/client/search/"

# Создаем сессию с retry/backoff

def create_session():
    session = requests.Session()

    # Заголовки и куки из DevTools
    session.headers.update({
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36"
        )
    })
    session.cookies.update({
        "PHPSESSID": "7b95f80cac497b764539e18f3b6451c0",
    })

    # Настройка retry с экспоненциальной задержкой по статусам и соединению
    retries = Retry(
        total=5,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session

# Глобальная сессия
_session = create_session()


def get_top(brand: str, article: str) -> str:
    """
    Возвращает имя провайдера первого (наилучшего) предложения.
    При тайм-ауте или ошибке несколько раз повторяет попытку.
    """
    params = {
        "article": article,
        "brand": brand,
        "withAnalogs": "1",
    }

    # ручные retry на случай ReadTimeout
    for attempt in range(3):
        try:
            resp = _session.get(API_URL, params=params, timeout=15)
            resp.raise_for_status()
            break
        except requests.exceptions.ReadTimeout as e:
            if attempt < 2:
                time.sleep(2 ** attempt)  # экспоненциальная задержка: 1s, 2s, ...
                continue
            print(f"[WARN] ReadTimeout для {brand}/{article} после {attempt+1} попыток: {e}")
            return ""
        except requests.RequestException as e:
            print(f"[WARN] Ошибка запроса для {brand}/{article}: {e}")
            return ""

    data = resp.json()

    # извлекаем список bestOffers
    best_offers = data.get("bestOffers") or data.get("data", {}).get("bestOffers", [])
    if not best_offers:
        return ""

    # Первое предложение
    offer = best_offers[0]
    provider_name = offer.get("providerName", "")
    return provider_name
