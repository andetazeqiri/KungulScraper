from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HttpClient:
    def __init__(
        self,
        user_agent: str = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
                "sec-ch-ua": '"Chromium";v="121", "Not A(Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "macOS",
            }
        )

    def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        json_body: Optional[Dict] = None,
    ) -> requests.Response:
        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=20,
        )
        response.raise_for_status()
        return response
