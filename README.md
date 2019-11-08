# img_server
Django website to store and destribute images on thumb drives

## Set Up
All you need to edit is allConfig.py file inside /images and settings.py(recpatch keys at bottom of file) file inside /project
<br>
all the commands in order are as follows
$pip3 install django
<br>
$pip3 install filetype
<br>
$pip3 install django-recaptcha
<br>
$pip3 install pillow
<br>
$python3 manage.py makemigrations
<br>
$python3 manage.py migrate
<br>
To create first user
<br>
$python3 manage.py createsuperuser
<br>

Then execute following command to run the server anytime:
<br>
$python3 manage.py runserver
<br>
