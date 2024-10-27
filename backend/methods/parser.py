import asyncio
from datetime import datetime, timedelta
import pytz
import json
from db.connect_db import check_db_connection, insert_data
from methods.get_floor import get_nft_collection_floor

timezone = pytz.timezone('Europe/Moscow')

pricesMinutes = []
pricesHours = []

now = datetime.now(timezone)
close_time_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
open_time_hour = now.replace(minute=0,second=0, microsecond=0)
close_time_minutes = (now + timedelta(minutes=5)).replace(second=0, microsecond=0)
open_time_minutes = now.replace(second=0, microsecond=0)

def get_time_minutes(address):
    global open_time_minutes, close_time_minutes, pricesMinutes
    # Обновление текущего времени
    now = datetime.now(timezone)
    if len(pricesMinutes) > 0 and close_time_minutes <= now.replace(second=0, microsecond=0):
        data = {
            'openTime': int(open_time_minutes.timestamp() * 1000),
            'closeTime': int(close_time_minutes.timestamp() * 1000),
            'percentChangePrice': percentChange(timeframe='5m'),
            'currentPrice': pricesMinutes[-1],
            'open': pricesMinutes[0],
            'high': max(pricesMinutes),
            'low': min(pricesMinutes),
            'close': pricesMinutes[-1],
        }
        writeInDB(data, address, timeframe='5m')
        print(f"Minutes candles was write in DB address:{address}\033[0m")
        pricesMinutes.clear()
        close_time_minutes = (now + timedelta(minutes=5)).replace(second=0, microsecond=0)
        open_time_minutes = now.replace(second=0, microsecond=0)

    print(f'\033[92m close time: {close_time_minutes} \033[0m')
    return open_time_minutes, close_time_minutes

def get_time_hour(address):
    global open_time_hour, close_time_hour, pricesHours
    # Обновление текущего времени
    now = datetime.now(timezone)
    if len(pricesHours) > 0 and close_time_hour <= now.replace(minute=0,second=0, microsecond=0):
        data = {
            'openTime': int(open_time_hour.timestamp() * 1000),
            'closeTime': int(close_time_hour.timestamp() * 1000),
            'percentChangePrice': percentChange(timeframe='1h'),
            'currentPrice': pricesHours[-1],
            'open': pricesHours[0],
            'high': max(pricesHours),
            'low': min(pricesHours),
            'close': pricesHours[-1],
        }
        writeInDB(data, address, timeframe='1h')
        print(f"Hours candles was write in DB address:{address}\033[0m")
        pricesHours.clear()
        close_time_hour = (now + timedelta(hours=1)).replace(minute=0,second=0, microsecond=0)
        open_time_hour = now.replace(minute=0,second=0, microsecond=0)

    print(f'\033[92m close time: {close_time_hour} \033[0m')
    return open_time_hour, close_time_hour

async def getPrice(address, timeframe):
    print(f'Fetching price for address: {address}')
    result = await get_nft_collection_floor(address)
    if result is None:
        asyncio.sleep(40)
        result = await get_nft_collection_floor(address)
    if timeframe=='5m':
        pricesMinutes.append(result)
    elif timeframe=='1h':
        pricesHours.append(result)
    print(f'\033[92m Price fetched: {result} \033[0m')
    return result

def percentChange(timeframe):
    if timeframe == '1h':
        if len(pricesHours) > 2 and pricesHours[0] is not None and pricesHours[-1] is not None:
            return ((pricesHours[-1] - pricesHours[0]) / (pricesHours[0] + pricesHours[-1] / 2)) * 100
        return None
    elif timeframe == '5m':
        if len(pricesMinutes) > 2 and pricesMinutes[0] is not None and pricesMinutes[-1] is not None:
            return ((pricesMinutes[-1] - pricesMinutes[0]) / (pricesMinutes[0] + pricesMinutes[-1] / 2)) * 100
        return None

async def writeFloorInFile(data, address, timeframe):
    with open(f'./candles/candles{address}{timeframe}.json', 'w+', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        if timeframe == '1h':
            print(f"File \033[96mcandles{address}{timeframe}\033[0m.json updated {len(pricesHours)} candles")
        elif timeframe == '5m':
            print(f"File \033[96mcandles{address}{timeframe}\033[0m.json updated {len(pricesMinutes)} candles")
        file.write('\n')

def writeInDB(data, address, timeframe):
    try:
        if check_db_connection():
            insert_data(address, data['openTime'], data['closeTime'], data['currentPrice'], data['open'], data['high'], data['low'], data['close'], data['percentChangePrice'], timeframe)
    except Exception as e:
        print(e)            

async def getData(address, timeframe):
    while True:
        try:
            if timeframe == '1h':
                data = {
                    'openTime': int(get_time_hour(address)[0].timestamp() * 1000),
                    'closeTime': int(get_time_hour(address)[1].timestamp() * 1000),
                    'percentChangePrice': percentChange(timeframe),
                    'currentPrice': await getPrice(address,'1h'),
                    'open': pricesHours[0],
                    'high': max(pricesHours),
                    'low': min(pricesHours),
                    'close': pricesHours[-1],
                }
            if timeframe == '5m':
                data = {
                    'openTime': int(get_time_minutes(address)[0].timestamp() * 1000),
                    'closeTime': int(get_time_minutes(address)[1].timestamp() * 1000),
                    'percentChangePrice': percentChange(timeframe),
                    'currentPrice': await getPrice(address,'5m'),
                    'open': pricesMinutes[0],
                    'high': max(pricesMinutes),
                    'low': min(pricesMinutes),
                    'close': pricesMinutes[-1],
                }
            if data:
                await writeFloorInFile(data, address, timeframe)
        except Exception as e:
            print(f"Bro, eto oshibka bro: {e}")
        await asyncio.sleep(60)

async def main(address, timeframe):
    print('Starting main function')
    await getData(address, timeframe)

