# other import
import json
import uuid
from datetime import datetime, timezone, timedelta

from asgiref.sync import async_to_sync

from apps.base.exception import CustomValidationError
from apps.common.mongo import MongoDBClient


def generate_unique_uuid(model):

    new_uuid = uuid.uuid4()
    while model.objects.filter(uuid=new_uuid).exists():
        new_uuid = uuid.uuid4()
    return new_uuid


def parse_date(date, is_end_of_month=False, is_required=False):
    if not date and is_required:
        raise CustomValidationError(
            {
                'detail': 'entry_date is required as a query parameter',
                'detail_jp': 'クエリパラメータとして entry_date が必要です。'
            })

    if date:
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            raise CustomValidationError(
                {
                    'detail': 'Invalid date format. Expected format is YYYY-MM-DD.',
                    'detail_jp': '日付の形式が無効です。正しい形式は YYYY-MM-DD です。'
                }
            )

    return date


def convert_datetime_from_string(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)


def send_websocket_update(group_name, message_type, data):
    """
    Sends data to a specified WebSocket group.

    Parameters:
    - group_name: The name of the WebSocket group to send the message to.
    - message_type: The type of message being sent.
    - data: The data payload for the message, typically a dictionary or list.

    Example usage:
    send_websocket_update('driver_location_updates', 'send_location_update', driver_locations)
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': message_type,
            'data': data
        }
    )



class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def serialize_data(data):
    """
    Helper function to recursively convert UUIDs in the data to strings.
    """
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, uuid.UUID):
        return str(data)
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    return data


