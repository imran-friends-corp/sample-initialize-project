from functools import cached_property
from uuid import UUID

import redis
import json
import datetime

from bson import ObjectId, Binary


class RedisBase:
    """
    # Example usage:
    if __name__ == '__main__':
        redis_crud = RedisExpiryStore()

        # Create
        redis_crud.create('my_key', 'Data from redis', 60)  # Expires in 60 seconds

        # Read
        value = redis_crud.read('my_key')
        print('Read:', value)

        # Update
        redis_crud.update('my_key', 'new_value', 10)  # Updates value and extends expiration to 120 seconds

        # Check if key is expired
        is_expired = redis_crud.is_expired('my_key')
        print('Is Expired:', is_expired)

        # Delete
        # redis_crud.delete('my_key')


    if __name__ == '__main__':
        redis_crud = RedisStore()

        # Create
        redis_crud.create('my_key1', {'field1': 'value1', 'field2': 'value2'})

        # Read
        value = redis_crud.read('my_key1')
        print('Read:', value)

        # Update
        redis_crud.update('my_key1', {'field1': 'new_value1', 'field2': 'new_value2'})

        # Read
        value = redis_crud.read('my_key1')
        print('Read:', value)

        # Delete
        # redis_crud.delete('my_key1')

        # Read
        value = redis_crud.read('my_key1')
        print('Read:', value)
    """

    def __init__(self, host='0.0.0.0', port=6379, db=5):
        self.host = host
        self.port = port
        self.db = db

    @cached_property
    def redis_client(self):
        return redis.StrictRedis(host=self.host, port=self.port, db=self.db)


class RedisExpiryStore(RedisBase):

    def create(self, key, value, expiration_seconds):
        def json_encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            if isinstance(obj, ObjectId):
                return str(obj)
            if isinstance(obj, Binary):
                return str(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        data = {
            'value': value,
            'expiration_time': (datetime.datetime.now() + datetime.timedelta(seconds=expiration_seconds)).isoformat()
        }
        self.redis_client.setex(key, expiration_seconds, json.dumps(data, default=json_encoder))

    def read(self, key):
        data = self.redis_client.get(key)
        if data:
            data = json.loads(data)
            return data['value']
        return None

    def update(self, key, new_value, expiration_seconds):
        if self.redis_client.exists(key):
            data = {
                'value': new_value,
                'expiration_time': (datetime.datetime.now() + datetime.timedelta(seconds=expiration_seconds)).isoformat()
            }
            self.redis_client.setex(key, expiration_seconds, json.dumps(data))
        else:
            raise KeyError(f"Key '{key}' not found")

    def delete(self, key):
        if self.redis_client.exists(key):
            self.redis_client.delete(key)
        else:
            raise KeyError(f"Key '{key}' not found")

    def is_expired(self, key):
        if self.redis_client.exists(key):
            data = json.loads(self.redis_client.get(key))
            expiration_time = datetime.datetime.fromisoformat(data['expiration_time'])
            return datetime.datetime.now() > expiration_time
        return True  # Key does not exist, treat it as expired


class RedisStore(RedisBase):

    def create(self, key, value):
        self.redis_client.set(key, json.dumps(value))

    def read(self, key):
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    def update(self, key, new_value):
        if self.redis_client.exists(key):
            self.redis_client.set(key, json.dumps(new_value))

    def delete(self, key):
        if self.redis_client.exists(key):
            self.redis_client.delete(key)


redis_expr_store = None
try:
    redis_expr_store = RedisExpiryStore(
        # host=settings.REDIS_HOST if settings.REDIS_HOST else "0.0.0.0",
        # port=settings.REDIS_PORT if settings.REDIS_PORT else "6379"
    )
    redis_store = RedisStore(
        # host=settings.REDIS_HOST if settings.REDIS_HOST else "0.0.0.0",
        # port=settings.REDIS_PORT if settings.REDIS_PORT else "6379"
    )
except Exception as err:
    pass
