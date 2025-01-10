from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from json import dumps
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from ordered_set import OrderedSet
from .forms import *
from .tasks import *
from .models import *
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from django.http import HttpResponse, JsonResponse, FileResponse
import serial.tools.list_ports as portlist
import nmap
from django.urls import reverse
from datetime import timedelta
from django.db import connection
from collections import OrderedDict
from .utils import can_add_device
from django.core.cache import cache
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from itertools import zip_longest
import random
from django.utils import timezone
import os
import timeit
import numpy as np

def user_manual_view(request):
    # file_path = os.path.join(settings.BASE_DIR, 'static', 'UserManual', 'UserManual_EnergyEye.pdf')
    return FileResponse(open("F:/BCMI-YAMAN-PILOT-TEST/DCRM_ALBADAHA_PROJECT/DCRM_A_Production_Work/website/static/UserManual/UserManual_EnergyEye.pdf", 'rb'), content_type='application/pdf')

def login_page(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print("im here")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, "Please Check Username and Password")
            return redirect('login_page')
    
   
    else:
        # print(request.POST)
        return render(request, 'login_page.html', {})

@login_required(login_url='login_page')
def home(request):
    records = Record.objects.all()
    current_user = request.user
    # print(current_user.id)

    return render(request, 'home.html', {'records':records, 'current_user':current_user})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('login_page')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Assign the user to the 'User' group
            user_group = Group.objects.get(name='User')
            user.groups.add(user_group)

            #authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'User registred successfully')
            return redirect('home')
    
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})
    
    return render(request, 'register.html', {'form':form})


def customer_record(request, pk):
    if request.user.is_authenticated:
        return render(request, 'record.html', {'request':request})
    
    else:
        messages.success(request, "You must be logged in to view this page")
        return redirect('home')
    
# def delete_record(request, pk):


#     if request.user.is_authenticated:
#         delete_it = Record.objects.get(id = pk)
#         delete_it.delete()
#         messages.success(request, "Record deleted...")
#         return redirect('home')
#     else:
#         messages.success(request, "You must be logged in to delete the record")
#         return redirect('home')

@login_required(login_url='login_page')
def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                add_record = form.save()
                messages.success(request, "Record Added...")
                return redirect('home')
        return render(request, 'add_record.html', {'form':form})
    else:
        messages.success(request, "Must be logged in to add record")
        return redirect('home')

@login_required(login_url='login_page')
def data_logs_devices(request):
    devices = Device.objects.all()

    return render(request, 'data_logs_devices.html', {'records':devices})




@login_required(login_url='login_page')
def devices(request):
    is_admin = request.user.groups.filter(name='Admin').exists()
    devices = Device.objects.all()

    return render(request, 'devices.html', {'devices':devices, "is_admin":is_admin})

@login_required(login_url='login_page')
def discover_ip(request):
    form = IPSearch(request.POST or None)

    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                IP_section1 = form.cleaned_data['IP_section1']
                IP_section2 = form.cleaned_data['IP_section2']
                IP_section3 = form.cleaned_data['IP_section3']
                start_ip = form.cleaned_data['start_ip']
                end_ip = form.cleaned_data['end_ip']
                
                available_devices = []
                try:
                    nm = nmap.PortScanner()
                    for i in range(int(start_ip), int(end_ip) + 1):
                        ip = f'{IP_section1}.{IP_section2}.{IP_section3}.{i}'
                        result = nm.scan(hosts=ip, arguments='-F')
                        if ip in result['scan']:
                            if nm[ip]['status']['state'] == 'up':
                                print(f"Host {ip} is reachable")
                                available_devices.append(ip)
                            else:
                                print(f"Host {ip} is not reachable")
                except Exception as e: 
                    messages.success(request, "there was an issue while scanning")
                    return redirect('discover_ip')
                
                request.session['available_devices'] = available_devices
                return redirect('add_device')            
            
            else:
                messages.success(request, "there was an issue while scanning")
                return redirect('discover_ip')
            
    return render(request, 'discover_ip.html', {'form':form})

@login_required(login_url='login_page')
def add_device(request):
    form = AddDeviceForm(request.POST or None)

    available_devices = request.session.pop('available_devices', [])

    com_ports = []
    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'auto_discover_com' in request.POST:
                for port in portlist.comports():
                    com_ports.append(port)

            elif form.is_valid():
                device_name = form.cleaned_data['device_name']
                if Device.objects.filter(device_name=device_name).exists():
                    messages.error(request, f"A device with the name '{device_name}' already exists.")
                
                else:    
                    can_add, message = can_add_device()
                    if not can_add:
                        messages.error(request, message)
                        return redirect('add_device')
                    else:
                        form.save()
                        messages.success(request, "Device added successfully.")
                        return redirect('devices')
        
        
        return render(request, 'add_device.html', {'form':form, 'discover_COM':com_ports, 'available_devices':available_devices})
    
    else:
        messages.success(request, "Failed to add Device")
        return redirect('devices')


@login_required(login_url='login_page')
def delete_device(request, pk):
    if request.user.is_authenticated:
        delete_it = Device.objects.get(id = pk)
        # print(delete_it.id)

        delete_it.delete()
        return redirect('devices')
    else:
        messages.success(request, "You must be logged in to delete the record")
        return redirect('devices')

@login_required(login_url='login_page')
def update_device(request, pk):
    device_record = Device.objects.get(id=pk)
    form = AddDeviceForm(request.POST or None, instance=device_record)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('devices')

    else:
        return render(request, 'update_device.html', {'form':form, "device_record":device_record})


@login_required(login_url='login_page')
def addresses(request):
    devices = Device.objects.all()

    return render(request, 'addresses.html', {'devices':devices})

@login_required(login_url='login_page')
def register_addresses(request, pk):
    is_admin = request.user.groups.filter(name='Admin').exists()
    selected_device = Device.objects.get(id=pk)

    registers = Register.objects.filter(channel=selected_device).order_by('-id')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            register = form.save(commit=False)
            register.channel = selected_device
            register.save()
            return redirect('register_addresses', pk=pk)
    else:
        form = RegisterForm()

    return render(request, 'register_addresses.html', {'selected_device':selected_device,'registers': registers, 'form': form, 'is_admin':is_admin})

