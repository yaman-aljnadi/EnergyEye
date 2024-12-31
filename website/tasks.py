from celery import Celery
from celery import shared_task, current_app ,current_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from datetime import datetime, timedelta
from celery.schedules import crontab
from .models import *
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient
from ordered_set import OrderedSet
from celery.result import AsyncResult
import struct
import pandas as pd
from django.db import connection
from decouple import config
from django.core.management.base import BaseCommand
import time
import pytz
import random

from django.utils import timezone
from django.utils.timezone import make_aware


app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

import mysql.connector

mydb = mysql.connector.connect(
  host= config("DATABASE_HOST"),
  user="root",
  password=config("DATABASE_PASSWORD"),
  database=config("DATABASE_NAME")
)


        
 
@shared_task
def create_report_tasks(report_id):
    PeriodicTask.objects.update(last_run_at=None)

    report = Report.objects.get(id=report_id)
    hours = int(report.report_interval_hours)
    minutes = int(report.report_interval_minutes)
    days = report.report_activation

    if report.report_activation == "Monthly":
        days = "*"
        monthly = "1"
        print("This is monthly")

    else:
        days = report.report_activation
        monthly = "*"
        

    # print(f"Enabled Reports {report.report_device}")
    if not PeriodicTask.objects.filter(args=[report_id]).exists():
        print("Does not Exists")

        schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=minutes,
        hour=hours,
        day_of_week=days,
        day_of_month = monthly,
        month_of_year='*',
        timezone=report.report_timezone,
        )
        
        PeriodicTask.objects.get_or_create(
            crontab=schedule,              # we created this above.
            name=report.report_description + f' Report Id: {report_id}',          # simply describes this periodic task.
            task='website.tasks.send_email_report',  # name of task.
            description = report.report_description,
            args=[report.id]
        )

    else:
        print("Exists")
        try:

            schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minutes,
            hour=hours,
            day_of_week=days,
            day_of_month=monthly,
            month_of_year='*',
            timezone=report.report_timezone,
            )

            PeriodicTask.objects.filter(args=[report_id]).update(
             crontab=schedule,
             args=[report.id], 
             task='website.tasks.send_email_report',
             description = report.report_description, 
             name=report.report_description + f' Report Id: {report_id}')
        except Exception as e:
            # break
            print(e)

            
@shared_task
def delete_report_tasks(report_id):
    PeriodicTask.objects.filter(args=[report_id]).delete()
    print("Deleted")





@shared_task
def schedule_task(polling_interval_all, polling_interval):
    devices = Device.objects.all()

    print(polling_interval)
    
    for device in devices:
        if device.signals == 'Enabeld':
            if device.connection_type == 'TCP':
                # registers = Register.objects.filter(channel=device.id)
                ip_address = device.ip_address
                port_conf = device.port_conf

                c = ModbusClient(host=ip_address, port=int(port_conf), timeout=1)
                c.open()
                try:
                    for register in Register.objects.filter(channel=device.id):
                        
                        register_address = register.register_address
                        num_of_registers = register.num_of_registers
                        
                        # print([device.device_name ,ip_address, port_conf, register_address, num_of_registers])
                        # print(["here is polling interval", polling_interval_all, polling_interval, register.polling_interval])
                        if register.polling_interval == polling_interval:
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

                                ModbusData.objects.create(device=device, register = register, register_address=register_address, value=last_value, polling_interval = polling_interval)

                                # print(["Value read from register:", value[0]])
                            else:
                                last_value = round(random.uniform(100, 300),2)
                                print("Failed to read from register")
                                ModbusData.objects.create(device=device, register = register, register_address=register_address, value=last_value, polling_interval = polling_interval)

                            
                except Exception as e:
                    print(e)

                c.close()

            elif device.connection_type == 'RTU':

                METHOD = 'RTU'
                COM_PORT = device.port_conf
                STOP_BITS = int(device.stop_bits)
                BYTE_SIZE = int(device.byte_size)
                PARITY = device.parity
                BAUD_RATE = int(device.baud_rate)
                TIMEOUT = int(device.timeout)

                client = ModbusSerialClient(method=METHOD,
                    port=COM_PORT,
                    stopbits=STOP_BITS,
                    bytesize=BYTE_SIZE,
                    parity=PARITY,
                    baudrate=BAUD_RATE,
                    strict=False,
                    timeout=TIMEOUT,
                    )
                
                connection = client.connect()
                
                try:
                    for register in Register.objects.filter(channel=device.id):
                        register_address = register.register_address
                        num_of_registers = register.num_of_registers

                        values = client.read_holding_registers(address=int(register_address),count=int(num_of_registers), slave=1)
                        if register.polling_interval == polling_interval:
                            if values:
                                last_value = values[0]
                                ModbusData.objects.create(device=device, register = register, register_address=register_address, value=values[0])
                                # print(["Value read from register:", value[0]])
                            else:
                                print("Failed to read from register")
                                last_value = 0
                                ModbusData.objects.create(device=device, register = register, register_address=register_address, value=0)

                            
                except Exception as e:
                    print(e)


                c.close()


            if polling_interval == "15 Seconds":
                alarms = Alarm.objects.filter(channel_id=device.id, alarm_trigger="Yes")
                for alarm in alarms:
                    alarm_exists = AlarmTrigger.objects.filter(trigger_alarm_id = alarm.id)
                    # print(len(alarm_exists))
                    if len(alarm_exists) >= 10:
                        # print("Reached the limit")
                        pass
                    else:
                        # print("Saving")
                        AlarmTrigger.objects.create(trigger_name=alarm.alarm_measure, trigger_data = last_value, trigger_device_id=device.id, trigger_alarm_id=alarm.id)
    




