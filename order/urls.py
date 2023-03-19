from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'order'

urlpatterns = [
    path('place_order/', views.placeOrder, name='place_order'),
    path('proceed_to_pay/',views.razorPayCheck,name="razorpaycheck"),
    
    path('myorders/', views.myOrders, name='myorders'),
    path('vieworder/<int:id>/',views.viewOrder, name='vieworder'),
    path('cancel-order/<int:id>/',views.cancelOrder, name='cancel_order'),
    path('order-complete/',views.orderComplete, name='order_complete'),
]