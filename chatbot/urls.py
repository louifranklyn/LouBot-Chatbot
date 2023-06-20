from django.contrib import admin
from django.urls import path,include

admin.site.site_header = "LouBot Admin"
admin.site.site_title = "LouBot Admin Portal"
admin.site.index_title = "Welcome to LouBot Researcher Portal"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('app.urls')),
    path('login/',include('app.urls')),
    path('signup/',include('app.urls')),
    path('contact/',include('app.urls')),
    path('chatbox/',include('app.urls')),
    path('get/',include('app.urls')),
]