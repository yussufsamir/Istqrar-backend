
# Register your models here.
# gameya/admin.py
from django.contrib import admin
from .models import Gameya, Membership, Contribution

admin.site.register(Gameya)
admin.site.register(Membership)
admin.site.register(Contribution)
