import asyncio
import os

class FileMonitor:
    def __init__(self, queue, file_path) -> None:
        self.file_path = file_path
        self.queue = queue
    
    # func: monitor
    async def monitor(self):
        while True:
            for file in os.listdir(self.file_path):
                if self.queue.empty():
                    await self.queue.put(os.path.join(self.file_path, file))
            await asyncio.sleep(1)