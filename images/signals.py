from django.contrib.auth.signals import user_logged_in
from .allConfig import mainuser

def set_status_online(sender, user, request, **kwargs):
    
    if user.get_username()==mainuser:
        import subprocess
        subprocess.call("/maintenancemode.sh")
        print("Maintenance Mode Entered")
        import sys
        sys.exit()
        

user_logged_in.connect(set_status_online)