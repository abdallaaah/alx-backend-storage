#!/usr/bin/env python3
""" test work with redis """
import redis
import uuid
from typing import Union, Callable, Optional, Any
from functools import wraps


def count_calls(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self: Any, *args, **kwargs):
        """wrapper func"""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self: Any, *args):
        self._redis.rpush(f'{method.__qualname__}:inputs', str(args))
        key = method(self, str(args))
        self._redis.rpush(f"{method.__qualname__}:outputs", key)
        return key
    return wrapper


class Cache():
    """class cash redponsilbe for redis connect"""
    def __init__(self):
        """start redis instance from here"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data:  Union[str, bytes, int, float]) -> str:
        """store redis value in uuid and return uuid"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get_int(self, value: int) -> int:
        """Convert into int ant return it"""
        x = int(value)
        return x

    def get_str(self, value: str) -> str:
        """Convert to string and return it"""
        x = str(value)
        return x

    @call_history
    def get(self, key: str, fn:  Optional[Callable] = None) -> Any:
        """Check the type on fn from the dict then retrive convert"""
        value = self._redis.get(key)
        if value is None:
            return
        if fn == int:
            x = self.get_int(value)
            return x
        if fn == str:
            x = self.get_str(value)
            return x
        if callable(fn):
            return fn(value)
        if fn is None:
            return value

    def replay(fn: Callable) -> None:
        """ Check redis for how many times a function was called and display:
                - How many times it was called
                - Function args and output for each call
        """
        client = redis.Redis()
        calls = client.get(fn.__qualname__).decode('utf-8')
        inputs = [input.decode('utf-8') for input in
                  client.lrange(f'{fn.__qualname__}:inputs', 0, -1)]
        outputs = [output.decode('utf-8') for output in
                   client.lrange(f'{fn.__qualname__}:outputs', 0, -1)]
        print(f'{fn.__qualname__} was called {calls} times:')
        for input, output in zip(inputs, outputs):
            print(f'{fn.__qualname__}(*{input}) -> {output}')