def update_address(request, pk):
    register = Register.objects.get(id = pk)
    form = RegisterForm(request.POST or None, instance=register)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # print("Form is Valid")
            return redirect('register_addresses', pk=register.channel_id)
        
        else:
            messages.success(request, "Input Error ")
            return redirect('register_addresses', pk=register.channel_id)
        
    return redirect('register_addresses', pk=register.channel_id)

@login_required(login_url='login_page')
def delete_addresses(request, pk):
    if request.user.is_authenticated:
        delete_it = Register.objects.get(id = pk)
        # print(delete_it.id)
        delete_it.delete()
        return redirect('register_addresses', pk=delete_it.channel_id)
    else:
        messages.success(request, "You must be logged in to delete the record")
        return redirect('addresses')


@login_required(login_url='login_page')
def charts(request):
    context = {}
    return render(request, 'charts.html', context)


@login_required(login_url='login_page')
def pre_add_alarm(request):
    devices = Device.objects.all()
    return render(request, 'pre_add_alarm.html', {'records':devices})

@login_required(login_url='login_page')
def add_alarm(request, pk):
    device = Device.objects.get(pk=pk)
    
    if request.method == 'POST':
        form = AddAlarmForm(device_pk=pk, data=request.POST)
        if form.is_valid():
            alarm = form.save(commit=False)   
            alarm.channel = device
            alarm.save()
            messages.success(request, "Alarm Added")
            return redirect('alarms')
        else:
            print(form.errors)
    else:
        form = AddAlarmForm(device_pk=pk)
    
    # print(device.device_name)
    return render(request, 'add_alarm.html', {'form': form, "device":device})

    # return render(request, 'alarms.html', {})

@login_required(login_url='login_page')
def alarms(request):
    is_admin = request.user.groups.filter(name='Admin').exists()
    Alarms_record = Alarm.objects.all()
    triggered_alarms = AlarmTrigger.objects.all()
    
    context = {
        'alarms':Alarms_record,
        "is_admin":is_admin,
        "triggered_alarms":triggered_alarms
    }
    return render(request, 'alarms.html', context)

@login_required(login_url='login_page')
def update_alarm(request, pk):

    alarm_record = Alarm.objects.get(id=pk)
    device = Device.objects.get(id =alarm_record.channel_id)

    form = AddAlarmForm(device_pk=alarm_record.channel_id, data=request.POST or None, instance=alarm_record)

    form.fields["alarm_description"].initial = alarm_record.alarm_description
    form.fields["alarm_min"].initial = alarm_record.alarm_min
    form.fields["alarm_max"].initial = alarm_record.alarm_max
    form.fields["alarm_emails"].initial = alarm_record.alarm_emails
    form.fields["alarm_measure"].initial = alarm_record.alarm_measure
    if request.method == 'POST':
        if form.is_valid():
            alarm = form.save(commit=False)   
            alarm.channel = device
            form.save()
            return redirect('alarms')
    else:
        return render(request, 'update_alarm.html', {'alarm_record':alarm_record, 'form':form})

@login_required(login_url='login_page')
def delete_alarm(request, pk):
    if request.user.is_authenticated:
        delete_it = Alarm.objects.get(id = pk)
        delete_it.delete()
        return redirect('alarms')
    else:
        messages.success(request, "You must be logged in to delete the record")
        return redirect('alarms')

@login_required(login_url='login_page')
def reset_alarm(request, pk):
    if request.user.is_authenticated:
        Alarm.objects.filter(id = pk).update(alarm_trigger = 'No', alarm_triggered_at="")
        AlarmTrigger.objects.filter(trigger_alarm_id = pk).delete()
        messages.success(request, "Alarm Reseted")
        return redirect('alarms')

    else:
        messages.success(request, "You must be logged in to reset the Alarm")
        return redirect('alarms')
        
@login_required(login_url='login_page')
def reports(request):
    is_admin = request.user.groups.filter(name='Admin').exists()
    form = ReportDateForm(request.GET or None)

    reports_record = Report.objects.all()
    for reports_record_updated in reports_record:
        report_device = eval(reports_record_updated.report_device)
        report_measure = eval(reports_record_updated.report_measure)
        reports_record_updated.devices_measures_list = list(zip_longest(report_device, report_measure, fillvalue=""))
        reports_record_updated.report_device_length = len(eval(reports_record_updated.report_device))
        reports_record_updated.report_measure_length = len(eval(reports_record_updated.report_measure))
        reports_record_updated.report_type = reports_record_updated.report_date_type.replace("_"," ")


    return render(request, 'reports.html', {'reports':reports_record, "is_admin":is_admin, "form":form})


@login_required(login_url='login_page')
def add_report(request):
    form = AddReportForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                print("Valid_Report")
                form.save()

                messages.success(request, "Report Added")
                return redirect('reports')
            else:
                print("Unvalid_Report")
                print(form.errors)
        return render(request, 'add_report.html', {'form':form})
    else:
        messages.success(request, "Failed to add alarm")
        return redirect('reports')

@login_required(login_url='login_page')
def update_report(request, pk):
    report_record = Report.objects.get(id=pk)
    form = AddReportForm(request.POST or None, instance=report_record)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('reports')
    return render(request, 'update_report.html', {'form': form})

@login_required(login_url='login_page')
def delete_report(request, pk):
    if request.user.is_authenticated:
        delete_it = Report.objects.get(id=pk)
        delete_it.delete()
        return redirect('reports')
    else:
        messages.success(request, "You must be logged in to delete the record")
        return redirect('reports')
    
def trigger_email_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    send_email_report.delay(report.id)  # Trigger the task asynchronously
    messages.success(request, "Report is sent to email")
    return redirect("reports")


