from django.contrib import admin
from .models import Student
from .models import Profile
from .models import Account
from .models import Transaction
from .models import KYCDocument

# Register your models here.
admin.site.register(Student)
admin.site.register(Profile)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(KYCDocument)