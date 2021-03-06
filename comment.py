# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: comment.py
# Time: 8月 20, 2021
import requests
from user_agent import generate_user_agent
from random import randint
from time import sleep
from json import loads, dumps, dump
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


# 公共请求函数
def pub_req(**kwargs):
    method = kwargs.get("method", "GET")
    url = kwargs.get("url", "")
    params = kwargs.get("params", {})
    data = kwargs.get("data", {})
    headers = {"User-Agent": generate_user_agent()} | kwargs.get("headers", {})
    proxy = kwargs.get("proxy", {})
    timeout = kwargs.get("timeout", 20)
    try:
        with requests.Session() as client:
            with client.request(method=method, url=url, params=params, data=data, headers=headers, proxies=proxy,
                                timeout=timeout) as rs:
                if rs.status_code == 200 or 201:
                    return rs.content
                else:
                    sleep(randint(1, 2))
                    retry = kwargs.get("retry", 0)
                    retry += 1
                    if retry >= 2:
                        return None
                    kwargs["retry"] = retry
                    return pub_req(**kwargs)
    except Exception as e:
        print(e)
        sleep(randint(1, 2))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 2:
            return None
        kwargs["retry"] = retry
        return pub_req(**kwargs)


# 网易严选搜索
def net_ease_search(key="T恤", page=1, size=40, sort_type=0):
    meta = {
        "url": "https://you.163.com/xhr/search/search.json",
        "params": {
            "page": page,
            "sortType": sort_type,
            "categoryId": "0",
            "descSorted": "true",
            "matchType": "1",
            "floorPrice": "-1",
            "upperPrice": "-1",
            "stillSearch": "false",
            "searchWordSource": "1",
            "size": size,
            "keyword": key,
            "needPopWindow": "false"
        }
    }
    result = pub_req(**meta)
    try:
        if result:
            result = loads(result.decode())
            pages = result["data"]["directly"]["searcherResult"]["pagination"]["totalPage"]
            # print(pages)
            id_list = [r["id"] for r in result["data"]["directly"]["searcherResult"]["result"]]
            return id_list
    except Exception as e:
        print("net_ease_search", e)


# 网易严选-商品评价
def net_ease_comment(item_id="4000070", page=1, size=30, order_by=0):
    meta = {
        "url": "https://you.163.com/xhr/comment/listByItemByTag.json",
        "params": {
            "itemId": item_id,
            "tag": "全部",
            "size": size,
            "page": page,
            "orderBy": order_by,
            "oldItemTag": "全部",
            "oldItemOrderBy": "0",
            "tagChanged": "0"
        },
    }
    res = pub_req(**meta)
    if not res: return None
    try:
        result = loads(res.decode())
        # print(result)
        return result
    except Exception as e:
        print("net_ease_comment", e)


# 网易严选-评论区图片下载
def mul_get(key="", item_id="4000070"):
    result = net_ease_comment(item_id=item_id)
    pages = result["data"]["pagination"]["totalPage"]
    if pages > 1:
        workers = 32 if pages > 32 else pages
        with ThreadPoolExecutor(workers - 1) as executor:
            future_list = [executor.submit(net_ease_comment, item_id=item_id, page=p) for
                           p in range(2, pages + 1)]
        result_list = result["data"]["commentList"]
        for r in as_completed(future_list):
            result = r.result()
            result_list += result["data"]["commentList"]
        # print(result_list)
        # print(len(result_list))
        pic_list = []
        for x in result_list:
            if x.get("picList", ""):
                pic_list += x["picList"]
        if not pic_list: return None
        print(pic_list)
        print(len(pic_list))
        workers = 32 if len(pic_list) > 32 else len(pic_list)
        with ThreadPoolExecutor(workers) as executor:
            future_list = {executor.submit(pub_req, **{"url": url}): url for
                           url in pic_list}
        os.makedirs(f'imgs/{key}/{item_id}', exist_ok=True)
        for r in as_completed(future_list):
            if r.result():
                with open(f'imgs/{key}/{item_id}/{future_list[r].split("?")[0].split("/")[-1]}', 'wb') as f:
                    f.write(r.result())
        return result_list
    else:
        return result["data"]["commentList"]


# 小米有品-搜索
def mi_you_pin_search(key="T恤", page=1, size=40, sort_type=0):
    meta = {
        "method": "POST",
        "url": "https://www.xiaomiyoupin.com/mtop/market/search/v2/doSearch",
        "data": dumps([{}, {"query": [{"queryName": key, "queryType": 0, "rule": []}], "sortBy": sort_type, "pageIdx": page,
                            "strategyInfo": None, "filter": None,
                            "baseParam": {"imei": "", "clientVersion": "", "ypClient": 3}, "source": "searchPage",
                            "requestId": "", "clientPageId": "", "recentAddress": None,
                            "requestExtraInfo": {}, "pageSize": size}]),
        "headers": {
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json"
        }
    }
    result = pub_req(**meta)
    print(result.decode())
    try:
        if result:
            result = loads(result.decode())
            total = result["data"]["total"]
            # print(total)
            return result
    except Exception as e:
        print(mi_you_pin_search, e)


# 小米有品-商品评价
def mi_you_pin_comment(item_id="129064", page=1, size=10):
    meta = {
        "method": "POST",
        "url": "https://www.xiaomiyoupin.com/mtop/market/comment/product/content",
        "data": dumps({"gid": item_id,
                       "folding": False,
                       "source": "PC",
                       "tag_name": "全部",
                       "tag_id": "__all__",
                       "psize": size,
                       "pindex": page,
                       "pids": [],
                       "session_id": ""
                       }),
        "headers": {
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br"
        }
    }
    res = pub_req(**meta)
    if not res: return None
    try:
        print(res.decode())
        result = loads(res.decode())
        return result
    except Exception as e:
        print("mi_you_pin_comment", e)


if __name__ == '__main__':
    key = "T恤"
    # 网易严选
    # id_list = net_ease_search(key=key, size=500)
    # for item_id in id_list:
    #     mul_get(key, item_id)

    # 小米有品
    # mi_you_pin_search(key)
    mi_you_pin_comment()
