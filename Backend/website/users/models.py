from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from .myusermanager import MyUserManager
from django.utils import timezone
import random
import hashlib
from datetime import datetime, timedelta
from django.utils.timezone import now



class MyUser(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)  # Store 6-digit OTP
    otp_create_time = models.DateTimeField(auto_now=True)  # Store OTP creation time
    is_customer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    meli_code = models.CharField(max_length=10, blank=True, unique=True, null=True)
    is_verified = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.mobile
        super().save(*args, **kwargs)
        
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
        self.otp_create_time = now()  # Use timezone-aware `now()`
        self.save()
        print(f"Generated OTP for {self.mobile}: {self.otp}")
        return self.otp
    
    def is_otp_valid(self, otp):
        # Check if the entered OTP matches the saved one and is within the validity period
        if self.otp == otp:
            if self.otp_create_time:
                # OTP validity: 10 minutes
                otp_expiry_time = timedelta(minutes=10)
                if now() <= self.otp_create_time + otp_expiry_time:  # Use timezone-aware `now()`
                    return True
        return False
       

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
    is_approved = models.BooleanField(default=False)  # Admin approval
    business_license = models.FileField(upload_to='licenses/', null=True, blank=True)  # For verification

    def __str__(self):
        return self.shop_name or self.user.username
