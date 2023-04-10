import datetime

from django.db import models
from dateutil.relativedelta import relativedelta


# Create your models here.
class Subscription(models.Model):
    subscriber_id = models.IntegerField()
    magazine_id = models.IntegerField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    @staticmethod
    def create_subscription(magazine_id, frequency, time_amount, user_id):
        start_date = datetime.date.today()
        frequency_delta = Subscription.FREQUENCY_DELTA_MAP.get(frequency)
        end_date = start_date + frequency_delta * time_amount
        subscription = Subscription(subscriber_id=user_id, magazine_id=magazine_id, start_date=start_date,
                                    end_date=end_date)
        return subscription

    def increase_end_date(self, time_amount, frequency):
        frequency_delta = Subscription.FREQUENCY_DELTA_MAP.get(frequency)
        self.end_date += frequency_delta * time_amount

    FREQUENCY_DELTA_MAP = {
        'daily': relativedelta(days=1),
        'weekly': relativedelta(weeks=1),
        'monthly': relativedelta(months=1),
        'quarterly': relativedelta(months=3),
        'biannual': relativedelta(months=6),
        'annual': relativedelta(years=1),
    }