def trigger_download_report(request, report_id):
    report = Report.objects.get(id=report_id)
    
    form = ReportDateForm(request.GET or None)
    
    if form.is_valid():
        report_date_from = form.cleaned_data.get('report_date_from')
        report_date_to = form.cleaned_data.get('report_date_to')
        report_date_type = form.cleaned_data.get('report_date_type')
    else:
        print(form.errors)

    temp_data = []
    All_data = {}
    measurements = []

    report_devices = eval(report.report_device)
    report_measures = eval(report.report_measure)

    for string in report_measures:
        for value in report_devices:
            if value in string:
                try:
                    IDs = Device.objects.get(device_name=value)
                except:
                    pass
                parts = string.split(value, 1)
                if len(parts) == 2:
                    part1 = parts[0].strip(", :;")
                    part2 = value
                    measurements.append([part1, part2, IDs])

    if report_date_type == "Last_Record":
        data_list = []
        for item in measurements:
            register_values = Register.objects.filter(name=item[0], channel=item[2]).last()
            try:
                modbus_data = ModbusData.objects.filter(device_id=register_values.channel_id, register_id=register_values.id).last()
                local_timestamp = timezone.localtime(modbus_data.timestamp, timezone.get_current_timezone())  
                output = [local_timestamp.strftime("%Y %b %d %I:%M %p"), item[1], item[0], f"{modbus_data.value} ({register_values.parameter_name})"]
                data_list.append(output)
            except:
                pass
        final_df = pd.DataFrame(data_list, columns=['Timestamp', 'Device', "Measure", 'Value'])
    else:
        for item in measurements:
            try:
                register_values = Register.objects.filter(name=item[0], channel=item[2]).first()
                try:
                    All_data[register_values.polling_interval].append([register_values.name, item[2]])
                except KeyError:
                    All_data[register_values.polling_interval] = [[register_values.name, item[2]]]
            except:
                pass

        df_list = []
        for polling_interval, devices in All_data.items():
            timestamp_data = {}
            for j, device in enumerate(devices): 
                register_values = Register.objects.filter(name=device[0], channel=device[1]).first()
                modbus_data = ModbusData.objects.filter(device=device[1],
                                                        register_id=register_values.id,
                                                        timestamp__range=(report_date_from, report_date_to)
                                                        ).select_related('register').order_by('id')
                
                for counter, data in enumerate(modbus_data):
                    local_timestamp = timezone.localtime(data.timestamp, timezone.get_current_timezone())  
                    if counter not in timestamp_data:
                        timestamp_data[counter] = {
                            "":"",
                            "Time": local_timestamp.strftime("%Y %b %d %I:%M %p"),
                            "Polling Interval": data.register.polling_interval,
                        }
                    timestamp_data[counter][f"{device[1]} {device[0]}"] = f"{data.value} ({data.register.parameter_name})"

            df = pd.DataFrame.from_dict(timestamp_data, orient='index')
            df_list.append(df)
            
        final_df = pd.concat(df_list, axis=1)
        
        # Calculating averages and medians
        device_columns = [col for col in final_df.columns if any(dev.device_name in col for dev in Device.objects.all())]
        avg_median_data = {'Devices': [], 'Avg': [], 'Median': [], 'Max':[],'Min':[],'space':[]}

        for col in device_columns:
            print("This is Col ",col)
            device_values = final_df[col].str.extract(r'(\d+\.?\d*)').dropna().astype(float)[0]
            avg_median_data['Devices'].append(col)
            avg_median_data['Avg'].append(device_values.mean())
            avg_median_data['Median'].append(device_values.median())
            avg_median_data['Max'].append(device_values.max())
            avg_median_data['Min'].append(device_values.min())
            avg_median_data['space'].append(None)

        avg_median_df = pd.DataFrame(avg_median_data)

        avg_median_df.columns = avg_median_df.columns.astype(str)
        final_df.columns = final_df.columns.astype(str)
        desired_columns = ['Devices', 'Avg', 'Median', 'Max', 'Min','']
        desired_columns.extend(final_df.columns)

        # Combining the dataframes
        final_df = pd.concat([avg_median_df, final_df], axis=1, ignore_index=True)
        final_df.columns = desired_columns
        
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(final_df)
  
    csv_data = final_df.to_csv(index=False)
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{report_id}.csv"'

    return response



@login_required(login_url='login_page')
def user_page(request):
    if request.method == 'POST' and request.user.groups.filter(name='Admin').exists():
        master_email = request.POST.get("master_email", "")
        
        if master_email:  # Check if master_email is not empty
            master_email_entry, created = MasterEmail.objects.get_or_create(id=1)
            master_email_entry.email = str.lower(master_email)
            master_email_entry.save()

        return redirect('user_page')
    
    is_admin = request.user.groups.filter(name='Admin').exists()
    email = MasterEmail.objects.first()

    context = {
        "is_admin":is_admin,
        "email":email
    }
    return render(request, 'user_page.html', context)

@login_required(login_url='login_page')
def historical_data_logs(request):
    tables = []
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'modbusdata_%';")
        # tables = [row[0] for row in cursor.fetchall()]
        for row in cursor.fetchall():
            table_heads = {'table_head': row[0], 'table_name': row[0].replace("modbusdata_", "").replace("_", "/")}
            tables.append(table_heads)

        # print(tables)
    
    context = {
        'tables': tables,
    }
    return render(request, 'historical_data_logs.html', context)

@login_required(login_url='login_page')
def historical_data(request, table_name):
    device_ids = []
    device_names = []

    with connection.cursor() as cursor:
        # Query to select all data from the specified historical table
        query = f"SELECT DISTINCT device_id, device_name FROM {table_name} ORDER BY device_name"
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        query = f"SELECT DISTINCT device_id, device_name FROM {table_name} ORDER BY device_name"


        for device in data:
            device_ids.append(device['device_id'])
            device_names.append(device['device_name'])

        # print(device_ids)
        # print(device_names)
        # print(data)
    table_name_view = table_name.replace("modbusdata_", "").replace("_", "/")
    

    # print(table_name_view)
    
    context = {
        'data': data,
        'table_name': table_name,
        'table_name_view':table_name_view,
        'device_ids':device_ids,
        'device_names':device_names,
    }
    return render(request, 'historical_data.html', context)


