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
    def wrapper(self: Any, *args, **kwags):
        self._redis.rpush(f'{method.__qualname__}:inputs', str(args))
        key = method(self, *args, **kwags)
        self._redis.rpush(f"{method.__qualname__}:outputs", key)
        return key
    return wrapper


def replay(fn: Callable) -> None:
    '''Displays the call history of a Cache class' method.
    '''
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


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
