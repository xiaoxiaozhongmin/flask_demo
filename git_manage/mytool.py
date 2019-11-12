# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
import time

def threadPool_map(action,args,workers=100,chunksize=1):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = pool.map(action, args,chunksize=chunksize)
    return results

def decorate(fun):
    count = 0
    def wrapper(*args,**kwargs):
        nonlocal count
        start_time = time.time()
        data = fun(*args,**kwargs)
        stop_time = time.time()
        dt = stop_time - start_time
        count += 1
        print("被调用%d次，本次调用花费时间%f秒。"%(count,dt))
        return data
    return wrapper

def robust(actual_do):
    def add_robust(*args, **keyargs):
        try:
            return actual_do(*args, **keyargs)
        except Exception as e:
            print('Error execute: %s' % actual_do.__name__)
            print(e)
            return False
    return add_robust


def singleton(cls):
    _instance = {}
    def _singleton(*args, **kwargs):
        dataname=args[0]
        if dataname not in cls.databases:
            _instance[dataname] = cls(*args, **kwargs)
        return _instance[dataname]
    return _singleton
