from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from json import dumps
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from ..forms import *
from ..tasks import *
from ..models import *
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.cache import cache_page
from django.utils import timezone



@login_required(login_url='login_page')
def dashboard(request):
    form = ElectricalBill(request.POST or None)
    measurements = []
    saved_bill = False
    
    if request.user.is_authenticated:
        saved_bill, created = Electrical_Bill.objects.get_or_create(id=1)

        if request.method == 'POST':
            report_device = request.POST.getlist('report_device')
            report_measure = request.POST.getlist('report_measure')
            
            # Save the selected values
            saved_bill.devices = report_device
            saved_bill.measures = report_measure
            saved_bill.save()

        elif saved_bill:
            print("here")
            report_device = eval(saved_bill.devices)
            report_measure = eval(saved_bill.measures)


        for string in report_measure:
            print("string", string)
            for value in report_device:
                print("value ",value)
                if value in string:
                    try:
                        IDs = Device.objects.get(device_name=value)
                    except Device.DoesNotExist:
                        continue
                    
                    parts = string.split(value, 1)
                    if len(parts) == 2:
                        part1 = parts[0].strip(", :;")
                        part2 = value
                        
                        # Find the register for this combination
                        register_values = Register.objects.filter(name=part1, channel=IDs).last()
                        if register_values:
                            try:
                                first_modbus_data = ModbusData.objects.filter(
                                    device_id=register_values.channel_id, 
                                    register_id=register_values.id,
                                    value__gt=0
                                ).first()
                                
                                last_modbus_data = ModbusData.objects.filter(
                                    device_id=register_values.channel_id, 
                                    register_id=register_values.id,
                                    value__gt=0
                                ).last()
                                
                                first_value = first_modbus_data.value if first_modbus_data else "N/A"
                                last_value = last_modbus_data.value if last_modbus_data else "N/A"

                                first_local_timestamp = timezone.localtime(first_modbus_data.timestamp, timezone.get_current_timezone())  
                                last_local_timestamp = timezone.localtime(last_modbus_data.timestamp, timezone.get_current_timezone())  

                                total_measure = round((float(last_value) - float(first_value)))

                                measurements.append({
                                    'device': part2,
                                    'measure': part1,
                                    'first_value': first_value + register_values.parameter_name,
                                    'last_value': last_value + register_values.parameter_name,
                                    'total_measure': f"{total_measure}  {register_values.parameter_name}",
                                    'first_time': first_local_timestamp.strftime("%Y %b %d %I:%M %p"),
                                    'last_time': last_local_timestamp.strftime("%Y %b %d %I:%M %p"),
                                    'cost': f'{total_measure * 0.18} SAR'
                                })

                            except Exception as e:
                                print(f"Error fetching Modbus data: {e}")
                                continue

    context = {'form': form, 'measurements': measurements}
    return render(request, 'dashboard.html', context)