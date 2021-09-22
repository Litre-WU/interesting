# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: qq_music.py
# Time: 9月 18, 2021
from requests import Session
from user_agent import generate_user_agent
from random import randint
from time import time, sleep
from lxml import etree
from json import dumps, loads
from moviepy.editor import AudioFileClip
from loguru import logger
import os
from concurrent import futures

logger.add(f'{os.path.basename(__file__)[:-3]}.log', rotation='200 MB', compression='zip', enqueue=True,
           serialize=False, encoding='utf-8', retention='7 days')


# 公共请求函数
def pub_req(**kwargs):
    method = kwargs.get("method", "GET")
    url = kwargs.get("url", "")
    params = kwargs.get("params", {})
    data = kwargs.get("data", {})
    headers = {"User-Agent": generate_user_agent()} | kwargs.get("headers", {})
    proxy = kwargs.get("proxy", {})
    timeout = kwargs.get("timeout", 10)
    try:
        with Session() as client:
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
        logger.info(f'{pub_req} {e}')
        sleep(randint(1, 2))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 2:
            return None
        kwargs["retry"] = retry
        return pub_req(**kwargs)


# QQ音乐搜索
def search_music(**kwargs):
    # meta = {
    #     "url": "https://c.y.qq.com/soso/fcgi-bin/client_search_cp",
    #     "params": {"ct": "24", "qqmusic_ver": "1298", "new_json": "1", "remoteplace": "txt.yqq.top", "searchid": "",
    #                "t": "0", "aggr": "1", "cr": "1", "catZhida": "1", "lossless": "0", "flag_qc": "0", "p": "1",
    #                "n": "10", "w": kwargs.get("keyword", "告白气球"), "_": str(int(time() * 1000)),
    #                "cv": "", "format": "json", "inCharset": "utf-8", "outCharset": "utf-8", "notice": "0",
    #                "platform": "yqq.json", "needNewCode": "0", "uin": kwargs.get("qq", "7475349744"),
    #                "g_tk_new_20200303": "", "g_tk": "", "hostUin": "0", "loginUin": kwargs.get("qq", "7475349744")
    #                }
    # }
    meta = {
        "method": "POST",
        "url": "https://u.y.qq.com/cgi-bin/musicu.fcg",
        "data": dumps({"comm": {"uin": "", "authst": "", "mina": 1, "appid": "", "ct": 25},
                       "req": {"method": "DoSearchForQQMusicMobile", "module": "music.search.SearchBrokerCgiServer",
                               "param": {"remoteplace": "miniapp.wxada7aab80ba27074", "searchid": "", "search_type": 0,
                                         "query": kwargs.get("keyword", "告白气球").encode().decode("unicode_escape"),
                                         "page_num": kwargs.get("page", 1), "num_per_page": kwargs.get("size", 20),
                                         "grp": 0}}}),
        "headers": {
            "Accept-Encoding": "gzip, deflate, br"
        }
    }
    res = pub_req(**meta)
    if not res: return None
    # print(res.decode())
    res = loads(res.decode())
    return res


# 音乐试听
def music_trial(**kwargs):
    songId = kwargs.get("songId", "")
    if not songId: return None
    meta = {
        "method": "POST",
        "url": "https://u.y.qq.com/cgi-bin/musicu.fcg",
        "data": dumps({"comm": {"uin": "",
                                "authst": "",
                                "mina": 1, "appid": "", "ct": 25},
                       "midReq": {"module": "track_info.UniformRuleCtrlServer", "method": "GetTrackInfo",
                                  "param": {"mids": [songId], "types": [0], "singer_pmid": 1}},
                       "urlReq0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey",
                                   "param": {"guid": "7475349744", "songmid": [songId], "songtype": [0],
                                             "filename": [], "uin": "", "loginflag": 1,
                                             "platform": "23", "h5to": "speed"}}}),
        "headers": {
            "Accept-Encoding": "gzip, deflate, br"
        }
    }
    res = pub_req(**meta)
    if not res: return None
    # print(res.decode())
    res = loads(res.decode())
    purl = f'{res["urlReq0"]["data"]["sip"][0]}{res["urlReq0"]["data"]["midurlinfo"][0]["purl"]}' if \
        res["urlReq0"]["data"]["midurlinfo"][0]["purl"] else ""
    # print(purl)
    return {"purl": purl}


# 搜索MV
def search_music_movie(**kwargs):
    meta = {
        "url": "https://shc.y.qq.com/soso/fcgi-bin/search_for_qq_cp",
        "params": {
            "_": str(int(time() * 1000)),
            "g_tk": "5381",
            "uin": "",
            "format": "json",
            "inCharset": "utf-8",
            "outCharset": "utf-8",
            "notice": "0",
            "platform": "h5",
            "needNewCode": "1",
            "w": kwargs.get("keyword", "告白气球"),
            "zhidaqu": "1",
            "catZhida": "1",
            "t": "0",
            "flag": "1",
            "ie": "utf-8",
            "sem": "1",
            "aggr": "0",
            "perpage": "20",
            "n": "20",
            "p": "1",
            "remoteplace": "txt.mqq.all"
        },
        "headers": {
            "referer": "http://y.qq.com/"
        }
    }
    res = pub_req(**meta)
    print(res.decode())


