# signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import signals
from .models import *
from .tasks import *
from datetime import timedelta
from celery.schedules import crontab

@receiver(post_save, sender=Report)
def schedule_email_report(sender, instance, created, **kwargs):
    report_id = instance.id
    create_report_tasks.apply_async((report_id,))


@receiver(post_delete, sender=Report)
def schedule_email_report(sender, instance, **kwargs):

    report_id = instance.id
    delete_report_tasks.apply_async((report_id,))


#Temp Solution needs to be tried before production
###############################################################################################################################################################################################################################
@receiver(post_save, sender=Register)
def add_new_register(sender, instance, created, **kwargs):
    counter = 0
    print(f"This is the instance Post Save {instance.polling_interval}")
    print(f"This is the created {created}")

    ModbusData.objects.filter(register_id=instance.id).delete()

    registers = Register.objects.filter(channel_id = instance.channel_id, polling_interval = instance.polling_interval)
    registers_first = registers.first()

    ModbusData.objects.filter(device_id = registers_first.channel_id, polling_interval = registers_first.polling_interval).delete()



@receiver(post_delete, sender=Register)
def delete_new_register(sender, instance, **kwargs):
    # Delete all ModbusData related to the specific register and polling interval

    # ModbusData.objects.filter(register_id=instance.id).delete()
    print("Deleted")

    report_id = instance.id
    print('Deleted register ', report_id)
    print(f'Deleted channel id {instance.channel_id}')
###############################################################################################################################################################################################################################

#Actual solution worked in production 