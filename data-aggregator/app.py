from kafka import KafkaConsumer
from functools import reduce
import json
import time
import os
import psycopg2

# Enable Debug logging with these lines
# import logging
# import sys
#
# logger = logging.getLogger('kafka')
# logger.addHandler(logging.StreamHandler(sys.stdout))
# logger.setLevel(logging.DEBUG)

BOOTSTRAP_SERVER_URL = os.environ.get("BOOTSTRAP_SERVER_URL", "127.0.0.1:9092")
POSTGRESQL_SERVER_URL = os.environ.get("POSTGRESQL_SERVER_URL", "127.0.0.1:5432")
POSTGRESQL_DATABASE_NAME = "tgam"
POSTGRESQL_DATABASE_USERNAME = "postgres"
POSTGRESQL_DATABASE_PASSWORD = "postgres"
print(f"Bootstrap Server URL {BOOTSTRAP_SERVER_URL}")
print(f"PostgreSQL Server URL {POSTGRESQL_SERVER_URL}")


def insert_data(vendor_name):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO vendors(vendor_name)
             VALUES(%s) RETURNING vendor_id;"""
    conn = None
    vendor_id = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(
                    host=POSTGRESQL_SERVER_URL,
                    database=POSTGRESQL_DATABASE_NAME,
                    user=POSTGRESQL_DATABASE_USERNAME,
                    password=POSTGRESQL_DATABASE_PASSWORD
                )
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (vendor_name,))
        # get the generated id back
        vendor_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return vendor_id

def average(stock_values):
    return reduce(lambda a, b: a + b, stock_values) / len(stock_values)


def persist_stock_prices(company, stock_price):
    print(f'Persisting Data => Company: {company}, Stock Price: {stock_price}')


def aggregate_data():
    print("Executing method => aggregate_data ")
    consumer = KafkaConsumer('stocks',
                             bootstrap_servers=[BOOTSTRAP_SERVER_URL],
                             value_deserializer=lambda m: json.loads(m.decode('ascii')))
    #print("Managed to get consumer ")
    while True:
        time.sleep(2)
        #print("Inside While")
        amazon_stock_prices = []
        microsoft_stock_prices = []
        apple_stock_prices = []
        print("Polling Data")
        msg_pack = consumer.poll(timeout_ms=30000)
        # Check if there are records, before proceeding.
        if msg_pack:
            for tp, messages in msg_pack.items():
                for message in messages:
                    stock_messages = message.value
                    for stock_message in stock_messages["tickers"]:
                        if stock_message["name"] == "AMZN":
                            amazon_stock_prices.append(stock_message["price"])
                        elif stock_message["name"] == "MSFT":
                            microsoft_stock_prices.append(stock_message["price"])
                        elif stock_message["name"] == "AAPL":
                            apple_stock_prices.append(stock_message["price"])
                        else:
                            print("Unsupported Stock")
            # Ideally these records should not be empty, fallback to check if they are not empty.
            if amazon_stock_prices and microsoft_stock_prices and apple_stock_prices:
                persist_stock_prices("AMZN", average(amazon_stock_prices))
                persist_stock_prices("MSFT", average(microsoft_stock_prices))
                persist_stock_prices("AAPL", average(apple_stock_prices))
        else:
            print("No new records found")


if __name__ == '__main__':
    print("Starting Data Aggregator")
    aggregate_data()
