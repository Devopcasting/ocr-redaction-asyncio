import asyncio
import os
import shutil
import configparser
from handlers.file_monitor import FileMonitor
from handlers.identify_card import IdentifyCard
from handlers.pan_card_p1 import PanCardPattern1Handler
from handlers.pan_card_p2 import PanCardPattern2Handler
from handlers.aadhaar_card_front import AadhaarCardFrontHandler
from handlers.e_aadhaar_card import EAadhaarCardHandler
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
        identify_card_obj = IdentifyCard(file_path, pan_card_p1_folder_path, pan_card_p2_folder_path, aadhaar_card_front_folder_path, eaadhaar_card_folder_path).identify()
        if identify_card_obj:
            q.task_done()
        else:
            logger.error(f"ERR002")
            shutil.move(file_path, os.path.join(rejected_folder_path, file_name) )
        await asyncio.sleep(1)

# func: write xml data for pan card pattern 1
async def write_xml_pan_card_p1(q):
    while True:
        file_path = await q.get()
        file_name = os.path.basename(file_path)
        if file_path is None:
            break
        # start: writing pan card pattern-1 info
        write_pan_card_p1_data = PanCardPattern1Handler(file_path, xml_folder_path, redacted_folder_path).pancard_p1()
        if write_pan_card_p1_data:
            logger.info(f"Pan card xml data is ready for {file_name}")
            q.task_done()
        else:
            logger.error(f"PANERR001")
            shutil.move(file_path, os.path.join(rejected_folder_path, file_name))
        await asyncio.sleep(1)

# func: write xml data for pan card pattern 2
async def write_xml_pan_card_p2(q):
    while True:
        file_path = await q.get()
        file_name = os.path.basename(file_path)
        if file_path is None:
            break
        # start: writing pan card pattern-2 info
        write_pan_card_p2_data = PanCardPattern2Handler(file_path, xml_folder_path, redacted_folder_path).pancard_p2()
        if write_pan_card_p2_data:
            logger.info(f"Pan card xml data is ready for {file_name}")
            q.task_done()
        else:
            logger.error(f"PANERR001")
            shutil.move(file_path, os.path.join(rejected_folder_path, file_name))
        await asyncio.sleep(1)

# func: write xml data for aadhaar card front-side
async def write_xml_aadhaar_card_front(q):
    while True:
        file_path = await q.get()
        file_name = os.path.basename(file_path)
        if file_path is None:
            break
        # start: writting aadhaar card front-side info
        write_aadhaar_card_front_data = AadhaarCardFrontHandler(file_path, xml_folder_path, redacted_folder_path).aadhaarcard_front()
        if write_aadhaar_card_front_data:
            logger.info(f"Aadhaar card xml data is ready for {file_name}")
            q.task_done()
        else:
            logger.error(f"AADERR001")
            shutil.move(file_path, os.path.join(rejected_folder_path, file_name))
            q.task_done()
        await asyncio.sleep(1)

# func: write xml data for e-aadhhar card
async def write_xml_e_aadhaar_card(q):
    while True:
        file_path = await q.get()
        file_name = os.path.basename(file_path)
        if file_path is None:
            break
        # start: writting e-aadhaar card
        write_e_aadhaar_card_data = EAadhaarCardHandler(file_path, xml_folder_path, redacted_folder_path).e_aadhaarcard()
        if write_e_aadhaar_card_data:
            logger.info(f"E-Aaadhaar card xml data is ready for {file_name}")
            q.task_done()
        else:
            logger.error(f"AADERR001")
            shutil.move(file_path, os.path.join(rejected_folder_path, file_name))
            q.task_done()

        await asyncio.sleep(1)

