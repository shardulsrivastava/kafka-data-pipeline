from kafka import KafkaProducer
import json

def generate_data():
    producer = KafkaProducer(bootstrap_servers="kafka:9092",value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    while True:
        stock_json_message = {}
        ticker_data = []
        amazon_stock_data = {}
        microsoft_stock_data = {}
        apple_stock_data = {}
        amazon_stock_data["name"] = "AMZN"
        amazon_stock_data["price"] = 1902
        microsoft_stock_data["name"] = "MSFT"
        microsoft_stock_data["price"] = 107
        apple_stock_data["name"] = "AAPL"
        apple_stock_data["price"] = 215
        ticker_data.append(amazon_stock_data)
        ticker_data.append(microsoft_stock_data)
        ticker_data.append(apple_stock_data)
        stock_json_message["tickers"] = ticker_data
        print(json.dumps(stock_json_message))
        producer.send('stocks', stock_json_message)

if __name__ == '__main__':
    generate_data()
