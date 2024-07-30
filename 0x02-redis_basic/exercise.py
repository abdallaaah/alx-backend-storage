#!/usr/bin/env python3
""" test work with redis """
import redis
import uuid


class Cache():
    """class cash redponsilbe for redis connect"""
    def __init__(self):
        """start redis instance from here"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, value: any) -> str:
        """stroe redis value in uuid and return uuid"""
        key = str(uuid.uuid4())
        self._redis.set(key, value)
        return key
