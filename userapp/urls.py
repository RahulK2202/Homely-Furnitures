from django.urls import path
from.import views
from django.contrib.auth import views as auth_views

app_name = 'userapp'

urlpatterns = [
    path('',views.home,name='home'),
    path('login/', views.login, name='login'),

    path('logout',views.logout,name='logout'),
    path('register/',views.register,name='user_register'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('changepassword',views.changepassword,name='changepassword'),

    path('forgotPassword/',views.forgotPassword, name="forgotPassword"),
    path('resetpassword_validate/<uidb64>/<token>',views.resetpassword_validate, name="resetpassword_validate"),
    path('resetPassword/',views.resetPassword, name="resetPassword"),
    path('viewprofile/',views.viewprofile,name='viewprofile'),

    path('viewAddresses/',views.viewAddresses,name='viewAddresses'),
    path('addNewAddress/<int:form_from>/',views.addNewAddress,name='addNewAddress'),
    path('editAddress/<int:address_id>/',views.editAddress ,name='editAddress'),
    path('deleteAddress/<int:address_id>/',views.deleteAddress ,name='deleteAddress'),

]
