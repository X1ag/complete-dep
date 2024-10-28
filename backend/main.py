import asyncio
import logging
import logging.handlers
from multiprocessing import Process, Queue, current_process
import methods.parser as parser
import methods.api as api
import json
import sys

class ShortenJSONFilter(logging.Filter):
    """
    Фильтр, укорачивающий длинные сообщения (например, JSON) для логов.
    """
    def filter(self, record):
        # Если сообщение — JSON или длинная строка, обрезаем до 500 символов
        if isinstance(record.msg, (dict, list)):
            record.msg = json.dumps(record.msg)[:100] + '... (обрезано)'
        elif isinstance(record.msg, str) and len(record.msg) > 100:
            record.msg = record.msg[:100] + '... (обрезано)'
        return True

def setup_logger(queue, level=logging.INFO):
    """
    Настройка логгера для отправки сообщений в очередь с заданным уровнем логирования.
    """
    handler = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

def start_parser(queue, address, timeframe):
    setup_logger(queue)
    logger = logging.getLogger(current_process().name)
    logger.info(f"Запуск парсера для {address} с интервалом {timeframe}")

    try:
        asyncio.run(parser.main(address, timeframe))
    except Exception as e:
        logger.error(f"Ошибка в процессе парсера: {str(e)[:100]}... (обрезано)")
    else:
        logger.info(f"Завершение парсера для {address} с интервалом {timeframe}")

def start_main(queue):
    setup_logger(queue)
    logger = logging.getLogger(current_process().name)
    logger.info("Запуск основного API процесса")

    try:
        asyncio.run(api.main())
    except Exception as e:
        logger.error(f"Ошибка в основном процессе API: {str(e)[:100]}... (обрезано)")
    else:
        logger.info("Завершение основного API процесса")

def log_listener(queue):
    """
    Функция для прослушивания и вывода логов из очереди.
    """
    root = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    filter = ShortenJSONFilter()  # Создаем экземпляр фильтра

    while True:
        try:
            record = queue.get()
            if record is None:
                break

            # Применяем фильтр перед выводом
            if filter.filter(record):
                logger = logging.getLogger(record.name)
                logger.handle(record)
        except Exception:
            import traceback
            print("Ошибка в лог-листенере:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    # Создаем очередь для логов
    log_queue = Queue()
    
    # Запускаем процесс прослушивания логов
    listener = Process(target=log_listener, args=(log_queue,))
    listener.start()
    
    # Запускаем процессы с передачей очереди для логов
    process_hours_anon = Process(target=start_parser, args=(log_queue, "EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N", "1h"), daemon=True)
    process_minutes_anon = Process(target=start_parser, args=(log_queue, "EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N", "5m"), daemon=True)

    process_hours_tg_usernames = Process(target=start_parser, args=(log_queue, "EQCA14o1-VWhS2efqoh_9M1b_A9DtKTuoqfmkn83AbJzwnPi", "1h"), daemon=True)
    process_minutes_tg_usernames = Process(target=start_parser, args=(log_queue, "EQCA14o1-VWhS2efqoh_9M1b_A9DtKTuoqfmkn83AbJzwnPi", "5m"), daemon=True)

    process_hours_domains = Process(target=start_parser, args=(log_queue, "EQC3dNlesgVD8YbAazcauIrXBPfiVhMMr5YYk2in0Mtsz0Bz", "1h"), daemon=True)
    process_minutes_domains = Process(target=start_parser, args=(log_queue, "EQC3dNlesgVD8YbAazcauIrXBPfiVhMMr5YYk2in0Mtsz0Bz", "5m"), daemon=True)

    process_hours_anon.start()
    process_hours_tg_usernames.start()
    process_hours_domains.start()
    
    process_minutes_anon.start()
    process_minutes_tg_usernames.start()
    process_minutes_domains.start()
    # Запускаем основную функцию в главном процессе
    start_main(log_queue)
    
    # Ожидаем завершения процессов
    process_hours_anon.join()
    process_hours_tg_usernames.join()
    process_hours_domains.join()
    
    process_minutes_anon.join()
    process_minutes_tg_usernames.join()
    process_minutes_domains.join()
    
    # Останавливаем процесс логов
    log_queue.put(None)
    listener.join()
    
    print('script started')
