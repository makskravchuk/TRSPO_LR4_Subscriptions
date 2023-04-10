import requests
from rest_framework.permissions import BasePermission

from subscriptions import views


class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        token = views.get_token(request)
        if token:
            data = {'token': token}
            url = "http://172.20.0.2:8001/api/v1/is_admin/"
            response = requests.post(url=url, json=data)
            if response.status_code == 200:
                data = response.json()
                return bool(data['is_admin'])
        return False


class IsAuthenticatedPermission(BasePermission):
    def has_permission(self, request, view):
        token = views.get_token(request)
        if token:
            data = {'token': token}
            url = "http://172.20.0.2:8001/api/v1/is_authenticated/"
            response = requests.post(url=url, json=data)
            if response.status_code == 200:
                data = response.json()
                return bool(data['is_authenticated'])
        return False



