#!/usr/bin/env python3
import asyncio

class app_loop():

    def __init__(self, loop):
        self.loop = loop
        self.tasks = []

    def add_task(self, task):
        self.loop.create_task(task)

    def add_task_to_running_loop(self, task):
        asyncio.ensure_future(task)

    def start_loop(self):
        self.loop.run_forever()

    async def update_loop(self, root, interval):
        while True:
            root.update()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.close()
