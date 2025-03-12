# django imports
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.validators import EmailValidator, ValidationError

# internal imports
from apps.common.exception import CustomValidationError

# others imports
import jwt
import datetime
import dns.resolver
from celery import shared_task


class InvitationTokenManager:

    @staticmethod
    def generate_invitation_token(payload):
        """
        Generate a JWT token for an invitation.

        Args:
            payload (dict): payload data.

        Returns:
            str: The JWT token for the invitation.
        """
        email_invitation_expiry_hour = int(settings.EMAIL_INVITATION_EXPIRY_HOUR)  # Token expiration default time s 72 hours
        payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=email_invitation_expiry_hour)
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token

    @staticmethod
    def validate_invitation_token(invitation_token):
        """
        Check the validity of an invitation token and decode its payload.

        Args:
            invitation_token (str): The JWT invitation token.

        Returns:
            dict: The decoded payload if the token is valid.
            dict: A message indicating that the invitation link has expired if the token is expired.
            dict: A message indicating that the invitation link is invalid if the token cannot be decoded.
        """

        try:
            payload = jwt.decode(invitation_token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise CustomValidationError("招待リンクの有効期限が切れました。")
        except jwt.DecodeError:
            raise CustomValidationError("無効な招待リンクです！")


class EmailManager(InvitationTokenManager):

    @staticmethod
    def is_valid_domain(hostname):
        '''
            This function will validate whether a host/domain
            is a valid MX record or not
        '''

        try:
            # getting  MX records
            mx_records = dns.resolver.resolve(hostname, 'MX')
            mx_records = [exdata for exdata in mx_records]

            # if a_records or mx_records:
            if mx_records:
                return True
            else:
                return False

        except:
            return False

    @staticmethod
    def is_valid_emails(emails: list):
        '''
            this function will validate a list of emails
            each email will validate by Django EmailValidator
            and also validate email domain
        '''

        email_validator = EmailValidator()
        for email in emails:
            try:
                email_validator(email)
            except ValidationError:
                return False, {"detail": f"Invalid email format: {email}", "detail_jp": f"無効な電子メール形式: {email}"}

            # get domain name from email
            email_domain_name = email.split("@")[-1]

            # check valid domain
            if not EmailManager.is_valid_domain(email_domain_name):
                return False, {"detail": f"Invalid domain: {email}", "detail_jp": f"無効なドメイン: {email}"}

        return True, "All emails are valid"


    @staticmethod
    @shared_task
    def send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=None):
        send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)



    @staticmethod
    @shared_task
    def send_otp(email, otp, expired_min, language='en'):
        """
        Send an invitation email to a recipient to join the team.

        Parameters:
        - email (str): The recipient's email address.
        """

        subject = 'iFLEET認証コード'
        message = \
            f'''
                 認証コード: {otp}

                 上記の認証コードをiFLEETの画面に入力し、認証を完了してください。
                 このコードは発行後
                 {expired_min}
                 分間有効です。有効期限が切れた場合は、再度認証コードを送信してください。

                 ※このメールは送信専用です。ご質問や返信には対応できませんので、ご了承ください。
             '''

        EmailManager.send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    @staticmethod
    @shared_task
    def send_member_invitation(payload, language='en'):
        """
        Send an invitation email to a recipient to join the team.

        Parameters:
        - email (str): The recipient's email address.
        """

        invitation_token = InvitationTokenManager.generate_invitation_token(payload)
        invitation_link = settings.USER_ACTIVATION_URL + invitation_token
        template_name = 'member_invitation.html'
        subject = 'iFLEET | Accept Invitation and Join iFLEET'

        message = render_to_string(
            template_name,
            {
                'invitation_link': invitation_link,
                "sender_email": settings.DEFAULT_EMAIL,
                "expiry_hour": settings.EMAIL_INVITATION_EXPIRY_HOUR
            }
        )

        # Check if the email sends successfully
        EmailManager.send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_EMAIL,
            recipient_list=[payload["email"]],
            fail_silently=False,
            html_message=message
        )

    @staticmethod
    @shared_task
    def send_registration_email(pyload, language='en'):
        """
        Send an invitation email to a recipient to join the team.

        Parameters:
        - email (str): The recipient's email address.
        """

        invitation_token = InvitationTokenManager.generate_invitation_token(pyload)
        invitation_link = settings.USER_ACTIVATION_URL + invitation_token

        template_name = 'member_invitation.html'
        subject = 'iFLEET | Accept Invitation and Join iFLEET'

        message = render_to_string(
            template_name,
            {
                'invitation_link': invitation_link,
                "sender_email": settings.DEFAULT_EMAIL,
                "expiry_hour": settings.EMAIL_INVITATION_EXPIRY_HOUR
            }
        )
        EmailManager.send_mail(
            subject=subject,
            message="",  # Leave the message empty. it's for text msg
            from_email=settings.DEFAULT_EMAIL,
            recipient_list=[pyload["email"]],
            fail_silently=False,
            html_message=message  # Set the content type to HTML
        )
