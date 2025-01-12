from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *
from django.forms import DateInput
from bootstrap_datepicker_plus.widgets import DatePickerInput, DateTimePickerInput  

from datetime import datetime, timedelta

class HourMinuteWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        hours = [(str(i), str(i).zfill(2)) for i in range(24)]
        minutes = [(str(i), str(i).zfill(2)) for i in range(60)]
        widgets = [
            forms.Select(choices=hours, attrs={"class": "form-control col-md-6"}),
            forms.Select(choices=minutes, attrs={"class": "form-control col-md-6"})
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(':')
        return [None, None]

class HourMinuteField(forms.MultiValueField):
    widget = HourMinuteWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=[(str(i), str(i).zfill(2)) for i in range(24)]),  # Hours
            forms.ChoiceField(choices=[(str(i), str(i).zfill(2)) for i in range(60)]),  # Minutes
        )
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            # Combine the selected hour and minute into a single string
            return '%s:%s' % (data_list[0], data_list[1])
        return None
    


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'class':"form-control", 'placeholder':"Email Address"}))
    first_name = forms.CharField(label='', max_length=50, widget=forms.TextInput(attrs={'class':"form-control", 'placeholder':"First Name"}))
    last_name = forms.CharField(label='', max_length=50, widget=forms.TextInput(attrs={'class':"form-control", 'placeholder':"Last Name"}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'	

class AddRecordForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"First Name", "class":"form-control"}), label='')
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"last Name", "class":"form-control"}), label='')
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"phone", "class":"form-control"}), label='')
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"address", "class":"form-control"}), label='')
    city = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"city", "class":"form-control"}), label='')
    state = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"state", "class":"form-control"}), label='')
    zipcode = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"zipcode", "class":"form-control"}), label='')

    class Meta:
        model = Record
        exclude = ('user',)

