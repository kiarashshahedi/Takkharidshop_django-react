from django.test import TestCase
from .models import MyUser, Customer, Seller



class test_customer_registering(TestCase):

    @classmethod
    def setUpTestData(cls):

        test_customer = Customer.objects.create(mobile = '32342123212')
        return super().setUpTestData()