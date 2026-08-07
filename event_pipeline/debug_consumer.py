#!/usr/bin/env python3
"""مستهلك تصحيح: يقرأ رسائل من الـ topic للتأكد أن الطالب 2 سيستلم بيانات فعلاً"""
import argparse
import json

from confluent_kafka import Consumer

from config.settings import settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    consumer = Consumer({
        "bootstrap.servers": settings.REDPANDA_BOOTSTRAP,
        "group.id": "debug-consumer",
        "auto.offset.reset": "latest",
    })
    consumer.subscribe([settings.RAW_EVENTS_TOPIC])

    seen = 0
    print("👂 بانتظار الرسائل ... (Ctrl+C للخروج)")
    try:
        while seen < args.count:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"⚠️ {msg.error()}")
                continue
            event = json.loads(msg.value())
            print(f"📨 {event.get('event_id')} | {event.get('cloud_provider')} | "
                  f"{event.get('action')} | {event.get('severity')}")
            seen += 1
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()