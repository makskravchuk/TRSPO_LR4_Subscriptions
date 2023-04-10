from django.urls import path

from subscriptions.views import SubscriptionAPIView, SubscriptionListAPIView

urlpatterns = [path("subscriptions/", SubscriptionListAPIView.as_view()),
               path("create-subscription/", SubscriptionAPIView.as_view()),
               path("subscription/<int:pk>", SubscriptionAPIView.as_view()), ]
