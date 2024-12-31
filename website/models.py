from django.db import models
from django.utils import timezone

class Record(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    Address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=20)

    def __str__(self):
        return (f'{self.first_name} {self.last_name}')
    

class Voltage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    L1 = models.CharField(max_length=20)
    frequency = models.CharField(max_length=20)

    def __str__(self):
        return (f"{self.created_at} {self.L1}")
    
class Company(models.Model):
    company_name = models.CharField(max_length=50)
    company_discreption = models.CharField(max_length=100)
    num_devices = models.CharField(max_length=10)
    licence_type = models.CharField(max_length=50)

    def __str__(self):
        return (f"{self.company_name} {self.company_discreption}")
        


# class TriggredAlarms(models.Model)
    
class Device(models.Model):
    company_name = models.CharField(max_length=50)
    device_name = models.CharField(max_length=50)
    connection_type = models.CharField(max_length=30)
    port_conf = models.CharField(max_length=30)
    device_status = models.CharField(max_length=30)

    stop_bits = models.CharField(max_length=5)
    byte_size = models.CharField(max_length=5)
    parity = models.CharField(max_length=5)
    baud_rate = models.CharField(max_length=15)
    timeout = models.CharField(max_length=5)

    ip_address = models.CharField(max_length=50)
    signals = models.CharField(max_length=30)
    manufacturer = models.CharField(max_length=50)

    group = models.CharField(max_length=15)

    def __str__(self):
        return (f"{self.device_name}")


class Report(models.Model):
    # channel = models.ManyToManyField(Device)
    report_status = models.CharField(max_length=30)
    report_device = models.TextField()
    report_measure = models.TextField()
    # report_interval = models.CharField(max_length=30)
    report_interval_hours = models.CharField(max_length=30)
    report_interval_minutes = models.CharField(max_length=30)
    report_description = models.TextField()
    report_activation = models.CharField(max_length=30)
    report_emails = models.CharField(max_length=30)
    report_timezone = models.CharField(max_length=30)

    report_date_type = models.CharField(max_length=50)
    # report_date_from = models.DateField()
    # report_date_to = models.DateField()

class Alarm(models.Model):
    channel = models.ForeignKey(Device, on_delete=models.CASCADE)
    alarm_status = models.CharField(max_length=30)
    alarm_device = models.CharField(max_length=30)
    alarm_measure = models.CharField(max_length=50)
    alarm_description = models.TextField()
    alarm_min = models.CharField(max_length=30)
    alarm_max = models.CharField(max_length=30)
    alarm_activation = models.CharField(max_length=30)
    alarm_emails = models.CharField(max_length=50)
    alarm_trigger = models.CharField(max_length=50, default='No')
    alarm_triggered_at = models.CharField(max_length=50, default='')

class AlarmTrigger(models.Model):
    trigger_device = models.ForeignKey(Device, on_delete=models.CASCADE)
    trigger_alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    trigger_name = models.CharField(max_length=30)
    trigger_data = models.CharField(max_length=30)

class Register(models.Model):
    channel = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    register_address = models.CharField(max_length=15)
    num_of_registers = models.CharField(max_length=15)
    dividing_parameter = models.IntegerField()
    polling_interval = models.CharField(max_length=50)
    parameter_name = models.CharField(max_length=50)
    
    def __str__(self):
        return (f"{self.name} {self.channel}")
    

class ModbusData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    register = models.ForeignKey(Register, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    register_address = models.IntegerField()
    value = models.CharField(max_length=30)
    polling_interval = models.CharField(max_length=50)

class License(models.Model):
    encrypted_license_key = models.CharField(max_length=255, unique=True)
    max_devices = models.IntegerField(default=40)

    def __str__(self):
        return f"License - {self.encrypted_license_key}"


class MasterEmail(models.Model):
    email = models.TextField()


class Diagram_Charts(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    chart_1_title = models.CharField(max_length=50)

    chart_1_1 = models.CharField(max_length=50)
    chart_1_max = models.IntegerField(default= 1)
    chart_1_min = models.IntegerField(default= 1)
    chart_1_thresh_hold = models.IntegerField(default= 1)

    chart_1_2 = models.CharField(max_length=50)
    chart_1_3 = models.CharField(max_length=50)
    chart_1_4 = models.CharField(max_length=50)
    chart_1_5 = models.CharField(max_length=50)

    chart_2_title = models.CharField(max_length=50)
    chart_2_max = models.IntegerField(default= 1)
    chart_2_min = models.IntegerField(default= 1)
    chart_2_thresh_hold = models.IntegerField(default= 1)

    chart_2_1 = models.CharField(max_length=50)
    chart_2_2 = models.CharField(max_length=50)
    chart_2_3 = models.CharField(max_length=50)
    chart_2_4 = models.CharField(max_length=50)
    chart_2_5 = models.CharField(max_length=50)

    chart_3_title = models.CharField(max_length=50)
    chart_3_max = models.IntegerField(default= 1)
    chart_3_min = models.IntegerField( default= 1)
    chart_3_thresh_hold = models.IntegerField(default= 1)

    chart_3_1 = models.CharField(max_length=50)
    chart_3_2 = models.CharField(max_length=50)
    chart_3_3 = models.CharField(max_length=50)
    chart_3_4 = models.CharField(max_length=50)
    chart_3_5 =models.CharField(max_length=50)

    chart_4_title = models.CharField(max_length=50)
    chart_4_max = models.IntegerField(default = 1)
    chart_4_min = models.IntegerField(default= 1)
    chart_4_thresh_hold = models.IntegerField(default= 1)
    
    chart_4_1 = models.CharField(max_length=50)
    chart_4_2 = models.CharField(max_length=50)
    chart_4_3 = models.CharField(max_length=50)
    chart_4_4 = models.CharField(max_length=50)
    chart_4_5 = models.CharField(max_length=50)

    chart_5_title = models.CharField(max_length=50)
    chart_5_max = models.IntegerField(default = 1)
    chart_5_min = models.IntegerField(default= 1)
    chart_5_thresh_hold = models.IntegerField(default= 1)
    
    chart_5_1 = models.CharField(max_length=50)
    chart_5_2 = models.CharField(max_length=50)
    chart_5_3 = models.CharField(max_length=50)
    chart_5_4 = models.CharField(max_length=50)
    chart_5_5 =models.CharField(max_length=50)

    chart_6_title = models.CharField(max_length=50)
    chart_6_max = models.IntegerField(default = 1)
    chart_6_min = models.IntegerField(default= 1)
    chart_6_thresh_hold = models.IntegerField(default= 1)

    chart_6_1 = models.CharField(max_length=50)
    chart_6_2 = models.CharField(max_length=50)
    chart_6_3 = models.CharField(max_length=50)
    chart_6_4 = models.CharField(max_length=50)
    chart_6_5 = models.CharField(max_length=50)

    graph_1 = models.TextField()