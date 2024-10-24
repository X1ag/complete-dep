import asyncio
from threading import Thread
import methods.parser as parser 
import methods.api as api

def start_parser(address, timeframe):
	asyncio.run(parser.main(address,timeframe))

def start_main():
	asyncio.run(api.main())
 
threadHours = Thread(target=start_parser, args=("EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N", "1h"), daemon=True)
threadMinutes = Thread(target=start_parser, args=("EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N", "5m"), daemon=True)
threadHours.start()
threadMinutes.start()
start_main()
print('script started')