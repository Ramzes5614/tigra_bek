from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Account,Profile,TigraAdmin
from basicauth import decode
from django.contrib.auth import authenticate
from accounts.serializers import ProfileSerializer

class IncreaseCounter(APIView):

    @staticmethod
    def post(request, phone):
        phone_number = phone
        account = Account.objects.get(phone_number=phone_number)
        profile = Profile.objects.get(account=account)
        profile.visit_counter += 1
        profile.save()
        if profile.visit_counter % 5 == 0:
            return Response({"ticket":"You have a free ticket","visits":f"{profile.visit_counter}"})
        else:
            return Response({"ticket":"You dont have a free ticket","visits":f"{profile.visit_counter}"})

    @staticmethod
    def get(request,phone):
        phone_number = phone
        account = Account.objects.get(phone_number=phone_number)
        profile = Profile.objects.get(account=account)
        return Response({"visits":f"{profile.visit_counter}"})

class LoginAccount(APIView):
    @staticmethod
    def get(request):
        phone_number,password = decode(request.headers['Authorization'])
        print(phone_number,password)
        account = authenticate(username=phone_number,password=password)
        if account is not None:
            profile = Profile.objects.get(account=account)
            serializer = ProfileSerializer(profile)
            return Response({"profile":serializer.data, "authorized":"true"})
        else:
            return Response({"authorized":"false"})

class GetAccounts(APIView):
    @staticmethod
    def get(request):
        profiles = Profile.objects.filter(visit_counter__gte=1).order_by("-account")
        serializers = ProfileSerializer(profiles,many=True)
        return Response(serializers.data)

class LoginTigraAdmin(APIView):
    @staticmethod
    def post(request):
        username,password = decode(request.headers['Authorization'])
        print("username "+username+"password "+password)
        account = TigraAdmin.objects.filter(password=password,username=username).count()
        if(account > 0):
            return Response({"status":"successfully logged in"})
        else:
            return Response({"status":"failed to log in"})