@login_required(login_url='login_page')
def dashboard(request):
    form = AddReportForm(request.POST or None)
    measurements = []  # List to hold the data for the template

    if request.user.is_authenticated:
        if request.method == 'POST':
            report_device = request.POST.getlist('report_device')
            report_measure = request.POST.getlist('report_measure')

            print(f"Report Device: {report_device}")
            print(f"Report Measure: {report_measure}")

            for string in report_measure:
                for value in report_device:
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
                                        register_id=register_values.id
                                    ).first()
                                    
                                    last_modbus_data = ModbusData.objects.filter(
                                        device_id=register_values.channel_id, 
                                        register_id=register_values.id
                                    ).last()
                                    
                                    first_value = first_modbus_data.value if first_modbus_data else "N/A"
                                    last_value = last_modbus_data.value if last_modbus_data else "N/A"

                                    # first_local_timestamp = timezone.localtime(first_modbus_data.timestamp, timezone.get_current_timezone())  
                                    # last_local_timestamp = timezone.localtime(last_modbus_data.timestamp, timezone.get_current_timezone())  

                                    measurements.append({
                                        'device': part2,
                                        'measure': part1,
                                        'first_value': first_value + register_values.parameter_name,
                                        'last_value': last_value + register_values.parameter_name,
                                        # 'first_time': first_local_timestamp.strftime("%Y %b %d %I:%M %p"),
                                        # 'last_time': last_local_timestamp.strftime("%Y %b %d %I:%M %p")
                                    })

                                except Exception as e:
                                    print(f"Error fetching Modbus data: {e}")
                                    continue

    context = {'form': form, 'measurements': measurements}
    return render(request, 'dashboard.html', context)

def build_tree(devices):
    # Create a dictionary to store the grouped devices
    group_dict = {}
    for device in devices:
        group = device.group
        if group not in group_dict:
            group_dict[group] = []
        group_dict[group].append({
            "value": device.device_name,
            "hidden": device.ip_address,
            "name": device.id,
            "children": []
        })

    # Create the final list of tree structures
    tree_data = []
    for group, devices in group_dict.items():
        tree_data.append({
            "value": group,
            "name": group,
            "children": devices
        })

    return tree_data

def device_tree_view(request):
    devices = Device.objects.all()
    tree_data = build_tree(devices)
    return JsonResponse(tree_data, safe=False)

def device_tree_view_element(request, pk):
    dict = {}
    dict["chart"] = []
    dict["chart_measure"] = []
    device = Device.objects.get(id = pk)

    dict["device_status"] = device.device_status
    dict["total_registers"] = Register.objects.filter(channel_id = device.id).count()
    dict["triggered_alarms"] = Alarm.objects.filter(channel_id = device.id, alarm_trigger = "Yes").count()
    dict["total_alarms"] = Alarm.objects.filter(channel_id = device.id).count()

    try:
        measures = Diagram_Charts.objects.get(device_id = pk)
        dict["chart"].append(measures.chart_1_1)
        dict["chart"].append(measures.chart_2_1)
        dict["chart"].append(measures.chart_3_1)
        dict["chart"].append(measures.chart_4_1)
        dict["chart"].append(measures.chart_5_1)
        dict["chart"].append(measures.chart_6_1)

        registers_list = [measures.chart_1_1, measures.chart_2_1, measures.chart_3_1, measures.chart_4_1,measures.chart_5_1, measures.chart_6_1]

        if device.connection_type == 'TCP':
            ip_address = device.ip_address
            port_conf = device.port_conf
            c = ModbusClient(host=ip_address, port=int(port_conf), timeout=0.1)
            c.open()
            try:
                for register_name in registers_list:
                    register = Register.objects.filter(channel_id = pk, name = register_name).first()

                    register_address = register.register_address
                    num_of_registers = register.num_of_registers
                    value = c.read_holding_registers(int(register_address), int(num_of_registers))
                    if value:
                        if len(value) == 4:
                            combined_value = (value[0] << 48) | (value[1] << 32) | (value[2] << 16) | value[3]     
                            last_value = struct.unpack('d', struct.pack('Q', combined_value))[0]
                            last_value = (last_value/register.dividing_parameter)

                        elif value[0] != 0:
                            combined_value = (value[0] << 16) | value[1]
                            last_value = struct.unpack('f', struct.pack('I', combined_value))[0]
                            last_value = (last_value/register.dividing_parameter)
                        # print(f"this is my new value {value_}")
                        else:
                            last_value = value[1]
                            last_value = (last_value/register.dividing_parameter)
                            
                        dict["chart_measure"].append(last_value)
                        
                    else:
                        # print("Failed to read from register")
                        last_value = random.randint(100, 300)
                        dict["chart_measure"].append(last_value)

            except Exception as e:
                print(e)

    except:
        pass



    return JsonResponse(dict, safe=False)

# @login_required(login_url='login_page')
def diagrams(request):
    context = {}
    return render(request, 'diagrams.html', context)
        
