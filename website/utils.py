from .models import License, Device
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from decouple import config

SECRET_KEY = config('ENCRYPTION_KEY').encode()
fernet = Fernet(SECRET_KEY)

def can_add_device():
    try:
        license = License.objects.first()  # Assuming a single license record
        decrypted_key = decrypt_license_key(license.encrypted_license_key)
        # Add additional validation for the license key if needed
    except License.DoesNotExist:
        print("License not found.")
        return False, "License not found."
    except Exception as e:
        print("License error")
        return False, str(e)

    device_count = Device.objects.count()
    if device_count >= license.max_devices:
        return False, "Maximum number of devices reached."
    
    return True, "Device can be added."

def encrypt_license_key(license_key):
    encrypted_key = fernet.encrypt(license_key.encode())
    return encrypted_key.decode()

def decrypt_license_key(encrypted_key):
    decrypted_key = fernet.decrypt(encrypted_key.encode())
    return decrypted_key.decode()


def generate_license(max_devices):
    import uuid
    license_key = str(uuid.uuid4())
    encrypted_key = encrypt_license_key(license_key)

    if License.objects.exists():
        new_license = License.objects.first()
        new_license.encrypted_license_key = encrypted_key
        new_license.max_devices = max_devices
        new_license.save()
    else:
        new_license = License.objects.create(encrypted_license_key=encrypted_key, max_devices=max_devices)
        new_license.save()
    return license_key