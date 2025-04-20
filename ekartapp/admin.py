from django.contrib import admin
from .models import Product,Orders,OrderUpdate,Contact
# Register your models here.
admin.site.register(Product)
admin.site.register(Orders)
admin.site.register(OrderUpdate)
admin.site.register(Contact)