def diagrams_device(request, pk):
    is_admin = request.user.groups.filter(name='Admin').exists()

    device = Device.objects.get(id=pk)
    existing_device_form = Diagram_Charts.objects.filter(device=device).first()
    
    if existing_device_form:
        # Create the form with initial data from the existing object
        form = Diagram_Charts_Form(device_pk=pk, data=request.POST or None, instance=existing_device_form)
    else:
        # Create a new form without initial data
        form = Diagram_Charts_Form(device_pk=pk, data=request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        print(f"Form is Valid {device}")
        device_form = form.save(commit=False)
        device_form.device = device

        if existing_device_form:
            for field in form.cleaned_data:
                setattr(existing_device_form, field, form.cleaned_data[field])
            existing_device_form.save()
            # print("Existing device form updated.")
        else:
            # Create a new object
            device_form.save()
            # print("New device form created.")
    else:
        # Print form errors if needed
        print(form.errors)

    context = {
        "device": device,
        "form": form,
        "is_admin":is_admin
    }
    return render(request, "diagrams_device.html", context)


def diagrams_chart_data(request, name):
    values_list = []
    chart_counter = 0

    device = Device.objects.get(id = name)
    measure = Diagram_Charts.objects.filter(device_id=name).values()
    measures_list = [measure[0]["chart_1_1"], measure[0]["chart_1_2"], measure[0]["chart_1_3"], measure[0]["chart_1_4"], measure[0]["chart_1_5"], measure[0]["chart_2_1"], measure[0]["chart_2_2"], measure[0]["chart_2_3"], measure[0]["chart_2_4"], measure[0]["chart_2_5"], measure[0]["chart_3_1"], measure[0]["chart_3_2"], measure[0]["chart_3_3"], measure[0]["chart_3_4"], measure[0]["chart_3_5"], measure[0]["chart_4_1"], measure[0]["chart_4_2"], measure[0]["chart_4_3"], measure[0]["chart_4_4"], measure[0]["chart_4_5"], measure[0]["chart_5_1"], measure[0]["chart_5_2"], measure[0]["chart_5_3"], measure[0]["chart_5_4"], measure[0]["chart_5_5"], measure[0]["chart_6_1"], measure[0]["chart_6_2"], measure[0]["chart_6_3"], measure[0]["chart_6_4"], measure[0]["chart_6_5"]]

    data = list(measure)

    for item in data:
        for key, value in item.items():
            if value is None or value == 'None':
                item[key] = 'None'  # Replace with your desired default value

        if device.connection_type == 'TCP':
            ip_address = device.ip_address
            port_conf = device.port_conf
            c = ModbusClient(host=ip_address, port=int(port_conf), timeout=0.1)
            c.open()

            try:
                for measure_data in measures_list:

                    register = Register.objects.filter(channel_id = name, name = measure_data).first()
                    if(register):
                        register_address = register.register_address
                        num_of_registers = register.num_of_registers
                        value = c.read_holding_registers(int(register_address), int(num_of_registers))
                        if value:
                            if len(value) == 4:
                                combined_value = (value[0] << 48) | (value[1] << 32) | (value[2] << 16) | value[3]     
                                last_value = struct.unpack('d', struct.pack('Q', combined_value))[0]
                                last_value = (last_value/register.dividing_parameter)

                            elif value[0] != 0:
                                combined_value = (value[0] << 16) | value[1]
                                last_value = struct.unpack('f', struct.pack('I', combined_value))[0]
                                last_value = (last_value/register.dividing_parameter)
                            # print(f"this is my new value {value_}")
                            else:
                                last_value = value[1]
                                last_value = (last_value/register.dividing_parameter)
                                
                            values_list.append([last_value, register.parameter_name])
                            
                        else:
                            # print("Failed to read from register")
                            last_value = random.randint(100, 300)
                            values_list.append([last_value, register.parameter_name])
                    else:
                        values_list.append("0")

            except Exception as e:
                print(e)

        try:
            for chart_num in range(1, 7):  
                for measure_num in range(1, 6):  
                    # print(values_list[chart_counter])
                    field_name = f'chart_{chart_num}_{measure_num}_measure'
                    item[field_name] = values_list[chart_counter]
                    chart_counter = chart_counter + 1

        except Exception as e:
            print(e)



    c.close()


    return JsonResponse(data, safe=False)

def diagrams_chart_graph(request, name):
    registers = []
    dict = {}

    measure = Diagram_Charts.objects.get(device_id=name)
    graph = eval(measure.graph_1)

    for item in graph:
        register = Register.objects.filter(channel_id = name, name = item).first()
        registers.append(register.id)

    # print(registers)
    modbus_data = ModbusData.objects.filter(device=name, register_id__in = registers).select_related('register').order_by('-id')

    grouped_data = {}
    unique_times = []
    parameter_name = []

    for item in modbus_data:
        local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
        time = local_timestamp.strftime("%Y %b %d %I:%M %p")

        if time not in unique_times:
            # Add the timestamp to the set
            unique_times.append(time)

    for item in modbus_data:
        register_name = item.register.name
        if register_name not in grouped_data:
            # Initialize the entry with the required structure
            grouped_data[register_name] = {
                'name': f"{register_name} ({item.register.parameter_name})",
                # 'id': item.id,
                # 'device_id': item.device_id,
                # 'register_id': item.register_id,
                # 'timestamp': item.timestamp.isoformat(),
                # 'register_address': item.register_address,
                'value': [],  # Initialize an empty list for values
                'polling_interval': item.polling_interval
            }

            parameter_name.append(item.register.parameter_name)
        # Append the value to the list
        grouped_data[register_name]['value'].append(f"{item.value}")

    # Convert the grouped_data dictionary to a list of dictionaries
    result = list(grouped_data.values())


    graph = [f"{l} ({p})" for l, p in zip(graph, parameter_name)]
    print(graph)
    # for item in result:
    #     print(item)

    unique_times = sorted(unique_times)
    legends = graph
    response_data = {
        'result': result,
        'legends': legends,
        'time':unique_times
    }

    return JsonResponse(response_data, safe=False)

























@login_required(login_url='login_page')
def historical_data_by_device_id(request, table_name, device_id):
    with connection.cursor() as cursor:
        query = f"SELECT device_name FROM {table_name} WHERE id = %s LIMIT 1"
        cursor.execute(query, [device_id])
        row = cursor.fetchone()
        device_name = row[0] if row else None

    with connection.cursor() as cursor:
        query = f"SELECT * FROM {table_name} WHERE device_id = %s ORDER BY -id LIMIT 10000"
        cursor.execute(query, [device_id])
        columns = [col[0] for col in cursor.description]
        modbus_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

    five_secounds = []
    fifteen_secounds = []
    thirty_secounds = []
    sixty_secounds = []
    five_minutes = []
    fifteen_minutes = []
    thirty_minutes = []
    sixty_minutes = []
    six_hours = []
    twealv_hours = []
    twinty_four_hours = []

    unique_registers_5 = OrderedDict()
    unique_registers_15 = OrderedDict()
    unique_registers_30 = OrderedDict()
    unique_registers_60 = OrderedDict()
    unique_registers_5_min = OrderedDict()
    unique_registers_15_min = OrderedDict()
    unique_registers_30_min = OrderedDict()
    unique_registers_60_min = OrderedDict()
    unique_registers_6_hours = OrderedDict()
    unique_registers_12_hours = OrderedDict()
    unique_registers_24_hours = OrderedDict()

    unique_registers_5["Time Stamp"] = None
    unique_registers_15["Time Stamp"] = None
    unique_registers_30["Time Stamp"] = None
    unique_registers_60["Time Stamp"] = None
    unique_registers_5_min["Time Stamp"] = None
    unique_registers_15_min["Time Stamp"] = None
    unique_registers_30_min["Time Stamp"] = None
    unique_registers_60_min["Time Stamp"] = None
    unique_registers_6_hours["Time Stamp"] = None
    unique_registers_12_hours["Time Stamp"] = None
    unique_registers_24_hours["Time Stamp"] = None

    for counter, data in enumerate(modbus_data):
        if data['polling_interval'] == "5 Seconds":
            five_secounds.append(data)
        elif data['polling_interval'] == "15 Seconds":
            fifteen_secounds.append(data)
        elif data['polling_interval'] == "30 Seconds":
            thirty_secounds.append(data)
        elif data['polling_interval'] == "60 Seconds":
            sixty_secounds.append(data)
        elif data['polling_interval'] == "5 Minutes":
            five_minutes.append(data)
        elif data['polling_interval'] == "15 Minutes":
            fifteen_minutes.append(data)
        elif data['polling_interval'] == "30 Minutes":
            thirty_minutes.append(data)
        elif data['polling_interval'] == "60 Minutes":
            sixty_minutes.append(data)
        elif data['polling_interval'] == "6 Houres":
            six_hours.append(data)  
        elif data['polling_interval'] == "12 Houres":
            twealv_hours.append(data)  
        elif data['polling_interval'] == "24 Houres":
            twinty_four_hours.append(data)

    for data in five_secounds:
        unique_registers_5[data['register_name']] = None
    for data in fifteen_secounds:
        unique_registers_15[data['register_name']] = None
    for data in thirty_secounds:
        unique_registers_30[data['register_name']] = None
    for data in sixty_secounds:
        unique_registers_60[data['register_name']] = None
    for data in five_minutes:
        unique_registers_5_min[data['register_name']] = None
    for data in fifteen_minutes:
        unique_registers_15_min[data['register_name']] = None
    for data in thirty_minutes:
        unique_registers_30_min[data['register_name']] = None
    for data in sixty_minutes:
        unique_registers_60_min[data['register_name']] = None
    for data in six_hours:
        unique_registers_6_hours[data['register_name']] = None
    for data in twealv_hours:
        unique_registers_12_hours[data['register_name']] = None
    for data in twinty_four_hours:
        unique_registers_24_hours[data['register_name']] = None

    # five_secounds.reverse()
    # fifteen_secounds.reverse()
    # thirty_secounds.reverse()
    # sixty_secounds.reverse()
    # five_minutes.reverse()
    # fifteen_minutes.reverse()
    # thirty_minutes.reverse()
    # sixty_minutes.reverse()
    # six_hours.reverse()
    # twealv_hours.reverse()
    # twinty_four_hours.reverse()

    # unique_registers_15.__reversed__()

    # print(unique_registers_15)
    # print(fifteen_secounds)

    context = {
        'five_secounds': five_secounds,
        'fifteen_secounds': fifteen_secounds,
        'thirty_secounds': thirty_secounds,
        'sixty_secounds': sixty_secounds,
        'five_minutes': five_minutes,
        'fifteen_minutes': fifteen_minutes,
        'thirty_minutes': thirty_minutes,
        'sixty_minutes': sixty_minutes,
        'six_hours': six_hours,
        'twealv_hours': twealv_hours,
        'twinty_four_hours': twinty_four_hours,

        "unique_registers_5": list(unique_registers_5.keys()),
        "unique_registers_15": list(unique_registers_15.keys()),
        "unique_registers_30": list(unique_registers_30.keys()),
        "unique_registers_60": list(unique_registers_60.keys()),
        "unique_registers_5_min": list(unique_registers_5_min.keys()),
        "unique_registers_15_min": list(unique_registers_15_min.keys()),
        "unique_registers_30_min": list(unique_registers_30_min.keys()),
        "unique_registers_60_min": list(unique_registers_60_min.keys()),
        "unique_registers_6_hours": list(unique_registers_6_hours.keys()),
        "unique_registers_12_hours": list(unique_registers_12_hours.keys()),
        "unique_registers_24_hours": list(unique_registers_24_hours.keys()),

        'length_5': len(unique_registers_5) - 1,
        'length_15': len(unique_registers_15) - 1,
        'length_30': len(unique_registers_30) - 1,
        'length_60': len(unique_registers_60) - 1,
        'length_5_min': len(unique_registers_5_min) - 1,
        'length_15_min': len(unique_registers_15_min) - 1,
        'length_30_min': len(unique_registers_30_min) - 1,
        'length_60_min': len(unique_registers_60_min) - 1,
        'length_6_hours': len(unique_registers_6_hours) - 1,
        'length_12_hours': len(unique_registers_12_hours) - 1,
        'length_24_hours': len(unique_registers_24_hours) - 1,

        "device_name":device_name
    }
    

    if request.GET.get('format') == 'csv':
        table_id = request.GET.get('table_id')
        if table_id == 'CSV_Export_5_sec':
            polling_interval = '5 Seconds'
        elif table_id == 'CSV_Export_15_sec':
            polling_interval = '15 Seconds'
        elif table_id == 'CSV_Export_30_sec':
            polling_interval = '30 Seconds'
        elif table_id == 'CSV_Export_60_sec':
            polling_interval = '60 Seconds'
        elif table_id == 'CSV_Export_5_min':
            polling_interval = '5 Minutes'
        elif table_id == 'CSV_Export_15_min':
            polling_interval = '15 Minutes'
        elif table_id == 'CSV_Export_30_min':
            polling_interval = '30 Minutes'
        elif table_id == 'CSV_Export_60_min':
            polling_interval = '60 Minutes'
        elif table_id == 'CSV_Export_6_hours':
            polling_interval = '6 Houres'
        elif table_id == 'CSV_Export_12_hours':
            polling_interval = '12 Houres'
        elif table_id == 'CSV_Export_24_hours':
            polling_interval = '24 Houres'

        with connection.cursor() as cursor:
            query = f"""
                    SELECT * FROM {table_name} 
                    WHERE device_id = %s AND polling_interval = %s 
                    ORDER BY id 
                """
            cursor.execute(query, [device_id, polling_interval])
            columns = [col[0] for col in cursor.description]
            modbus_data_download = [dict(zip(columns, row)) for row in cursor.fetchall()]

        if table_id:
            # Prepare CSV data for the specified table
            if table_id == 'CSV_Export_5_sec':
                csv_data = ' , '.join(unique_registers_5) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_5) - 1) == 0:
                        if counter == 0:
                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:
                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_15_sec':
                csv_data = ' , '.join(unique_registers_15) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_15) - 1) == 0:
                        if counter == 0:
                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:
                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "
                    
            elif table_id == 'CSV_Export_30_sec':
                csv_data = ' , '.join(unique_registers_30) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_30) - 1) == 0:
                        if counter == 0:
                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:
                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_60_sec':
                csv_data = ' , '.join(unique_registers_60) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_60) - 1) == 0:
                        if counter == 0:

                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:

                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_5_min':
                csv_data = ' , '.join(unique_registers_5_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_5_min) - 1) == 0:
                        if counter == 0:

                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:

                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_15_min':
                csv_data = ' , '.join(unique_registers_15_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_15_min) - 1) == 0:
                        if counter == 0:

                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:

                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_30_min':
                csv_data = ' , '.join(unique_registers_30_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_30_min) - 1) == 0:
                        if counter == 0:

                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:

                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_60_min':
                csv_data = ' , '.join(unique_registers_60_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_60_min) - 1) == 0:
                        if counter == 0:

                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:

                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_6_hours':
                csv_data = ' , '.join(unique_registers_6_hours) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_6_hours) - 1) == 0:
                        if counter == 0:

                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:

                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_12_hours':
                csv_data = ' , '.join(unique_registers_12_hours) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_12_hours) - 1) == 0:
                        if counter == 0:

                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:

                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            elif table_id == 'CSV_Export_24_hours':
                csv_data = ' , '.join(unique_registers_24_hours) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    value = item["value"]
                    time = item["timestamp"].strftime("%Y %b %d %I:%M %p")
                    parameter_name = item["parameter_name"]
                    if counter % (len(unique_registers_24_hours) - 1) == 0:
                        if counter == 0:
                            csv_data += f"{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                        else:
                            csv_data += f"\n{time} ,"
                            csv_data += f"{value} ({parameter_name}), "
                    else:
                        csv_data += f"{value} ({parameter_name}), "

            # Return the CSV data for the specified table as an attachment
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{device_name}_{table_id}.csv"'
            return response
        else:
            return HttpResponse("Table ID parameter is missing", status=400)

    return render(request, "historical_data_by_device_id.html", context)