class AddDeviceForm(forms.ModelForm):
    alphabet_choices = [(" Group " + chr(i), " Group " + chr(i)) for i in range(ord('A'), ord('Z') + 1)]

    device_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Device Name", "class":"form-control"}), label='Device Name')
    connection_type = forms.ChoiceField(choices = (('TCP','TCP'), ('RTU','RTU')), required=False, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='Connection Type')
    
    ip_address = forms.CharField(initial='', required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Ip Address", "class":"form-control"}), label='')
    port_conf = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Port--> 'COM3' or '503' ", "class":"form-control"}), label='')
    
    signals = forms.ChoiceField(choices = (('Enabeld','Enabel'), ('Disabled','Disable')), required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='') 
    manufacturer = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Manufacturar", "class":"form-control"}), label='')
    
    stop_bits = forms.IntegerField(initial=1, required=False, widget=forms.widgets.NumberInput(attrs={"placeholder":"Stop Bits", "class":"form-control"}), label='')
    byte_size = forms.IntegerField(initial=8, required=False, widget=forms.widgets.NumberInput(attrs={"placeholder":"Byte Size", "class":"form-control"}), label='')
    parity = forms.ChoiceField(choices=(('N','None'), ('E','Even'), ('O','Odd')), required=False, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')
    baud_rate = forms.ChoiceField(choices=(
        ('1200', '1200'),
        ('2400', '2400'),
        ('4800', '4800'),
        ('9600', '9600'),
        ('19200', '19200'),
        ('38400', '38400'),
        ('57600', '57600'),
        ('115200', '115200'),
    ), initial='9600', required=False, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')
    timeout = forms.IntegerField(initial=1,required=False, widget=forms.widgets.NumberInput(attrs={"placeholder":"Timeout", "class":"form-control"}), label='')
    
    group = forms.ChoiceField(choices=alphabet_choices, required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')

    class Meta:
        model = Device
        exclude = ("company_name", "device_status")


class AddAlarmForm(forms.ModelForm):
    alarm_device = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    alarm_measure = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')

    alarm_description = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Alarm Description", "class":"form-control"}), label='')
    alarm_min = forms.IntegerField(required=True, widget=forms.widgets.NumberInput(attrs={"placeholder":"Minimum Value", "class": "form-control"}), label='')
    alarm_max = forms.IntegerField(required=True, widget=forms.widgets.NumberInput(attrs={"placeholder":"Maximum Value", "class": "form-control"}), label='')
    alarm_activation = forms.ChoiceField(choices = (('Notification','Notification'), ('Email','Email'),), required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')
    alarm_status = forms.ChoiceField(choices = (('Enabeld','Enabel'), ('Disabled','Disable')), required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')
    alarm_emails = forms.EmailField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Email", "class":"form-control"}), label='')

    def __init__(self, device_pk, *args, **kwargs):
        super(AddAlarmForm, self).__init__(*args, **kwargs)
        
        device = Device.objects.get(pk=device_pk)
        self.fields['alarm_device'].choices = [(device.device_name, device.device_name)]
        self.fields['alarm_measure'].choices = [(register.name, register.name) for register in device.register_set.all()]
        
    class Meta:
        model = Alarm
        fields = ('alarm_device','alarm_measure', 'alarm_description', 'alarm_min', 'alarm_max', 'alarm_activation', 'alarm_status', 'alarm_emails')


class ReportDateForm(forms.Form):
    today = datetime.today()
    first_day_of_month = today.replace(day=1, hour=0, minute=0).strftime('%Y-%m-%d %H:%M')
    current_day = today.strftime('%Y-%m-%d %H:%M')

    report_date_type = forms.ChoiceField(choices=[
        ('Last_Record', 'All Records'),
        ('From_To', 'From-To'),
    ], required=True, widget=forms.widgets.Select(attrs={'class':'form-select', 'id': 'report_date_type'}), label='')

    report_date_from = forms.DateTimeField(
        required=False,
        widget=DateTimePickerInput(
            options={
                "format": "YYYY-MM-DD HH:mm",
                "showClose": True,
                "showClear": True,
                "showTodayButton": True,
                "minDate": first_day_of_month,
                "maxDate": current_day,
            },
            attrs={"class": "form-control", "id": "report_date_from"}
        ),
        initial=first_day_of_month,
        label='From'
    )

    report_date_to = forms.DateTimeField(
        required=False,
        widget=DateTimePickerInput(
            options={
                "format": "YYYY-MM-DD HH:mm",
                "showClose": True,
                "showClear": True,
                "showTodayButton": True,
                "minDate": first_day_of_month,
                "maxDate": current_day,
            },
            attrs={"class": "form-control", "id": "report_date_to"}
        ),
        initial=current_day,
        label='To'
    )

class AddReportForm(forms.ModelForm):
    all_measures = []
    devices = Device.objects.all()

    device_choices = [('All_Devices', 'All Devices')] + [(device.device_name, device.device_name) for device in devices]
    
    for device in devices:
        measures = Register.objects.filter(channel_id=device.id)
        for measure in measures:
            all_measures.append((f"{measure.name}, {measure.channel}", f"{measure.name}, {measure.channel}"))

    report_device = forms.MultipleChoiceField(
        choices=device_choices,
        required=True,
        widget=forms.SelectMultiple(attrs={
            "class": "selectpicker",
            "data-width": "100%",
            "multiple": None,
            "data-live-search": "true"
        }),
        label=''
    )
    report_measure = forms.MultipleChoiceField(
        choices=all_measures,
        required=True,
        widget=forms.SelectMultiple(attrs={
            "class": "selectpicker",
            "data-width": "100%",
            "multiple": None,
            "data-live-search": "true"
        }),
        label=''
    )
    
    report_activation = forms.ChoiceField(choices=[
        ('Monthly', 'Monthly'),
        ('*', 'Daily'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
    ], required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')

    report_date_type = forms.ChoiceField(choices=[
        ('Last_Record', 'Last Record'),
        ('All_Records', 'All Records'),
    ], required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')

    report_status = forms.ChoiceField(choices=[('Enabled', 'Enable'), ('Disabled', 'Disable')], required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')
    report_timezone = forms.ChoiceField(choices=[('Asia/Riyadh', 'Asia/Riyadh'), ("", "")], required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='', initial=0)

    report_description = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Report Description", "class":"form-control"}), label='')
    report_interval_hours = forms.ChoiceField(choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(24)], required=True, label='Hour', widget=forms.widgets.Select(attrs={"class":"form-control"}))
    report_interval_minutes = forms.ChoiceField(choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(60)], required=True, label='Minutes', widget=forms.widgets.Select(attrs={"class":"form-control"}))
    report_emails = forms.EmailField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Email", "class":"form-control"}), label='')

    def __init__(self, *args, **kwargs):
        super(AddReportForm, self).__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['report_device'].initial = self.instance.report_device
            self.fields['report_activation'].initial = self.instance.report_activation
            self.fields['report_status'].initial = self.instance.report_status
            self.fields['report_interval_minutes'].initial = self.instance.report_interval_minutes
            self.fields['report_interval_hours'].initial = self.instance.report_interval_hours
            self.fields['report_emails'].initial = self.instance.report_emails
            self.fields['report_description'].initial = self.instance.report_description

    class Meta:
        model = Report
        fields = '__all__'



class RegisterForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Name", "class":"form-control"}), label='')
    register_address = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Register Address", "class":"form-control"}), label='')
    num_of_registers = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Number of Registers", "class":"form-control"}), label='')
    polling_interval = forms.ChoiceField(choices = (('None','None'),
                                                    ('5 Seconds','5 Seconds'),
                                                    ('15 Seconds','15 Seconds'),
                                                    ('30 Seconds','30 Seconds'),
                                                    ('60 Seconds','60 Seconds'),
                                                    ('5 Minutes','5 Minutes'),
                                                    ('15 Minutes','15 Minutes'),
                                                    ('30 Minutes','30 Minutes'),
                                                    ('60 Minutes','60 Minutes'),
                                                    ('6 Houres','6 Houres'),
                                                    ('12 Houres','12 Houres'),
                                                    ('24 Houres','24 Houres'),
                                                    ), required=True, widget=forms.widgets.Select(attrs={'class':'form-select'}), label='')
    dividing_parameter = forms.IntegerField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Division Factor example -> 10 or 100 or 1000 ...  Input 1 for None", "class":"form-control"}), label='')
    parameter_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Parameter -> Volt (V), Amp(A), Watts(W) ...", "class":"form-control"}), label='')
    
    class Meta:
        model = Register
        fields = ['name', 'register_address', 'num_of_registers', "dividing_parameter", 'parameter_name', 'polling_interval',]

class IPSearch(forms.ModelForm):
    IP_section1 = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"ip segment", "class":"form-control"}), label='')
    IP_section2 = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"ip segment", "class":"form-control"}), label='')
    IP_section3 = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"ip segment", "class":"form-control"}), label='')
    start_ip = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"start IP", "class":"form-control"}), label='')
    end_ip = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"End IP", "class":"form-control"}), label='')
    class Meta:
        model = Register
        fields = ['IP_section1', 'IP_section2', 'IP_section3', 'start_ip', 'end_ip']


