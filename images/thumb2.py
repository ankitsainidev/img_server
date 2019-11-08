from PIL import Image
import os
import filetype
from .models import Client

import shutil
from .allConfig import homeDirectory, drives
homedir = homeDirectory
def saveImage(image, path, changename=0):
    im = Image.open(image)
    im.save(os.path.join(path, str(image)+'.'*changename))
    im.close()
    image.close()
def getthumbint(userid,client):
    print(userid,client)
    client = Client.objects.get(user=userid,name=client)
    if client.thumbs=='EXPIRE':
        return []
    return [int(j)-1 for j in client.thumbs]

def storeToHome(userid, name, images, text):
    clientdir = os.path.join(homedir, userid, name)
    if not os.path.exists(clientdir):
        os.makedirs(clientdir)
    for image in images:
        try:
            saveImage(image, clientdir)
        except FileExistsError:
            try:
                saveImage(image, clientdir, changename=1)
            except:
                saveImage(image, clientdir, changename=2)   
    if text is not None:
        saveText(text,clientdir)
    
def storeToThumb(userid,name,images,textfile):
    for i in getthumbint(userid,name):
        try:
            clientdir = os.path.join(drives[i][1], userid, name)
            if not os.path.exists(clientdir):
                os.makedirs(clientdir)
            for image in images:
                try:
                    saveImage(image, clientdir)
                except FileExistsError:
                    try:
                        saveImage(image, clientdir, changename=1)
                    except:
                        saveImage(image, clientdir, changename=2) 
            if text is not None:
                saveText(text,clientdir)
        except:
            print('some errors are there.')
def storeToThumbAndHome(items,userid,name):
    images = []
    for imageName in ['image','image1','image2']:
        if items[imageName] is not None:
            images.append(items[imageName])

    try:
        f = Client.objects.get(user=userid, name=name)
        return "client already exist"
    except Client.DoesNotExist:
        client = Client(user=userid,name = name, thumbs = ''.join(set(sorted(list(str(items['thumbs']))))))
        client.save()
        storeToHome(userid,name,images,items['textfile'])
        storeToThumb(userid,name,images,items['textfile'])

def getclients(user):
    userpath = os.path.join(homedir,user)
    if os.path.exists(userpath):
        toret =  os.listdir(userpath)
        if os.path.exists(os.path.join(userpath,'expire')):
            toret.remove('expire')
            toret += os.listdir(os.path.join(userpath,'expire'))
        return toret
    return None
def deleteFromThumb(userid,client):
    for i in getthumbint(userid,client):
        
        shutil.rmtree(os.path.join(drives[i][1],userid,client), ignore_errors=True)
       
    
def deleteFromHome(userid,client):
    shutil.rmtree(os.path.join(homedir,userid,client), ignore_errors=True)
    
def moveToExpire(userid,client):
    shutil.move(os.path.join(homedir,userid,client),os.path.join(homedir,userid,'expire',client))
    
def expireClient(userid,client):
    deleteFromThumb(userid,client)
    moveToExpire(userid,client)
    client = Client.objects.get(user = userid, name = client)
    client.thumbs='EXPIRE'
    client.save()

def deleteClient(userid,client):
    
    deleteFromThumb(userid,client)
    deleteFromHome(userid,client)
    Client.objects.get(user = userid, name = client).delete()
#adsflkjdfjds
#dslfjdslf
#ldsfjldsf
#take a look bro
#take a look
def checkSync(userid):
    pass
def sync(userid):
    pass
def getPathsAndInfo(user, client):
    clientPath = os.path.join(homedir,user,client)
    if not os.path.exists(clientPath):
        clientPath = os.path.join(homedir,user,'expire',client)
    if not os.path.exists(clientPath):
        return None
    else:
        Paths =  os.listdir(clientPath)
        Paths = [os.path.join(clientPath,path) for path in Paths]
        imagePath = []
        
        for path in Paths:
            
            k = filetype.guess(path)
            if k is not None:
                f = k.mime
                if f.find('image') !=-1:
                    imagePath.append(path)
                else:
                    textpath = path
            else:
                textpath = path
        
    thumbs = Client.objects.get(user=user,name=client)
    return imagePath, client, thumbs.thumbs, textpath
def deleteImage(path):
    os.remove(path)
def UpdateClient(items,user,client):
    myclient = Client.objects.get(user=user,name=client)
    if items['name'] is not None and items['name']!='':
        myclient.name=items['name']
    images = []
    for imageName in ['image','image1','image2']:
        if items[imageName] is not None:
            images.append(items[imageName])
    if myclient.thumbs=='EXPIRE':
        client=os.path.join('expire',client)
    storeToHome(user,client,images,items['textfile'])
    storeToThumb(user,client,images,items['textfile'])
    if items['thumbs'] is not None:
        myclient.thumbs = items['thumbs']

    myclient.save()
    if myclient.thumbs=='EXPIRE':
        shutil.move(os.path.join(homedir,user,client),os.path.join(homedir,user,'expire',myclient.name))
    else:
        shutil.move(os.path.join(homedir,user,client),os.path.join(homedir,user,myclient.name))
def drivedata(path):
    drive = os.statvfs(path)
    total = int((float(drive.f_bsize*drive.f_blocks)/1024/1024/1024)*100)/100
    free = int((float(drive.f_bsize*(drive.f_bfree))/1024/1024/1024)*100)/100
    usedratio = 1-(free/total)
    return total,free,usedratio
def alldrivedata(drives=drives):
    toret = [(drive[0],*drivedata(drive[1])) for drive in drives]
    return toret