@shared_task
def check_and_process_alarms():
    Alarms_record = Alarm.objects.all()
    try:
        master_email = MasterEmail.objects.get(id = 1)
    except:
        master_email = None

    for alarm in Alarms_record:           
        if alarm.alarm_status == 'Enabeld':
            if alarm.alarm_trigger == 'No':
                register_value = Register.objects.filter(name = alarm.alarm_measure, channel_id=alarm.channel_id)
                # print(f"this is alarm channel {alarm.channel_id}")
                device = Device.objects.get(id = alarm.channel_id)

                print([register_value])

                for value in register_value:
                    data = ModbusData.objects.filter(register_address= value.register_address, device_id=alarm.channel_id).last()
                # print(["Alarm value is: ", float(data.value)])
                print(device.device_status)
                if data:
                    if (float(alarm.alarm_min) > float(data.value)) or (float(alarm.alarm_max) < float(data.value)) or device.device_status == 'Offline':
                        print("Device is offline")

                        if (alarm.alarm_activation == "Email"):

                            if master_email:
                                email = EmailMessage(
                                f'An alarm has been triggred on device {alarm.alarm_device}',
                                f'''This is a triggred Alarm on reading {value.name} regarding device {alarm.alarm_device} \n
                                The Alarm have been triggred at {datetime.today().strftime("%Y %b %d %I:%M %p")}''',
                                settings.EMAIL_HOST_USER,
                                [alarm.alarm_emails],
                                )

                                email.send(fail_silently=False) 
                            else:
                                email = EmailMessage(
                                f'An alarm has been triggred on device {alarm.alarm_device}',
                                f'''This is a triggred Alarm on reading {value.name} regarding device {alarm.alarm_device} \n
                                The Alarm have been triggred at {datetime.today().strftime("%Y %b %d %I:%M %p")}''',
                                settings.EMAIL_HOST_USER,
                                [alarm.alarm_emails],
                                )

                                email.send(fail_silently=False)  
                            Alarm.objects.filter(alarm_device=alarm.alarm_device).update(alarm_trigger="Yes", alarm_triggered_at=datetime.today().strftime("%Y %b %d %I:%M %p"))
                        else:
                            Alarm.objects.filter(alarm_device=alarm.alarm_device).update(alarm_trigger="Yes", alarm_triggered_at=datetime.today().strftime("%Y %b %d %I:%M %p"))
                

                               
@shared_task
def send_email_report(report_id):
    report = Report.objects.get(id=report_id)
    try:
        master_email = MasterEmail.objects.get(id = 1)
    except:
        master_email = None

    
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

    if report.report_date_type == "Last_Record":
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
        avg_median_data = {'Devices': [], 'Avg': [], 'Median': [],'Max':[],'Min':[], 'space':[]}

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

    email = EmailMessage(
        f'BCMI Report Message for Device {report.report_device}',
        f'This is a message generated from Device {report.report_device} concerning ',
        settings.EMAIL_HOST_USER,
        [report.report_emails ,master_email.email],
    )
    email.attach(f'report_{report.report_description}_{datetime.now().strftime("%Y_%m_%d")}.csv', csv_data, 'text/csv')  
    
    # Send the email
    email.send(fail_silently=False)
    



