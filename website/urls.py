
from django.urls import path, include
from . import views
from .view.dashboard import dashboard

urlpatterns = [
    path('', dashboard, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('user_manual/', views.user_manual_view, name='user_manual'),

    path('record/<int:pk>', views.customer_record, name='record'),
    # path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    # path('add_record/', views.add_record, name='add_record'),
    path('data_logs_devices/', views.data_logs_devices, name='data_logs_devices'),
    path('data_logs/<int:pk>', views.data_logs, name='data_logs'),


    path('devices/', views.devices, name='devices'),
    path('dashboard/', dashboard, name='dashboard'),

    path('add_device/', views.add_device, name='add_device'),
    path('update_device/<int:pk>', views.update_device, name='update_device'),
    path('delete_device/<int:pk>', views.delete_device, name='delete_device'),
    path('discover_ip', views.discover_ip, name='discover_ip'),

    path('addresses/', views.addresses, name='addresses'),
    path('register_addresses/<int:pk>', views.register_addresses, name='register_addresses'),
    path('delete_addresses/<int:pk>', views.delete_addresses, name='delete_addresses'),
    path('update_address/<int:pk>', views.update_address, name='update_address'),

    path('charts/', views.charts, name='charts'),

    path('reports/', views.reports, name='reports'),
    path('add_report/', views.add_report, name='add_report'),
    path('delete_report/<int:pk>', views.delete_report, name='delete_report'),
    path('update_report/<int:pk>', views.update_report, name='update_report'),
    path('send-report/<int:report_id>/', views.trigger_email_report, name='send_report'),
    path('download-report/<int:report_id>/', views.trigger_download_report, name='download_report'),

    path('alarms/', views.alarms, name='alarms'),
    path('pre_add_alarm/', views.pre_add_alarm, name='pre_add_alarm'),
    path('add_alarm/<int:pk>', views.add_alarm, name='add_alarm'),
    path('update_alarm/<int:pk>', views.update_alarm, name='update_alarm'),
    path('delete_alarm/<int:pk>', views.delete_alarm, name='delete_alarm'),
    path('reset_alarm/<int:pk>', views.reset_alarm, name='reset_alarm'),

    path('user_page/', views.user_page, name='user_page'),

    path('historical_data_logs/', views.historical_data_logs, name='historical_data_logs'),
    path('historical_data/<str:table_name>/', views.historical_data, name='historical_data'),
    path('historical-data/<str:table_name>/<int:device_id>/', views.historical_data_by_device_id, name='historical_data_by_device_id'),
    
    path('diagrams', views.diagrams, name='diagrams'),
    path('diagrams/<int:pk>', views.diagrams_device, name='diagrams_device'),
    path('diagrams_chart_data/<str:name>/', views.diagrams_chart_data, name='diagrams_chart_data'),
    path('diagrams_chart_graph/<str:name>/', views.diagrams_chart_graph, name='diagrams_chart_graph'),
    path('diagrams_chart_graph_2/<str:name>/', views.diagrams_chart_graph_2, name='diagrams_chart_graph_2'),
    path('device-tree/', views.device_tree_view, name='device_tree_view'),
    path('device_tree_view_element/<int:pk>', views.device_tree_view_element, name='device_tree_view_element'),
]