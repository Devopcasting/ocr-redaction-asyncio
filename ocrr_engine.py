import asyncio
import queue
import os
import shutil
import configparser
from handlers.file_monitor import FileMonitor
from handlers.identify_card import IdentifyCard
from helpers.process_images import ProcessJPEGImages
from ocrr_logging.ocrrlogging import OCRREngineLogging

# func: process images from upload folder
async def process_images(q):
    while True:
        file_path = await q.get()
        file_name = os.path.basename(file_path)
        if file_path is None:
            break
        # start: processing images
        processed_image_obj = ProcessJPEGImages(file_path, os.path.join(processed_folder_path, file_name)).processed_image()
        if processed_image_obj:
            logger.info(f"{file_name} processed successfully")
            shutil.move(file_path, os.path.join(original_folder_path, file_name))
            q.task_done()
        else:
            logger.error(f"ERR001")
        await asyncio.sleep(1)

# func: identify image
async def identify_image(q):
    while True:
        file_path = await q.get()
        file_name = os.path.basename(file_path)
        if file_path is None:
            break
        # start: identify image
        identify_card_obj = IdentifyCard(file_path, pan_card_p1_folder_path, pan_card_p2_folder_path).identify()
        if identify_card_obj:
            q.task_done()
        else:
            logger.error(f"ERR002")
            shutil.move(file_path, os.path.join(rejected_folder_path, file_name) )
        await asyncio.sleep(1)
    
# func: main ocrr-engine
async def start_ocrr_engine():
    # define Queues
    upload_folder_q = asyncio.Queue()
    processed_folder_q = asyncio.Queue()

    #  monitor folders
    monitor_upload_folder = FileMonitor(upload_folder_q, upload_folder_path)
    monitor_processed_folder = FileMonitor(processed_folder_q, processed_folder_path)

    # func: wrap process_images in a async
    async def async_process_image(q):
        await process_images(q)

    # func: wrap identify_image in a async
    async def async_identify_image(q):
        await identify_image(q)

    # tasks
    upload_folder_task = asyncio.create_task(monitor_upload_folder.monitor())
    process_folder_task = asyncio.create_task(monitor_processed_folder.monitor())

    process_image_task = asyncio.create_task(async_process_image(upload_folder_q))
    identify_image_task = asyncio.create_task(async_identify_image(processed_folder_q))
    
    # gather all the tasks
    await asyncio.gather(upload_folder_task, process_image_task, process_folder_task, identify_image_task)

if __name__ == '__main__':

    # Configure logger
    config = OCRREngineLogging()
    logger = config.configure_logger()

    # create a ConfigParser object with the allow_no_value keyword argument
    config = configparser.ConfigParser(allow_no_value=True)
    # read config.ini
    config.read(r'C:\Users\pokhriyal\Desktop\Asyncio-OCRR-Pan_Card\config.ini')

    # get the paths
    upload_folder_path = config['Path']['upload']
    processed_folder_path = config['Path']['processed']
    original_folder_path = config['Path']['original']
    rejected_folder_path = config['Path']['rejected']
    pan_card_p1_folder_path = config['Path']['pancardp1']
    pan_card_p2_folder_path = config['Path']['pancardp2']

    asyncio.run(start_ocrr_engine())