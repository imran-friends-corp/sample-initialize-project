# django imports
from django.conf import settings

# internal imports
from apps.common.redis import redis_expr_store, redis_store
from apps.common.exception import CustomValidationError

# other imports
from random import randint


OTP_SECRET_KEY = settings.OTP_SECRET_KEY
OTP_VERIFY_SECRET_KEY = settings.OTP_VERIFY_SECRET_KEY


class InvalidOTPException(Exception):
    pass


class OTP:

    @staticmethod
    def generate_otp_code():
        """
        Generate a random OTP code.

        Returns:
        str: A randomly generated 6-digit OTP code.
        """
        return randint(100000, 999999)

    @staticmethod
    def otp_secret_key(key):
        """
        Generate a random OTP code.

        Returns:
        str: A randomly generated 6-digit OTP code.
        """

        return f'{key}_{OTP_SECRET_KEY}'

    @staticmethod
    def otp_verify_secret_key(key):
        """
        Generate a random OTP code.

        Returns:
        str: A randomly generated 6-digit OTP code.
        """

        return f'{key}_{OTP_VERIFY_SECRET_KEY}'

    @classmethod
    def is_valid(cls, email, user_otp):
        # Retrieve the stored OTP from Redis
        cache_key = cls.otp_secret_key(email)
        stored_otp = redis_expr_store.read(cache_key)
        if user_otp == stored_otp:
            return True
        raise CustomValidationError("コードの有効期限が切れているか無効です")

    @classmethod
    def create(cls, email):
        cache_key = cls.otp_secret_key(email)
        otp = OTP.generate_otp_code()

        # Calculate the expiration time in seconds
        expiration_seconds = int(str(settings.OTP_EXPIRY_MIN)) * 60

        # Store the OTP in Redis with the desired expiration time
        redis_expr_store.create(cache_key, otp, expiration_seconds)
        return otp, settings.OTP_EXPIRY_MIN

    @classmethod
    def is_verified(cls, email):
        key = cls.otp_verify_secret_key(email)
        if not redis_expr_store.read(key):
            raise CustomValidationError(f"{email}: OTP 検証が見つかりません!")

    @classmethod
    def create_verified(cls, email):
        key = cls.otp_verify_secret_key(email)
        expiration_seconds = 30*60
        redis_expr_store.create(key, True, expiration_seconds)

    @classmethod
    def delete_verified(cls, email):
        key = cls.otp_verify_secret_key(email)
        redis_expr_store.delete(key)