@shared_task
def check_device_status():
    devices = Device.objects.all()

    for device in devices:
        if device.connection_type == 'TCP':
            ip_address = device.ip_address
            port_conf = device.port_conf

            client = ModbusClient(host=ip_address, port=int(port_conf), timeout=1)
            client.open()

            if client.is_open:
                device.device_status = 'Online'
                device.save()

            else:
                device.device_status = 'Offline'
                device.save()

            client.close()
        elif device.connection_type == 'RTU':

            METHOD = 'RTU'
            COM_PORT = device.port_conf
            STOP_BITS = int(device.stop_bits)
            BYTE_SIZE = int(device.byte_size)
            PARITY = device.parity
            BAUD_RATE = int(device.baud_rate)
            TIMEOUT = int(device.timeout)

            client = ModbusSerialClient(method=METHOD,
                port=COM_PORT,
                stopbits=STOP_BITS,
                bytesize=BYTE_SIZE,
                parity=PARITY,
                baudrate=BAUD_RATE,
                strict=False,
                timeout=TIMEOUT,
                )
            
            if client.connect():
                device.device_status = 'Online'
                device.save()
            else:
                device.device_status = 'Offline'
                device.save()
            
            client.close()









@shared_task
def create_monthly_table():
    current_day = datetime.now().strftime("%Y_%m_%d")

    print(current_day)

    with connection.cursor() as cursor:
        # Create the new table based on the ModbusData table structure and add additional columns for Register fields
        create_table_query = f"""
        CREATE TABLE modbusdata_{current_day} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id BIGINT,
            register_id BIGINT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            register_address INT NOT NULL,
            value VARCHAR(30) NOT NULL,
            register_name VARCHAR(50),
            device_name VARCHAR(50),
            num_of_registers VARCHAR(15),
            polling_interval VARCHAR(50),
            parameter_name VARCHAR(50)
        ) ENGINE=InnoDB;
        """
        cursor.execute(create_table_query)


@shared_task
def backup_and_clear_data():
    # current_month = datetime.now().strftime('%Y_%m')
    # next_month = (datetime.now().replace(day=28) + timedelta(days=4)).strftime('%Y_%m')
    # current_week = datetime.now().strftime('%Y_%U')

    current_day = datetime.now().strftime("%Y_%m_%d")

    print(current_day)
    
    with connection.cursor() as cursor:
        # Move data to the new table, including Register information and device_name
        move_data_query = f"""
        INSERT INTO modbusdata_{current_day} (device_id, register_id, timestamp, register_address, value, device_name, register_name, num_of_registers, polling_interval, parameter_name)
        SELECT 
            modbusdata.device_id, 
            modbusdata.register_id, 
            modbusdata.timestamp, 
            modbusdata.register_address, 
            modbusdata.value, 
            device.device_name AS device_name,
            register.name AS register_name, 
            register.num_of_registers AS num_of_registers, 
            register.polling_interval AS polling_interval,
            register.parameter_name AS parameter_name
        FROM 
            website_modbusdata AS modbusdata
        JOIN 
            website_register AS register ON modbusdata.register_id = register.id
        JOIN 
            website_device AS device ON modbusdata.device_id = device.id;
        """
        cursor.execute(move_data_query)
        
        # Truncate the current table
        truncate_table_query = "TRUNCATE TABLE website_modbusdata;"
        cursor.execute(truncate_table_query)

        
