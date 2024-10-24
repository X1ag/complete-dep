import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def check_db_connection():
	try:
		conn = psycopg2.connect(
						dbname=os.getenv('DB_NAME'),
						host=os.getenv('DB_HOST'),
						user=os.getenv('DB_USER'),
						password=os.getenv('DB_PASSWORD'),
						port=os.getenv('DB_PORT'),
			)

		# Создание курсора
		with conn.cursor() as curs:
			# Выполнение тестового SQL-запроса
			curs.execute("SELECT NOW();")
			current_time = curs.fetchone()
			print("Connection successful. Current time in DB:", current_time)
			return True	
	except psycopg2.Error as e:
		# Обработка ошибок
		print(f'Error bro oshibka: {e}')
		return False
	finally:
		# Закрытие соединения с базой данных
		if conn:
			conn.close()
check_db_connection()

def insert_data(address, openTime, closeTime, currentPrice, openPrice, maxPrice, minPrice, closePrice, priceChange, timeframe):
	try:
		# Установка соединения с базой данных
		conn = psycopg2.connect(
						dbname=os.getenv('DB_NAME'),
						host=os.getenv('DB_HOST'),
						user=os.getenv('DB_USER'),
						password=os.getenv('DB_PASSWORD'),
						port=os.getenv('DB_PORT'),
		)
		# Создание курсора
		with conn.cursor() as curs:
			# SQL-запрос для вставки данных
			if timeframe == '1h':
				create_query = '''
					CREATE TABLE IF NOT EXISTS candlesHours (
					address VARCHAR(255) NOT NULL,
					openTime BIGINT NOT NULL,
					closeTime BIGINT NOT NULL,
					currentPrice FLOAT NOT NULL,
					openPrice FLOAT,
					maxPrice FLOAT,
					minPrice FLOAT,
					closePrice FLOAT,
					priceChange FLOAT
					);
					'''
				curs.execute(create_query)

				insert_query = '''
				INSERT INTO candlesHours (address, openTime, closeTime, currentPrice, openPrice, maxPrice, minPrice, closePrice, priceChange) VALUES (
				%s, %s, %s, %s, %s, %s, %s, %s, %s
				);'''
			elif timeframe == '5m':
				create_query = '''
			CREATE TABLE IF NOT EXISTS candlesMinutes (
			address VARCHAR(255) NOT NULL,
			openTime BIGINT NOT NULL,
			closeTime BIGINT NOT NULL,
			currentPrice FLOAT NOT NULL,
			openPrice FLOAT,
			maxPrice FLOAT,
			minPrice FLOAT,
			closePrice FLOAT,
			priceChange FLOAT
			);
			'''
				curs.execute(create_query)

				insert_query = '''
							INSERT INTO candlesMinutes (address, openTime, closeTime, currentPrice, openPrice, maxPrice, minPrice, closePrice, priceChange) VALUES (
							%s, %s, %s, %s, %s, %s, %s, %s, %s
							);'''
			curs.execute(insert_query, (address, openTime, closeTime, currentPrice, openPrice, maxPrice, minPrice, closePrice, priceChange))
			conn.commit()
	except psycopg2.Error as e:
		# Обработка ошибок
		print(f'Error: {e}')

def connect_db(address, timeframe):
	try:
		conn = psycopg2.connect(
						dbname=os.getenv('DB_NAME'),
						host=os.getenv('DB_HOST'),
						user=os.getenv('DB_USER'),
						password=os.getenv('DB_PASSWORD'),
						port=os.getenv('DB_PORT'),
				)
		# Создание курсора
		with conn.cursor() as curs:
			# Выполнение SQL-запроса
			if timeframe =='1h':
				curs.execute('SELECT * FROM candlesHours WHERE address = %s;', (address,))
			elif timeframe == '5m':
				curs.execute('SELECT * FROM candlesMinutes WHERE address = %s;', (address,))
			# Получение всех строк результата запроса
			all_candles = curs.fetchall()
			return all_candles	
	except psycopg2.Error as e:
		# Обработка ошибок
		print(f'Error bro oshibka: {e}')
	
	finally:
		# Закрытие соединения с базой данных
		if conn:
			conn.close()
