from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from .myusermanager import MyUserManager
import datetime
from django.utils import timezone
import random
import hashlib



class MyUser(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=64, blank=True, null=True)  # Storing hashed OTP
    otp_create_time = models.DateTimeField(auto_now=True)
    is_customer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    meli_code = models.CharField(max_length=10, blank=True, unique=True, null=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.mobile
        super().save(*args, **kwargs)
        
    def generate_otp(self):
        otp = str(random.randint(100000, 999999))
        self.otp = otp
        self.otp_create_time = timezone.now()
        self.save()
        print(f"Generated OTP for {self.mobile}: {otp}")
        return otp
     
    def is_otp_valid(self, otp):
        is_valid = (
            self.otp == otp and 
            timezone.now() - self.otp_create_time < timezone.timedelta(minutes=5)
        )
        return is_valid
       

class Customer(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField()
    # Address
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=10)
    meli_code = models.CharField(max_length=10, blank=True ,unique=True, null=True,)

class Seller(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='seller_profile')
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    shop_name = models.CharField(max_length=100, null=True, blank=True)
    shop_address = models.CharField(max_length=200, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    since_date = models.DateField()
    meli_code = models.CharField(max_length=10, blank=True ,unique=True, null=True,)