# MV
def music_video(**kwargs):
    vid = kwargs.get("vid", "")
    if not vid: return None
    meta = {
        "method": "POST",
        "url": "https://u.y.qq.com/cgi-bin/musicu.fcg",
        "data": dumps({"comm": {"ct": 6, "cv": 0, "g_tk": 5381, "uin": 0, "format": "json", "platform": "yqq"},
                       "mvInfo": {"module": "video.VideoDataServer", "method": "get_video_info_batch",
                                  "param": {"vidlist": [vid],
                                            "required": ["vid", "type", "sid", "cover_pic", "duration", "singers",
                                                         "new_switch_str", "video_pay", "hint", "code", "msg", "name",
                                                         "desc",
                                                         "playcnt", "pubdate", "isfav", "fileid", "filesize", "pay",
                                                         "pay_info", "uploader_headurl", "uploader_nick",
                                                         "uploader_uin",
                                                         "uploader_encuin"]}},
                       "mvUrl": {"module": "music.stream.MvUrlProxy", "method": "GetMvUrls",
                                 "param": {"vids": [vid], "request_type": 10003, "addrtype": 3, "format": 264}}}),
        "headers": {
            "referer": "http://y.qq.com/"
        }
    }
    res = pub_req(**meta)
    # print(res.decode())
    res = loads(res.decode())
    filetypeDict = {10: "360P", 20: "480P", 30: "720P", 40: "1080P"}
    video_list = {filetypeDict[m["filetype"]]: m["freeflow_url"][0] for m in res["mvUrl"]["data"][vid]["mp4"] if
                  m["freeflow_url"]}
    print(video_list)
    return {"cover": res["mvInfo"]["data"][vid]["cover_pic"], "mv": video_list}


def movie2music(url, name):
    res = pub_req(**{"url": url})
    os.makedirs('files', exist_ok=True)
    if os.path.exists(f'files/{name}.mp3'):return True
    with open(f'files/{name}.mp4', 'wb') as f:
        f.write(res)
    AudioFileClip(f'files/{name}.mp4').write_audiofile(f'files/{name}.mp3')
    AudioFileClip(f'files/{name}.mp4').write_audiofile(f'files/{name}.wav')
    os.remove(f'files/{name}.mp4')
    return True


def search(**kwargs):
    res = search_music(**{"keyword": kwargs.get("keyword", "告白气球")})
    data_list = [
        {"id": r["mid"], "vid": r["mv"]["vid"], "name": r["name"], "author": "&".join(set(r["author"].split(";"))),
         "album": r["album"]["name"], "mp3": f'{r["name"]}-{"&".join(set(r["author"].split(";")))}({r["album"]["name"]}).mp3',
         "wav": f'{r["name"]}-{"&".join(set(r["author"].split(";")))}({r["album"]["name"]}).wav'} for r in
        res["req"]["data"]["body"]["item_song"]]
    # print(data_list)
    with futures.ThreadPoolExecutor(len(data_list)) as executor:
        trial_tasks = {data_list[i]["id"]: executor.submit(music_trial, **{"songId": data_list[i]["id"]}) for i in
                       range(len(data_list))}
        purl_list = {k: v.result() for k, v in trial_tasks.items() if v.result()}
        # print(purl_list)
        result_list = [data | v for data in data_list for k, v in purl_list.items() if data["id"] == k]
        video_tasks = {data_list[i]["vid"]: executor.submit(music_video, **{"vid": data_list[i]["vid"]}) for i in
                       range(len(data_list))}
        video_list = {k: v.result() for k, v in video_tasks.items() if v.result()}
        # print(video_list)
        result_list = [data | v for data in result_list for k, v in video_list.items() if data["vid"] == k]
        [executor.submit(movie2music, result_list[i]["mv"]["360P"],
                         f'{result_list[i]["name"]}-{result_list[i]["author"]}({result_list[i]["album"]})') for i in range(len(result_list))]
    print(result_list)
    return result_list


def main():
    # search_music(**{"keyword": "玫瑰少年", "page": "1", "size": "20"})
    # music_trial(**{"songId": "003OUlho2HcRHC"})
    music_video(**{"vid": "r0031vaxwj0"})
    # url = 'https://apd-ff3b9234aabec3ce3c18b80cca040033.v.smtcdns.com/mv.music.tc.qq.com/AiVsmr8FaEH9KAmspHpsEWzPycubECimFzUjHFFUkYZU/8406BD052CC4FA64A3B8BDD0380CEB129EB3DDD1F8B23BD324C32946FF6701DC475A48D30E815CB002AA7EDC0528B5A6ZZqqmusic_default/qmmv_0b6b4uabaaaa5man5nqc2fqvjziacdsqaeca.f9844.mp4?fname=qmmv_0b6b4uabaaaa5man5nqc2fqvjziacdsqaeca.f9844.mp4'
    # movie2music(url, "告白气球")
    # search(**{"keyword": "玫瑰少年"})


if __name__ == '__main__':
    main()
