import asyncio
from datetime import datetime, timedelta
import pytz
import json
import os
from db.connect_db import insert_data
from methods.get_floor import get_nft_collection_floor

timezone = pytz.timezone('Europe/Moscow')

prices = []
close_price = None

now = datetime.now(timezone)
close_time_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
open_time_hour = now.replace(minute=0,second=0, microsecond=0)
close_time_minutes = (now + timedelta(minutes=5)).replace(second=0, microsecond=0)
open_time_minutes = now.replace(second=0, microsecond=0)

def get_time_minutes(address):
    global open_time_minutes, close_time_minutes, prices
    
    # Обновление текущего времени
    now = datetime.now(timezone)
    if len(prices) > 0 and close_time_minutes <= now.replace(second=0, microsecond=0):
        data = {
            'openTime': int(open_time_minutes.timestamp() * 1000),
            'closeTime': int(close_time_minutes.timestamp() * 1000),
            'percentChangePrice': percentChange(),
            'currentPrice': prices[-1],
            'open': prices[0],
            'high': max(prices),
            'low': min(prices),
            'close': prices[-1],
        }
        writeInDB(data, address)
        print(f"Minutes candles was write in DB address:{address}\033[0m")
        prices.clear()
        close_time_minutes = (now + timedelta(minutes=5)).replace(second=0, microsecond=0)
        open_time_minutes = now.replace(second=0, microsecond=0)

    print(f'\033[92m close time: {close_time_minutes} \033[0m')
    return open_time_minutes, close_time_minutes

def get_time_hour(address):
    global open_time_hour, close_time_hour, prices
    # Обновление текущего времени
    now = datetime.now(timezone)
    if len(prices) > 0 and close_time_hour <= now.replace(minute=0,second=0, microsecond=0):
        data = {
            'openTime': int(open_time_hour.timestamp() * 1000),
            'closeTime': int(close_time_hour.timestamp() * 1000),
            'percentChangePrice': percentChange(),
            'currentPrice': prices[-1],
            'open': prices[0],
            'high': max(prices),
            'low': min(prices),
            'close': prices[-1],
        }
        writeInDB(data, address)
        print(f"Hours candles was write in DB address:{address}\033[0m")
        prices.clear()
        close_time_hour = (now + timedelta(hours=1)).replace(minute=0,second=0, microsecond=0)
        open_time_hour = now.replace(minute=0,second=0, microsecond=0)

    print(f'\033[92m close time: {close_time_hour} \033[0m')
    return open_time_hour, close_time_hour

async def getPrice(address):
    print(f'Fetching price for address: {address}')
    result = await get_nft_collection_floor(address)
    if result is None:
        asyncio.sleep(15)
        result = await get_nft_collection_floor(address)
    prices.append(result)
    print(f'\033[92m Price fetched: {result} \033[0m')
    return result

def percentChange():
    if len(prices) < 2 or prices[0] is None or prices[-1] is None:
        return None
    return ((prices[-1] - prices[0]) / (prices[0] + prices[-1] / 2)) * 100

async def writeFloorInFile(data, address, timeframe):
    with open(f'./candles/candles{address}{timeframe}.json', 'w+', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"File \033[96mcandles{address}{timeframe}\033[0m.json updated, request amount: {len(prices)}")
        file.write('\n')

def writeInDB(data, address, timeframe='1h'):
     insert_data(address, data['openTime'], data['closeTime'], data['currentPrice'], data['open'], data['high'], data['low'], data['close'], data['percentChangePrice'], timeframe)

async def getData(address, timeframe):
    while True:
        try:
            if timeframe == '1h':
                data = {
                    'openTime': int(get_time_hour(address)[0].timestamp() * 1000),
                    'closeTime': int(get_time_hour(address)[1].timestamp() * 1000),
                    'percentChangePrice': percentChange(),
                    'currentPrice': await getPrice(address),
                    'open': prices[0],
                    'high': max(prices),
                    'low': min(prices),
                    'close': prices[-1],
                }
            if timeframe == '5m':
                data = {
                    'openTime': int(get_time_minutes(address)[0].timestamp() * 1000),
                    'closeTime': int(get_time_minutes(address)[1].timestamp() * 1000),
                    'percentChangePrice': percentChange(),
                    'currentPrice': await getPrice(address),
                    'open': prices[0],
                    'high': max(prices),
                    'low': min(prices),
                    'close': prices[-1],
                }
            if data:
                await writeFloorInFile(data, address, timeframe)
        except Exception as e:
            print(f"Bro, eto oshibka bro: {e}")
        await asyncio.sleep(15)

async def main(address, timeframe):
    print('Starting main function')
    await getData(address, timeframe)

