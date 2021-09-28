# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: 秒杀商品(令牌).py
# Time: 9月 28, 2021
from fastapi import FastAPI, Header, Cookie, Depends, BackgroundTasks
from starlette.requests import Request
from boltons.cacheutils import LRI, LRU
from hashlib import md5

lri_cache = LRI()
lru_cache = LRU()

app = FastAPI()


# 秒杀商品发布
@app.get("/t1")
async def test1(request: Request):
    num = 10
    key = "123456"
    global lri_cache
    lri_cache = LRI(max_size=num)
    for n in range(num):
        token = md5(f'{key}{n}'.encode()).hexdigest()
        lri_cache[token] = key
    print(dict(lri_cache))
    return {"msg": "t1"}


# 秒杀
@app.get("/t2")
async def test2(request: Request):
    if lri_cache.keys():
        token = list(lri_cache.keys()).pop()
        good_id = lri_cache.pop(token)
        return token
    else:
        return {"msg": None}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
