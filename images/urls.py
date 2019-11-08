from django.urls import path
from .views import home, Login, Logout, newClient, clientDetail, passwordView,useroperationView,passwordChangeView,expireClientView,deleteClientView, imageDeleteView,driveView,syncView
urlpatterns = [
    path('', home,name='dashboard'),
    path('login/',Login,name='login'),
    path('logout/',Logout, name = 'logout'),
    path('newClient/',newClient, name = 'newclient'),
    path('clientdetail/<str:client>',clientDetail,name = 'clientdetail'),
    path('expireClient/<str:client>',expireClientView,name='expire'),
    path('deleteClient/<str:client>',deleteClientView,name='delete'),
    path('deleteImage/<str:client>/<path:imagepath>',imageDeleteView, name='imgdelete'),
    path('passlist',passwordView,name='passwords'),
    path('mainuseroperation',useroperationView,name='operation'),
    path('passwordChange/',passwordChangeView,name='passchange'),
    path('drives/',driveView,name='drive'),
    path('syncdrive/<int:drive>',syncView),
    path('syncdrive',syncView),
    
]