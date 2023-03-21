from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'adminapp'

urlpatterns = [
    path('adminhome/', views.adminHome, name="adminhome"),
    path('', views.adminLogin, name='adminlogin'),
    path('admindashboard/', views.adminDashboard, name="admindashboard"),

    path('addcategory/', views.addCategory, name="addcategory"),
    path('viewcategory', views.viewCategory, name="viewcategory"),
    path('editcategory/<int:pid>/', views.editCategory, name="editcategory"),
    path('deletecategory/<int:pid>/', views.deleteCategory, name="deletecategory"),

    path('addproduct/', views.addProduct, name='addproduct'),
    path('viewproduct/', views.viewProduct, name='viewproduct'),
    path('editproduct/<int:pid>/', views.editProduct, name='editproduct'),
    path('deleteproduct/<int:pid>/', views.deleteProduct, name="deleteproduct"),

    path('manageuser/', views.manageUser, name="manageuser"),
    path('viewusers/', views.viewUsers, name="viewusers"),
    path('<int:u_id>/userblock/', views.userBlock, name='userblock'),

    path('manageorder/', views.manageOrder, name="manageorder"),
    path('updateorder/<int:id>',views.updateOrder,name="updateorder"),

    path('adminlogout', views.adminLogout, name='adminlogout'),
    path('addcoupon/', views.addCoupon, name="addcoupon"),
    path('viewcoupon/', views.viewCoupon, name="viewcoupon"),

    path('editcoupon/<int:pid>/', views.editCoupon, name='editcoupon'),
    path('deleteCoupon/<int:pid>/', views.deleteCoupon, name="deletecoupon"),

    path('trigeremail', views.trigerEmail, name="trigeremail"),
    path('searchUser/',views.searchUser,name="searchuser"),
    path('searchOrder/',views.searchOrder,name="searchorder"),
    path('searchCategory/',views.searchCategory,name="searchcategory"),
    path('searchProduct/',views.searchProduct,name="searchproduct"),
    path('searchCoupon/',views.searchCoupon,name="searchcoupon"),
    path('vieworder/<int:id>', views.viewOrder, name="vieworder"),
    path('searchManageUser/',views.searchManageUser,name="searchmanageuser"),



]