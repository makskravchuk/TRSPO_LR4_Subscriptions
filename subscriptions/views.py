import requests
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from subscriptions.models import Subscription
from subscriptions.permissions import IsAuthenticatedPermission, IsAdminPermission
from subscriptions.serializers import SubscriptionSerializer, EditionChoiceSerializer


# Create your views here.
class SubscriptionListAPIView(ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @method_decorator(cache_page(60))
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class SubscriptionAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == "GET":
            return [IsAuthenticatedPermission()]
        else:
            return [IsAdminPermission()]

    @method_decorator(cache_page(60))
    def get(self, request, pk):
        subscription = Subscription.objects.get(pk=pk)
        serializer = SubscriptionSerializer(subscription)
        return Response(data=serializer.data)

    def post(self, request):
        serializer = EditionChoiceSerializer(data=request.data)
        if serializer.is_valid():
            magazine_id = serializer.validated_data['magazine_id']
            time_amount = serializer.validated_data['time_amount']
            magazine = get_magazine(magazine_id)
            user_id = get_user_id(get_token(request))
            if user_id and magazine:
                if not Subscription.objects.filter(subscriber_id=user_id, magazine_id=magazine_id).exists():
                    subscription = Subscription.create_subscription(magazine_id, magazine['frequency'], time_amount,
                                                                    user_id)
                    subscription.save()
                else:
                    subscription = Subscription.objects.filter(subscriber_id=user_id, magazine_id=magazine_id).first()
                    subscription.increase_end_date(time_amount, magazine['frequency'])
                    subscription.save()
                status = create_payment(subscription_id=subscription.pk, price=magazine['price'], time_amount=time_amount,token=get_token(request))
                return Response(status=status)
        return Response(status=406)

    def delete(self, request, pk):
        try:
            Subscription.objects.filter(pk=pk).delete()
        except:
            return Response({"error": "Object does not exists"})
        return Response(status=200)


def get_user_id(token):
    if token:
        data = {'token': token}
        url = "http://172.20.0.2:8001/api/v1/get-user-id/"
        response = requests.post(url=url, json=data)
        if response.status_code == 200:
            data = response.json()
            return data["user_id"]
    return None


def get_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header.startswith('Token '):
        token = auth_header[len('Token '):]
        return token
    return None


def get_magazine(magazine_id):
    url = f"http://172.20.0.3:8002/api/v1/magazine/{magazine_id}"
    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
        return data
    return None


def create_payment(subscription_id, price, time_amount,token):
    data = {'subscription_id': subscription_id, "price": price, "time_amount": time_amount}
    headers = {'Authorization': f"Token {token}"}
    url = "http://172.20.0.5:8004/api/v1/create-payment/"
    response = requests.post(url=url, json=data,headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    return response.status_code
