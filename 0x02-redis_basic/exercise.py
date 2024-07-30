#!/usr/bin/env python3
""" test work with redis """
import redis
import uuid
from typing import Union, Callable


class Cache():
    """class cash redponsilbe for redis connect"""
    def __init__(self):
        """start redis instance from here"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: any) -> str:
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

    def get(self, key: str, fn:  Union[str, bytes, Callable, int, float, None]) -> Union[str, bytes, int, float, None]:
        """Check the type on fn from the dict then retrive convert"""
        value = self._redis.get(key)
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
