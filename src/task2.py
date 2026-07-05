"""Sliding Window rate limiter for chat message frequency control."""

import random
import time
from collections import deque


class SlidingWindowRateLimiter:
    """Rate limiter using the Sliding Window algorithm."""

    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_windows: dict = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Remove expired timestamps and delete user record if window is empty."""
        if user_id not in self.user_windows:
            return
        window = self.user_windows[user_id]
        while window and current_time - window[0] >= self.window_size:
            window.popleft()
        if not window:
            del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Return True if the user is allowed to send a message right now."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_windows:
            return True
        return len(self.user_windows[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """Record a message attempt. Returns True if allowed, False if rate-limited."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_windows:
            self.user_windows[user_id] = deque()
        if len(self.user_windows[user_id]) < self.max_requests:
            self.user_windows[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """Return seconds until the user can send the next message."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_windows:
            return 0.0
        if len(self.user_windows[user_id]) < self.max_requests:
            return 0.0
        oldest = self.user_windows[user_id][0]
        return max(0.0, self.window_size - (current_time - oldest))


def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
