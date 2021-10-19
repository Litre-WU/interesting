# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: kafak_test.py
# Time: 10月 19, 2021
import asyncio
from json import loads, dumps
from kafka import KafkaProducer, KafkaConsumer, KafkaClient, TopicPartition
from kafka.errors import kafka_errors
import traceback


# 生产者
async def producer(**kwargs):
    kafka_producer = KafkaProducer(bootstrap_servers=[':9092'], key_serializer=lambda k: dumps(k).encode(),
                                   value_serializer=lambda v: dumps(v).encode())
    for i in range(kwargs.get("num", 100)):
        future = kafka_producer.send(topic=kwargs.get("topic", "kafka_demo"), key=f'{kwargs.get("name", "商品")}',
                                     value=i,
                                     partition=1)
        try:
            future.get(timeout=10)
        except kafka_errors:
            traceback.format_exc()
    return True


# 消费者
async def consumer(**kwargs):
    kafka_consumer = KafkaConsumer(kwargs.get("topic", "kafka_demo"), bootstrap_servers=':9092',
                                   group_id=kwargs.get("gid", "demo"))
    for message in kafka_consumer:
        print({loads(message.key.decode()): loads(message.value.decode())})


if __name__ == '__main__':
    # asyncio.get_event_loop().run_until_complete(consumer())
    meta = {"name": "Mac Pro 2022", "num": 10000}
    rs = asyncio.get_event_loop().run_until_complete(producer(**meta))
    print(rs)