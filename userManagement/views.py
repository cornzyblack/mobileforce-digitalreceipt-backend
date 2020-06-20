import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import api_view
import random as r

from services.email_verification import GmailObject
from .models import User
from .serializers import UserSerializer


def otpgen():
    otp = ""
    for i in range(4):
        otp += str(r.randint(1, 9))
    return otp


def emailOtpMessage(otp):
    html = """
            <html>
                <body>
                    <p>Hello,<br><br>
                    Thanks for registering in our application<br><br>
                    Please verify your OTP. Your OTP number is below
                    <br><br>
                     <b>""" + otp + """</b>
                    </p>
                </body>
            </html>
        """
    return html


@api_view(['POST'])
def user_registration_send_email(request):
    if request.method == 'POST':
        email_address = request.data['email_address']
        try:
            validate_email(email_address)
        except ValidationError as e:
            return JsonResponse({
                "error": "Enter correct email address"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Check if there is any user with this email address
            try:
                userData = User.objects.get(email_address=request.data['email_address'])
            except User.DoesNotExist:
                otp = otpgen()
                try:
                    GmailObject.gm.send_message("Email OTP Verification - Digital Receipt", emailOtpMessage(otp),
                                                request.data['email_address'])
                    return JsonResponse({
                        "data": {
                            "otp":otp,
                            "email_address":request.data['email_address']
                        },
                        "message":"Sent email with otp successfully"
                    }, status=status.HTTP_200_OK)
                except Exception as error:
                    return JsonResponse({
                        "error": error
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({
                    "error": e
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({
                    "error": "Email Already exists"
                }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        try:
            validate_email(request.data['email_address'])
        except ValidationError as e:
            return JsonResponse({
                "error": "Enter correct email address"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
