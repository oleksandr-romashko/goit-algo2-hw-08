"""LRU cache optimization for range sum queries on a large array."""

import random
import time
from collections import OrderedDict


class LRUCache:
    """LRU cache with get/put interface. Returns -1 on cache miss."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


def range_sum_no_cache(arr, left, right):
    """Return sum of array[left:right+1] without caching."""
    return sum(arr[left:right + 1])


def update_no_cache(arr, index, value):
    """Set array[index] = value without caching."""
    arr[index] = value


lru_cache = LRUCache(capacity=1000)


def range_sum_with_cache(arr, left, right):
    """Return sum of array[left:right+1], using cache to avoid recomputation."""
    key = (left, right)
    result = lru_cache.get(key)
    if result == -1:
        result = sum(arr[left:right + 1])
        lru_cache.put(key, result)
    return result


def update_with_cache(arr, index, value):
    """Set array[index] = value and invalidate all cache entries covering index."""
    arr[index] = value
    to_delete = [k for k in list(lru_cache.cache) if k[0] <= index <= k[1]]
    for k in to_delete:
        del lru_cache.cache[k]


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    """Generate a mixed query list."""
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


if __name__ == "__main__":
    N = 100_000
    Q = 50_000

    arr = [random.randint(1, 100) for _ in range(N)]
    queries = make_queries(N, Q)

    arr1 = arr[:]
    start = time.time()
    for q in queries:
        if q[0] == "Range":
            range_sum_no_cache(arr1, q[1], q[2])
        else:
            update_no_cache(arr1, q[1], q[2])
    t_no_cache = time.time() - start

    arr2 = arr[:]
    lru_cache.cache.clear()
    start = time.time()
    for q in queries:
        if q[0] == "Range":
            range_sum_with_cache(arr2, q[1], q[2])
        else:
            update_with_cache(arr2, q[1], q[2])
    t_with_cache = time.time() - start

    print(f"Без кешу :  {t_no_cache:.2f} с")
    print(f"LRU-кеш  :  {t_with_cache:.2f} с  (прискорення x{t_no_cache / t_with_cache:.1f})")