@shared_task
def create_and_backup_and_delete_database():

    list_names = ["5_Seconds_Check", "15_Seconds_Check", "30_Seconds_Check", "60_Seconds_Check", "5_Minutes_Check", "15_Minutes_Check", "30_Minutes_Check", "60_Minutes_Check", "6_Houres_Check", "12_Houres_Check", "24_Houres_Check"]

    try:
        updated_count = PeriodicTask.objects.filter(name__in=list_names).update(interval_id=16)
    
        # Notify Celery Beat about the changes
        if updated_count > 0:
            PeriodicTasks.update_changed()
        else:
            print("No tasks were updated. Please check the task names and try again.")
    except PeriodicTask.DoesNotExist:
        print("The periodic task with")

    time.sleep(20)

    try:
        create_monthly_table()
        backup_and_clear_data()
    except Exception as e:
        print("Here error 1",e)


    try:
        periodic_task_5_sec = PeriodicTask.objects.get(name="5_Seconds_Check")
        periodic_task_5_sec.interval_id = 7
        periodic_task_5_sec.save()
        periodic_task_15_sec = PeriodicTask.objects.get(name="15_Seconds_Check")
        periodic_task_15_sec.interval_id = 8
        periodic_task_15_sec.save()

        periodic_task_30_sec = PeriodicTask.objects.get(name="30_Seconds_Check")
        periodic_task_30_sec.interval_id = 3
        periodic_task_30_sec.save()

        periodic_task_60_sec = PeriodicTask.objects.get(name="60_Seconds_Check")
        periodic_task_60_sec.interval_id = 1
        periodic_task_60_sec.save()

        periodic_task_5_min = PeriodicTask.objects.get(name="5_Minutes_Check")
        periodic_task_5_min.interval_id = 9
        periodic_task_5_min.save()

        periodic_task_15_min = PeriodicTask.objects.get(name="15_Minutes_Check")
        periodic_task_15_min.interval_id = 10
        periodic_task_15_min.save()

        periodic_task_30_min = PeriodicTask.objects.get(name="30_Minutes_Check")
        periodic_task_30_min.interval_id = 11
        periodic_task_30_min.save()

        periodic_task_60_min = PeriodicTask.objects.get(name="60_Minutes_Check")
        periodic_task_60_min.interval_id = 12
        periodic_task_60_min.save()

        periodic_task_6_hours = PeriodicTask.objects.get(name="6_Houres_Check")
        periodic_task_6_hours.interval_id = 13
        periodic_task_6_hours.save()

        periodic_task_12_hours = PeriodicTask.objects.get(name="12_Houres_Check")
        periodic_task_12_hours.interval_id = 14
        periodic_task_12_hours.save()

        periodic_task_24_hours = PeriodicTask.objects.get(name="24_Houres_Check")
        periodic_task_24_hours.interval_id = 15
        periodic_task_24_hours.save()

        
        # Notify Celery Beat about the changes
        # PeriodicTasks.changed()
        PeriodicTasks.update_changed()

    except PeriodicTask.DoesNotExist:
        print("The periodic task with")


@shared_task
def remove_foreign_key_constraint():
    with connection.cursor() as cursor:
        # Drop the existing foreign key constraint
        drop_constraint_query = """
        ALTER TABLE modbusdata_2024_05_21
        DROP FOREIGN KEY modbusdata_2024_05_21_ibfk_2;
        """
        cursor.execute(drop_constraint_query)

@shared_task
def add_foreign_key_constraint():
    with connection.cursor() as cursor:
        # Add a new foreign key constraint with ON DELETE CASCADE
        add_constraint_query = """
        ALTER TABLE modbusdata_2024_05_21
        ADD CONSTRAINT modbusdata_2024_05_21_ibfk_2
        FOREIGN KEY (register_id)
        REFERENCES website_register (id)
        ON DELETE CASCADE;
        """
        cursor.execute(add_constraint_query)


@shared_task
def test_area_functions():
    c = ModbusClient(host="10.0.0.129", port=int("503"), timeout=1)
    c.open()
    
    
    register_address = 476
    num_of_registers = 4
    value = c.read_holding_registers(int(register_address), int(num_of_registers))
    
    print(f"Value Original {value}")
    print(f"Length of value is  {len(value)}")
    
    if value:
        if value[0] != 0:
            combined_value = (value[0] << 48) | (value[1] << 32) | (value[2] << 16) | value[3]
            print(f"Combined value: {combined_value}")
            
            # Interpret the 64-bit integer as a double-precision floating-point number
            last_value = struct.unpack('d', struct.pack('Q', combined_value))[0]
            print(f"Last value with updates {last_value}")

        else:
            last_value = value[1]
            print(f"Last value without updates{last_value}")

    else:
        last_value = 0
        print("Failed to read from register")