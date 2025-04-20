from ekartapp import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('checkout/', views.checkout, name="checkout"),
    path('profile',views.profile,name="profile"),
    path('search',views.search,name="search"),
    path('cancelorder/<id>', views.cancelorder, name="cancelorder"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('dashboard/addProduct', views.addProduct, name="addProduct"),
    path('dashboard/editProduct/<id>', views.editProduct, name="editProduct"),
    path('dashboard/deleteProduct/<id>', views.deleteProduct, name="deleteProduct"),
]
