from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('enquiry/submit/', views.submit_property_enquiry, name='submit_enquiry'),
    path('valuation/request/', views.request_valuation, name='request_valuation'),
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/<int:id>/', views.branch_detail, name='branch_detail'),
]
