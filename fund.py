# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: fund.py
# Time: 10月 12, 2021
import asyncio
from aiohttp import ClientSession
from user_agent import generate_user_agent
from time import sleep
from random import randint
from json import loads
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.commons.utils import JsCode


async def req(**kwargs):
    proxy = kwargs.get("proxy", "")
    method = kwargs.get("method", "GET")
    url = kwargs.get("url", "")
    params = kwargs.get("params", "")
    data = kwargs.get("data", "")
    headers = kwargs.get("headers", {})
    headers = {**{
        "User-Agent": generate_user_agent(),
    }, **headers}
    try:
        async with ClientSession() as client:
            if proxy:
                client.proxy = proxy
            async with client.request(method=method, url=url, headers=headers, params=params, data=data,
                                      timeout=5) as rs:
                if rs.status == 200:
                    result = await rs.read()
                    # print(result)
                    return result
                else:
                    print(await rs.text())
                    sleep(randint(2, 3))
                    retry = kwargs.get("retry", 0)
                    retry += 1
                    if retry >= 3:
                        return None
                    kwargs["retry"] = retry
                    return await req(**kwargs)
    except Exception as e:
        print(e)
        sleep(randint(2, 3))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 3:
            return None
        kwargs["retry"] = retry
        return await req(**kwargs)


async def query_fund(**kwargs):
    meta = {
        "url": "https://fundsuggest.eastmoney.com/FundCodeNew.aspx",
        "params": {
            "input": kwargs.get("key", "白酒"),
            "count": "10",
            "cb": " "
        }
    }
    res = await req(**meta)
    if not res: return None
    res = eval(res.decode())
    res = [r.split(",")[:-1] for r in res]
    print(res)
    return res


async def fund_detail(**kwargs):
    meta = {"url": f"https://j5.fund.eastmoney.com/sc/tfs/qt/v2.0.1/{kwargs.get('code', '012414')}.json"}
    res = await req(**meta)
    if not res: return None
    res = loads(res.decode())
    print(res)
    return res


async def fund_records(**kwargs):
    meta = {
        "url": f'https://uni-fundts.1234567.com.cn/dataapi/fund/FundVPageAcc',
        "params": {
            "CODE": kwargs.get("code", "012414"),
            "RANGE": kwargs.get("range", "n")
        }
    }
    res = await req(**meta)
    if not res: return None
    res = loads(res.decode())
    background_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#c86589'}, {offset: 1, color: '#06a7ff'}], false)"
    )
    area_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#eb64fb'}, {offset: 1, color: '#3fbbff0d'}], false)"
    )
    (
        Line(init_opts=opts.InitOpts(width="1600px", height="800px", bg_color=JsCode(background_color_js)))
            .add_xaxis(xaxis_data=[r.get("pdate", "") for r in res["data"]])
            .add_yaxis(
            series_name="成立来",
            y_axis=[float(r.get("yield", "")) for r in res["data"]],
            is_smooth=True,
            is_symbol_show=True,
            symbol="circle",
            symbol_size=4,
            linestyle_opts=opts.LineStyleOpts(color="#fff"),
            label_opts=opts.LabelOpts(is_show=False, position="top", color="white"),
            itemstyle_opts=opts.ItemStyleOpts(
                color="red", border_color="#fff", border_width=2
            ),
            # tooltip_opts=opts.TooltipOpts(is_show=True),
            areastyle_opts=opts.AreaStyleOpts(color=JsCode(area_color_js), opacity=1),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                    opts.MarkLineItem(symbol="none", x="90%", y="max"),
                    opts.MarkLineItem(symbol="circle", type_="max", name="最高点"),
                    opts.MarkLineItem(symbol="circle", type_="min", name="最低点"),
                ]
            ),
        )
            .add_yaxis(
            series_name="中证白酒",
            y_axis=[float(r.get("indexYield", "")) for r in res["data"]],
            label_opts=opts.LabelOpts(is_show=False),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最高点"),
                    opts.MarkPointItem(type_="min", name="最低点"),
                ]
            ),
        )
            .add_yaxis(
            series_name="业绩比较基准",
            y_axis=[float(r.get("benchQuote", "")) for r in res["data"]],
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="同类平均",
            y_axis=[float(r.get("fundTypeYield", "")) for r in res["data"]],
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="白酒", subtitle="实时数据"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
            .render("chart_test.html")
    )
    return res


async def fund_estimate(**kwargs):
    meta = {
        "url": "https://fundmobapi.eastmoney.com/FundMApi/FundVarietieValuationDetail.ashx",
        "params": {
            "FCODE": kwargs.get("code", "012414"),
            "deviceid": "123",
            "plat": "Iphone",
            "product": "EFund",
            "version": "6.2.5",
        },
    }
    res = await req(**meta)
    if not res: return None
    res = loads(res.decode())
    print(res)
    return res


async def gen_html(**kwargs):
    title = kwargs.get("title", "某商场销售情况")
    subtitle = kwargs.get("subtitle", "实时数据")
    x_list = kwargs.get("x_list", ["衬衫", "毛衣", "领带", "裤子", "风衣", "高跟鞋", "袜子"])
    y_list = kwargs.get("y_list", [{"商家A": [114, 55, 27, 101, 125, 27, 105]}, {"商家B": [57, 134, 137, 129, 145, 60, 49]}])

    line = Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
    line.add_xaxis(x_list)
    for y in y_list:
        k, v = list(y.items())[0]
        line.add_yaxis(series_name=k, y_axis=v)
    line.set_global_opts(title_opts=opts.TitleOpts(title=title, subtitle=subtitle))
    line.render()
    return line.render()


if __name__ == '__main__':
    rs = asyncio.get_event_loop().run_until_complete(gen_html())
