from pymongo import MongoClient
from logger import LOGGER

class MongoDBHandler:
    def __init__(self, host, port, username=None, password=None):
        self.host = host
        self.port = port
        self.client = None
        self.db = None
        self.collection = None

    def insert_data(self, db_name, collection_name, data_to_insert):
        try:
            self.client = MongoClient(host=self.host, port=self.port)
            self.db = self.client[db_name]
            LOGGER.info("Connected to MongoDB")
            self.collection = self.db[collection_name]
            result = self.collection.insert_one(data_to_insert)
            LOGGER.info(f"Data inserted with ObjectId: {result.inserted_id}")
            self.close_connection()
        except Exception as e:
            LOGGER.info(f"Error inserting data into MongoDB: {e}")
            self.close_connection()

    def close_connection(self):
        if self.client:
            self.client.close()
            LOGGER.info("MongoDB connection closed")

# 사용 예시
if __name__ == "__main__":
    # MongoDB 연결 정보
    host = 'localhost'
    port = 27017
    db_name = 'devices'
    collection_name = 'airQuality_out'

    # MongoDBHandler 인스턴스 생성 및 연결
    mongo_handler = MongoDBHandler(host, port)
    mongo_handler.connect(db_name,collection_name)

    # 저장할 데이터
    data_to_insert = {
        'name': 'SSG',
        'age': 30,
        'email': 'ssg@example.com'
    }

    # 데이터 삽입
    mongo_handler.insert_data(collection_name, data_to_insert)