class Diagram_Charts_Form(forms.ModelForm):
    all_measures = []


    chart_1_title = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"", "class":"form-control"}), label='', initial="None")
    chart_1_1 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_1_min = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"0"}), label='')
    chart_1_max = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"300"}), label='')
    chart_1_thresh_hold = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"250"}), label='')

    chart_1_2 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_1_3 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_1_4 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_1_5 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')

    chart_2_title = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"", "class":"form-control"}), label='', initial="None")
    chart_2_1 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_2_min = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"0"}), label='')
    chart_2_max = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"300"}), label='')
    chart_2_thresh_hold = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"250"}), label='')

    chart_2_2 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_2_3 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_2_4 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_2_5 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')


    chart_3_title = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"", "class":"form-control"}), label='', initial="None")
    chart_3_1 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_3_min = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"0"}), label='')
    chart_3_max = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"300"}), label='')
    chart_3_thresh_hold = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"250"}), label='')

    chart_3_2 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_3_3 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_3_4 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_3_5 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')


    chart_4_title = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"", "class":"form-control"}), label='', initial="None")
    chart_4_1 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_4_min = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"0"}), label='')
    chart_4_max = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"300"}), label='')
    chart_4_thresh_hold = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"250"}), label='')

    chart_4_2 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_4_3 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_4_4 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_4_5 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')


    chart_5_title = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"", "class":"form-control"}), label='', initial="None")
    chart_5_1 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_5_min = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"0"}), label='')
    chart_5_max = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"300"}), label='')
    chart_5_thresh_hold = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"250"}), label='')

    chart_5_2 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_5_3 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_5_4 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_5_5 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')

    
    chart_6_title = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"", "class":"form-control"}), label='', initial="None")
    chart_6_1 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_6_min = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"0"}), label='')
    chart_6_max = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"300"}), label='')
    chart_6_thresh_hold = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"class": "form-control", "value":"250"}), label='')

    chart_6_2 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_6_3 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_6_4 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')
    chart_6_5 = forms.ChoiceField(required=True, widget=forms.widgets.Select(attrs={"class": "form-control"}), label='')

    graph_1 = forms.MultipleChoiceField(
        choices=all_measures,
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "selectpicker",
            "data-width": "100%",
            "multiple": None,
            "data-live-search": "true"
        }),
        label=''
    )

    def __init__(self, device_pk, *args, **kwargs):
        super(Diagram_Charts_Form, self).__init__(*args, **kwargs)
        
        device = Device.objects.get(pk=device_pk)
        Measuerments = [('None', 'None')] + [(register.name, register.name) for register in device.register_set.all()]
        self.fields['chart_1_1'].choices = Measuerments
        self.fields['chart_1_2'].choices = Measuerments
        self.fields['chart_1_3'].choices = Measuerments
        self.fields['chart_1_4'].choices = Measuerments
        self.fields['chart_1_5'].choices = Measuerments

        self.fields['chart_2_1'].choices = Measuerments
        self.fields['chart_2_2'].choices = Measuerments
        self.fields['chart_2_3'].choices = Measuerments
        self.fields['chart_2_4'].choices = Measuerments
        self.fields['chart_2_5'].choices = Measuerments

        self.fields['chart_3_1'].choices = Measuerments
        self.fields['chart_3_2'].choices = Measuerments
        self.fields['chart_3_3'].choices = Measuerments
        self.fields['chart_3_4'].choices = Measuerments
        self.fields['chart_3_5'].choices = Measuerments

        self.fields['chart_4_1'].choices = Measuerments
        self.fields['chart_4_2'].choices = Measuerments
        self.fields['chart_4_3'].choices = Measuerments
        self.fields['chart_4_4'].choices = Measuerments
        self.fields['chart_4_5'].choices = Measuerments

        self.fields['chart_5_1'].choices = Measuerments
        self.fields['chart_5_2'].choices = Measuerments
        self.fields['chart_5_3'].choices = Measuerments
        self.fields['chart_5_4'].choices = Measuerments
        self.fields['chart_5_5'].choices = Measuerments

        self.fields['chart_6_1'].choices = Measuerments
        self.fields['chart_6_2'].choices = Measuerments
        self.fields['chart_6_3'].choices = Measuerments
        self.fields['chart_6_4'].choices = Measuerments
        self.fields['chart_6_5'].choices = Measuerments

        self.fields["graph_1"].choices = Measuerments[1:]

    class Meta:
        model = Diagram_Charts
        fields = '__all__'
        exclude = ("device",)
        # fields = ["chart_1_title", "chart_2_title", "chart_1_measure"]






