from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import pyotp
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import phoneModel
import base64
import requests
from requests.auth import HTTPBasicAuth
from accounts.models import Account,Profile

SMS_AERO_API_KEY = "p56Y8j13AhS5mvN1WUXdtDnNeGF"
SMS_AERO_USERNAME = "savrulloevsunrise@gmail.com"
SMS_AERO_URL = "https://email:api_key@gate.smsaero.ru/v2/sms/send"

# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"


class getPhoneNumberRegistered(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def get(request, phone):
        try:
            Mobile = phoneModel.objects.get(phone_number=phone)  # if Mobile already exists the take this else create New One
        except ObjectDoesNotExist:
            phoneModel.objects.create(
                phone_number=phone,
            )
            Mobile = phoneModel.objects.get(phone_number=phone)  # user Newly created Model
        Mobile.counter += 1  # Update Counter At every Call
        Mobile.save()  # Save the data
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Key is generated
        OTP = pyotp.HOTP(key)  # HOTP Model for OTP is created
        print(OTP.at(Mobile.counter))
        custom_params = {
            "number":phone,
            "text":f"Your one time code is: {OTP.at(Mobile.counter)}",
            "sign":"SMS Aero"
        }
        requests.get(
            url = SMS_AERO_URL,
            params=custom_params,
            auth=HTTPBasicAuth(SMS_AERO_USERNAME,SMS_AERO_API_KEY)
        ) #same as Http Basic auth
        # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
        return Response({"otp": OTP.at(Mobile.counter)}, status=200)  # Just for demonstration

    # This Method verifies the OTP
    @staticmethod
    def post(request, phone):
        try:
            Mobile = phoneModel.objects.get(phone_number=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
        OTP = pyotp.HOTP(key)  # HOTP Model
        if OTP.verify(request.data["otp"], Mobile.counter):  # Verifying the OTP
            Mobile.isVerified = True
            Mobile.save()
            first_name = request.data["first_name"]
            last_name = request.data['last_name']
            child_name = request.data['child_name']
            phone_number = phone
            password = request.data['password']
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,password=password,phone_number=phone_number)
            user.save()
            if child_name == "null":
                account = Profile.objects.create(account=user,visit_counter=0)
            else:
                account = Profile.objects.create(account=user,visit_counter=0,child_name=child_name)
            account.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong", status=400)

# Time after which OTP will expire
EXPIRY_TIME = 1020 # seconds

class getPhoneNumberRegistered_TimeBased(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def get(request, phone):
        user = Account.objects.filter(phone_number=phone).count()
        mobile = phoneModel.objects.filter(phone_number=phone).count()
        if user > 0:
            return Response("Phone number already exists")
        elif mobile > 0:
            Mobile = phoneModel.objects.get(phone_number=phone)
        else:
            phoneModel.objects.create(
                phone_number=phone,
            )
            Mobile = phoneModel.objects.get(phone_number=phone)
        Mobile.save()  # Save the data
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Key is generated
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model for OTP is created
        print(OTP.now())
        custom_params = {
            "number":phone,
            "text":f"Your one time code is: {OTP.now()}",
            "sign":"SMS Aero"
            }
        r = requests.get(
            url = SMS_AERO_URL,
            params=custom_params,
            auth=HTTPBasicAuth(SMS_AERO_USERNAME,SMS_AERO_API_KEY)
            )
        # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
        return Response({"OTP": OTP.now(),"Responded":r.json()}, status=200)  # Just for demonstration

    # This Method verifies the OTP
    @staticmethod
    def post(request, phone):
        try:
            Mobile = phoneModel.objects.get(phone_number=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model 
        if OTP.verify(request.data["otp"]):  # Verifying the OTP
            Mobile.isVerified = True
            Mobile.save()
            first_name = request.data["first_name"]
            last_name = request.data['last_name']
            child_name = request.data['child_name']
            phone_number = phone
            password = request.data['password']
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,password=password,phone_number=phone_number)
            user.save()
            if child_name == "null":
                account = Profile.objects.create(account=user,visit_counter=0)
            else:
                account = Profile.objects.create(account=user,visit_counter=0,child_name=child_name)
            account.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong/expired", status=400)

class forgotPassword(APIView):
    @staticmethod
    def get(request,phone):
        account_num = Account.objects.filter(phone_number=phone).count()
        if account_num > 0:
            keygen = generateKey()
            key = base64.b32encode(keygen.returnValue(phone).encode())  # Key is generated
            OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model for OTP is created
            print(OTP.now())
            custom_params = {
                "number":phone,
                "text":f"Code to reset the password: {OTP.now()}",
                "sign":"SMS Aero"
            }
            r = requests.get(
                url = SMS_AERO_URL,
                params=custom_params,
                auth=HTTPBasicAuth(SMS_AERO_USERNAME,SMS_AERO_API_KEY)
            )
            return Response({"OTP": OTP.now(),"Responded":r.json()}, status=200) 
        else:
            return Response("Phone number is not registered")
    @staticmethod
    def post(request,phone):
        account_num = Account.objects.filter(phone_number=phone).count()
        if account_num > 0:
            keygen = generateKey()
            key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
            OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model 
            print(OTP.now())
            if OTP.verify(request.data["otp"]):
                return Response("Phone number found", status=200)
            return Response("OTP is wrong/expired", status=400)

class ResetPassword(APIView):
    @staticmethod
    def post(request,phone):
        password = request.data['password']
        account = Account.objects.get(phone_number=phone)
        account.set_password(password)
        account.save()
        return Response("Password changed successfully", status=200)