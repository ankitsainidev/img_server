from PIL import Image
import os
import filetype
from .models import Client
import shutil
from .allConfig import homeDirectory, drives
homedir = homeDirectory

def saveImage(image, path, changename=0):
    """give the path and image and it will save it"""
    im = Image.open(image)
    im.save(os.path.join(path, str(image)+'.'*changename))
    im.close()
    image.close()
def getthumbint(userid,client):
    """give userid and client name to get a list of their drives"""
    print(userid,client)
    client = Client.objects.get(user=userid,name=client)
    if client.thumbs=='EXPIRE':
        return []
    return [int(j)-1 for j in client.thumbs]
def saveText(file, path):
    """give a text file and a path and it will save it"""
    files = os.listdir(path)
    for fil in files:
        if filetype.guess(os.path.join(path,fil)) is None:
            os.remove(os.path.join(path,fil)) 
    tx = open(os.path.join(path, str(file)), 'wb')
    file.open()
    tx.write(file.read())
    file.close()
    tx.close()

def storeToHome(userid, name, images, text=None, expire=False):
    """give userid and client name it'll save it to home directory"""
    if expire:
        clientdir= os.path.join(homedir,userid,'expire',name)
    else:
        clientdir = os.path.join(homedir, userid, name)
    if not os.path.exists(clientdir):
        os.makedirs(clientdir)
    for image in images:
        saveImage(image, clientdir)
          
    if text is not None:
        saveText(text,clientdir)


def storeToThumb(userid,name,images,textfile=None,drivelist=[]):
    for i in drivelist:
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
            if textfile is not None:
                saveText(textfile,clientdir)
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
        client = Client(user=userid,name = name, thumbs = items['thumbs'])
        client.save()
        storeToHome(userid,name,images,items['textfile'])
        storeToThumb(userid,name,images,items['textfile'],getthumbint(userid,name))
def getclients(user):
    userpath = os.path.join(homedir,user)
    if os.path.exists(userpath):
        toret =  os.listdir(userpath)
        if os.path.exists(os.path.join(userpath,'expire')):
            toret.remove('expire')
            toret += os.listdir(os.path.join(userpath,'expire'))
        return toret
    return None
def deleteFromThumb(userid,client,drivelist):
    for drive in drivelist:
        shutil.rmtree(os.path.join(drives[drive][1],userid,client), ignore_errors=True)
def deleteFromHome(userid,client):
    user = Client.objects.get(user=userid,name=client)
    if user.thumbs=='EXPIRE':
        shutil.rmtree(os.path.join(homedir,userid,'expire',client), ignore_errors=True)
    else:
        shutil.rmtree(os.path.join(homedir,userid,client), ignore_errors=True)
def moveToExpire(userid,client):
    shutil.move(os.path.join(homedir,userid,client),os.path.join(homedir,userid,'expire',client))
def expireClient(userid,client):
    deleteFromThumb(userid,client,getthumbint(userid,client))
    moveToExpire(userid,client)
    client = Client.objects.get(user = userid, name = client)
    client.thumbs='EXPIRE'
    client.save()
def deleteClient(userid,client):
    
    deleteFromThumb(userid,client,getthumbint(userid,client))
    deleteFromHome(userid,client)
    Client.objects.get(user = userid, name = client).delete()
def getPathsAndInfo(user, client):
    clientPath = os.path.join(homedir,user,client)
    imagePath = []
    textpath = ''
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
def drivedata(path):
    drive = os.statvfs(path)
    total = int((float(drive.f_bsize*drive.f_blocks)/1024/1024/1024)*100)/100
    free = int((float(drive.f_bsize*(drive.f_bfree))/1024/1024/1024)*100)/100
    usedratio = 1-(free/total)
    return total,free,usedratio
def alldrivedata(drives=drives):
    toret = [(drive[0],*drivedata(drive[1])) for drive in drives]
    return toret
def sync(user, client, drive=None):
    clientpath = os.path.join(homedir, user, client)
    if drive is None:
        if getthumbint(user,client) == []:
            return None
        
        for i in getthumbint(user,client):
            shutil.copytree(clientpath,os.path.join(drives[i][1],user,client))
    else:
        if drive in getthumbint(user,client):
            shutil.copytree(clientpath,os.path.join(drives[drive][1],user,client))
        
def UpdateClient(items,user,client):
    myclient = Client.objects.get(user=user,name=client)
    prevthumb = myclient.thumbs
    prevlocation = ''
    if myclient.thumbs=='EXPIRE':
        prevlocation = os.path.join(homedir,user,'expire',client)
    else:
        prevlocation = os.path.join(homedir,user, client)
    if items['name'] is not None and items['name']!='':
        myclient.name=items['name']
    images = []
    for imageName in ['image','image1','image2']:
        if items[imageName] is not None:
            images.append(items[imageName])
        
    storeToHome(user,client,images,items['textfile'],expire=(myclient.thumbs=='EXPIRE'))
    myclient.save()
    
    if items['thumbs'] is not None:
        myclient.thumbs = items['thumbs']
        
        myclient.save()
    currpath = ''
    if myclient.thumbs=='EXPIRE':
        currpath = os.path.join(homedir,myclient.user,'expire', myclient.name)
    else:
        currpath = os.path.join(homedir,myclient.user,myclient.name)
    shutil.move(prevlocation,currpath)
    if items['thumbs'] is not None:
        deleteFromThumb(user,myclient.name,getthumbint(user,myclient.name))
        sync(user, myclient.name)
def deleteImage(path):
    os.remove(path)