# func: main ocrr-engine
async def start_ocrr_engine():
    # define Queues
    upload_folder_q = asyncio.Queue()
    processed_folder_q = asyncio.Queue()
    pan_card_p1_folder_q = asyncio.Queue()
    pan_card_p2_folder_q = asyncio.Queue()
    aadhaar_card_front_folder_q = asyncio.Queue()
    e_aadhaar_card_q = asyncio.Queue()

    #  monitor folders
    monitor_upload_folder = FileMonitor(upload_folder_q, upload_folder_path)
    monitor_processed_folder = FileMonitor(processed_folder_q, processed_folder_path)
    monitor_pan_card_p1_folder = FileMonitor(pan_card_p1_folder_q, pan_card_p1_folder_path)
    monitor_pan_card_p2_folder = FileMonitor(pan_card_p2_folder_q, pan_card_p2_folder_path)
    monitor_aadhaar_card_front_folder = FileMonitor(aadhaar_card_front_folder_q, aadhaar_card_front_folder_path)
    monitor_e_aadhaar_card_folder = FileMonitor(e_aadhaar_card_q, eaadhaar_card_folder_path)

    # func: wrap process_images in a async
    async def async_process_image(q):
        await process_images(q)

    # func: wrap identify_image in a async
    async def async_identify_image(q):
        await identify_image(q)

    # func: wrap write_xml_pan_card_p1 in a async
    async def async_write_xml_pan_card_p1(q):
        await write_xml_pan_card_p1(q)

    # func: wrap write_xml_pan_card_p2 in a async
    async def async_write_xml_pan_card_p2(q):
        await write_xml_pan_card_p2(q)
    
    # func: wrap write_xml_aadhaar_card_front in a async
    async def async_write_xml_aadhaar_card_front(q):
        await write_xml_aadhaar_card_front(q)
    
    # func: wrap write_xml_e_aadhaar_card in a async
    async def async_write_xml_e_aadhaar_card(q):
        await write_xml_e_aadhaar_card(q)

    # tasks
    upload_folder_task = asyncio.create_task(monitor_upload_folder.monitor())
    process_folder_task = asyncio.create_task(monitor_processed_folder.monitor())
    pan_card_p1_folder_task = asyncio.create_task(monitor_pan_card_p1_folder.monitor())
    pan_card_p2_folder_task = asyncio.create_task(monitor_pan_card_p2_folder.monitor())
    aadhaar_card_front_folder_task = asyncio.create_task(monitor_aadhaar_card_front_folder.monitor())
    e_aadhaar_card_folder_task = asyncio.create_task(monitor_e_aadhaar_card_folder.monitor())

    process_image_task = asyncio.create_task(async_process_image(upload_folder_q))
    identify_image_task = asyncio.create_task(async_identify_image(processed_folder_q))
    write_xml_pan_card_p1_task = asyncio.create_task(async_write_xml_pan_card_p1(pan_card_p1_folder_q))
    write_xml_pan_card_p2_task = asyncio.create_task(async_write_xml_pan_card_p2(pan_card_p2_folder_q))
    write_xml_aadhaar_card_front_task = asyncio.create_task(async_write_xml_aadhaar_card_front(aadhaar_card_front_folder_q))
    write_xml_e_aadhaar_card_task = asyncio.create_task(async_write_xml_e_aadhaar_card(e_aadhaar_card_q))
    
    # gather all the tasks
    await asyncio.gather(upload_folder_task, process_image_task, 
                         process_folder_task, identify_image_task,
                          pan_card_p1_folder_task, write_xml_pan_card_p1_task,
                           pan_card_p2_folder_task, write_xml_pan_card_p2_task,
                            aadhaar_card_front_folder_task, write_xml_aadhaar_card_front_task,
                             e_aadhaar_card_folder_task, write_xml_e_aadhaar_card_task )

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
    aadhaar_card_front_folder_path = config['Path']['aadhaarcardfront']
    aadhaar_card_back_folder_path = config['Path']['aadhaarcardback']
    eaadhaar_card_folder_path = config['Path']['eaadhaar']
    redacted_folder_path = config['Path']['redacted']
    xml_folder_path = config['Path']['xml']

    asyncio.run(start_ocrr_engine())