@login_required(login_url='login_page')
def data_logs(request, pk):
    form = ReportDateForm(request.GET or None)
    temp_data = []
    All_data = []

    five_secounds = []
    fifteen_secounds = []
    thirty_secounds = []
    sixty_secounds = []
    five_minutes = []
    fifteen_minutes = []
    thirty_minutes = []
    sixty_minutes = []
    six_hours = []
    twealv_hours = []
    twinty_four_hours = []

    unique_registers_5 = OrderedSet()
    unique_registers_15 = OrderedSet()
    unique_registers_30 = OrderedSet()
    unique_registers_60 = OrderedSet()
    unique_registers_5_min = OrderedSet()
    unique_registers_15_min = OrderedSet()
    unique_registers_30_min = OrderedSet()
    unique_registers_60_min = OrderedSet()
    unique_registers_6_hours = OrderedSet()
    unique_registers_12_hours = OrderedSet()
    unique_registers_24_hours = OrderedSet()

    unique_registers_5.add("Time Stamp")
    unique_registers_15.add("Time Stamp")
    unique_registers_30.add("Time Stamp")
    unique_registers_60.add("Time Stamp")
    unique_registers_5_min.add("Time Stamp")
    unique_registers_15_min.add("Time Stamp")
    unique_registers_30_min.add("Time Stamp")
    unique_registers_60_min.add("Time Stamp")
    unique_registers_6_hours.add("Time Stamp")
    unique_registers_12_hours.add("Time Stamp")
    unique_registers_24_hours.add("Time Stamp")
                
    records = Device.objects.get(id = pk)

    modbus_data = ModbusData.objects.filter(device=records).select_related('register').order_by('-id')[:10000]

    for counter, data in enumerate(modbus_data):
        if data.register.polling_interval == "5 Seconds":
            five_secounds.append(data)

        elif data.register.polling_interval == "15 Seconds":
            fifteen_secounds.append(data)

        elif data.register.polling_interval == "30 Seconds":
            thirty_secounds.append(data)

        elif data.register.polling_interval == "60 Seconds":
            sixty_secounds.append(data)

        elif data.register.polling_interval == "5 Minutes":
            five_minutes.append(data)

        elif data.register.polling_interval == "15 Minutes":
            fifteen_minutes.append(data)

        elif data.register.polling_interval == "30 Minutes":
            thirty_minutes.append(data)

        elif data.register.polling_interval == "60 Minutes":
            sixty_minutes.append(data)

        elif data.register.polling_interval == "6 Houres":
            six_hours.append(data)  

        elif data.register.polling_interval == "12 Houres":
            twealv_hours.append(data)  

        elif data.register.polling_interval == "24 Houres":
            twinty_four_hours.append(data)           

    
    for data in five_secounds:
        unique_registers_5.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in fifteen_secounds:
        unique_registers_15.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in thirty_secounds:
        unique_registers_30.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in sixty_secounds:
        unique_registers_60.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in five_minutes:
        unique_registers_5_min.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in fifteen_minutes:
        unique_registers_15_min.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in thirty_minutes:
        unique_registers_30_min.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in sixty_minutes:
        unique_registers_60_min.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in six_hours:
        unique_registers_6_hours.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in twealv_hours:
        unique_registers_12_hours.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])

    for data in twinty_four_hours:
        unique_registers_24_hours.add(data.register.name)
        # print([data.timestamp, data.register.name,data.value, data.register.polling_interval])
    
    # five_secounds.reverse()
    # fifteen_secounds.reverse()
    # thirty_secounds.reverse()
    # sixty_secounds.reverse()
    # five_minutes.reverse()
    # fifteen_minutes.reverse()
    # thirty_minutes.reverse()
    # sixty_minutes.reverse()
    # six_hours.reverse()
    # twealv_hours.reverse()
    # twinty_four_hours.reverse()

    context = {
        'five_secounds': five_secounds,
        'fifteen_secounds': fifteen_secounds,
        'thirty_secounds': thirty_secounds,
        'sixty_secounds': sixty_secounds,
        'five_minutes': five_minutes,
        'fifteen_minutes': fifteen_minutes,
        'thirty_minutes': thirty_minutes,
        'sixty_minutes': sixty_minutes,
        'six_hours': six_hours,
        'twealv_hours': twealv_hours,
        'twinty_four_hours': twinty_four_hours,

        "unique_registers_5":unique_registers_5,
        "unique_registers_15":unique_registers_15,
        "unique_registers_30":unique_registers_30,
        "unique_registers_60":unique_registers_60,
        "unique_registers_5_min":unique_registers_5_min,
        "unique_registers_15_min":unique_registers_15_min,
        "unique_registers_30_min":unique_registers_30_min,
        "unique_registers_60_min":unique_registers_60_min,
        "unique_registers_6_hours":unique_registers_6_hours,
        "unique_registers_12_hours":unique_registers_12_hours,
        "unique_registers_24_hours":unique_registers_24_hours,
        
        'length_5':len(unique_registers_5) - 1,
        'length_15':len(unique_registers_15) - 1,
        'length_30':len(unique_registers_30) - 1,
        'length_60':len(unique_registers_60) - 1,
        'length_5_min':len(unique_registers_5_min) - 1,
        'length_15_min':len(unique_registers_15_min) - 1,
        'length_30_min':len(unique_registers_30_min) - 1,
        'length_60_min':len(unique_registers_60_min) - 1,
        'length_6_hours':len(unique_registers_6_hours) - 1,
        'length_12_hours':len(unique_registers_12_hours) - 1,
        'length_24_hours':len(unique_registers_24_hours) - 1,


        'modbus_data':modbus_data,
        'records':records,
        'form':form
    }

    if request.GET.get('format') == 'csv':
        table_id = request.GET.get('table_id')
        date_type = request.GET.get('date_type')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        print(table_id)
        print(date_type)
        print(date_to)
        print(date_from)

        if table_id == 'CSV_Export_5_sec':
            polling_interval = '5 Seconds'
        elif table_id == 'CSV_Export_15_sec':
            polling_interval = '15 Seconds'
        elif table_id == 'CSV_Export_30_sec':
            polling_interval = '30 Seconds'
        elif table_id == 'CSV_Export_60_sec':
            polling_interval = '60 Seconds'
        elif table_id == 'CSV_Export_5_min':
            polling_interval = '5 Minutes'
        elif table_id == 'CSV_Export_15_min':
            polling_interval = '15 Minutes'
        elif table_id == 'CSV_Export_30_min':
            polling_interval = '30 Minutes'
        elif table_id == 'CSV_Export_60_min':
            polling_interval = '60 Minutes'
        elif table_id == 'CSV_Export_6_hours':
            polling_interval = '6 Houres'
        elif table_id == 'CSV_Export_12_hours':
            polling_interval = '12 Houres'
        elif table_id == 'CSV_Export_24_hours':
            polling_interval = '24 Houres'

        if date_type == "Last_Record":
            modbus_data_download = ModbusData.objects.filter(
                device=records, 
                register__polling_interval=polling_interval
            ).select_related('register').order_by('-id')

        else:
            modbus_data_download = ModbusData.objects.filter(
                device=records, 
                register__polling_interval=polling_interval,
                timestamp__range=(date_from, date_to)
            ).select_related('register').order_by('-id')

        if table_id:
            # Prepare CSV data for the specified table
            if table_id == 'CSV_Export_5_sec':
                csv_data = ' , '.join(unique_registers_5) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_5) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} ({item.register.parameter_name}), "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} ({item.register.parameter_name}), "
                    else:
                        csv_data += f"{item.value} ({item.register.parameter_name}), "

            elif table_id == 'CSV_Export_15_sec':
                csv_data = ' , '.join(unique_registers_15) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_15) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} ({item.register.parameter_name}), "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} ({item.register.parameter_name}), "
                    else:
                        csv_data += f"{item.value} ({item.register.parameter_name}), "
                    
            elif table_id == 'CSV_Export_30_sec':
                csv_data = ' , '.join(unique_registers_30) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_30) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} ({item.register.parameter_name}), "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} ({item.register.parameter_name}), "
                    else:
                        csv_data += f"{item.value} ({item.register.parameter_name}), "

            elif table_id == 'CSV_Export_60_sec':
                csv_data = ' , '.join(unique_registers_60) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_60) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "

            elif table_id == 'CSV_Export_5_min':
                csv_data = ' , '.join(unique_registers_5_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_5_min) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "

            elif table_id == 'CSV_Export_15_min':
                csv_data = ' , '.join(unique_registers_15_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_15_min) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "

            elif table_id == 'CSV_Export_30_min':
                csv_data = ' , '.join(unique_registers_30_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_30_min) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "

            elif table_id == 'CSV_Export_60_min':
                csv_data = ' , '.join(unique_registers_60_min) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_60_min) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "

            elif table_id == 'CSV_Export_6_hours':
                csv_data = ' , '.join(unique_registers_6_hours) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_6_hours) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "

            elif table_id == 'CSV_Export_12_hours':
                csv_data = ' , '.join(unique_registers_12_hours) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_12_hours) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "

            elif table_id == 'CSV_Export_24_hours':
                csv_data = ' , '.join(unique_registers_24_hours) + '\n'
                for counter, item in enumerate(modbus_data_download):
                    if counter % (len(unique_registers_24_hours) - 1) == 0:
                        if counter == 0:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                        else:
                            local_timestamp = timezone.localtime(item.timestamp, timezone.get_current_timezone())
                            time = local_timestamp.strftime("%Y %b %d %I:%M %p")
                            csv_data += f"\n{time} ,"
                            csv_data += f"{item.value} {item.register.parameter_name}, "
                    else:
                        csv_data += f"{item.value} {item.register.parameter_name}, "
                # csv_data = generate_csv_data_for_6_hours_table()

            # Return the CSV data for the specified table as an attachment
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{records.device_name}_{table_id}.csv"'
            return response
        else:
            return HttpResponse("Table ID parameter is missing", status=400)
        
    return render(request, 'data_logs.html', context)