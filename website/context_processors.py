from .models import *


def base_page(request):
    alarm_record = Alarm.objects.filter(alarm_trigger="Yes")
    alarms_list = []
    
    for alarm in alarm_record:
        alarms_list.append(f"{alarm.alarm_device}")
    
    # Join the alarms_list into a single string with a separator of your choice, e.g., "; "
    alarms_string = "; ".join(alarms_list)
    num_triggred_alarms = alarm_record.count()
    
    return {
        'alarm_record':alarm_record,
        'num_triggred_alarms': num_triggred_alarms,
        'alarms_string': alarms_string,
    }