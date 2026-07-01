import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    #Rate limiter simplu in memorie, suficient pentru endpoint-uri de baza si testare

    def __init__(self, app, requests_per_window: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self._requests: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Identifica clientul dupa IP si endpoint
        client_ip = request.client.host if request.client else "unknown"
        key = (client_ip, request.url.path)
        # Inregistreaza timpul cererii si verifica daca depaseste limita
        now = time.time()
        window_start = now - self.window_seconds

        # Curata cererile vechi din coada
        queue = self._requests[key]
        while queue and queue[0] < window_start:
            queue.popleft()

        # Verifica daca depaseste limita
        if len(queue) >= self.requests_per_window:
            return JSONResponse(
                status_code=429,
                content={"detail": "Prea multe cereri. Încearcă din nou mai târziu."},
            )

        # Adauga cererea curenta in coada
        queue.append(now)
        response = await call_next(request)
        return response
