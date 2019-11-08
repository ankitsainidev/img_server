import shutil
import os
from PIL import Image
import filetype
from .models import Client
from .allConfig import homeDirectory
homedir = homeDirectory
from .allConfig import drives,drivelimit
from .thumb import alldrivedata
drives = [drive[1] for drive in drives]
def suggest(user, s):
    query = Client.objects.filter(user = user)
    k = []
    i = 0
    while len(k) < 3:
        if not query.filter(name=s+f'{i}').exists():
            k.append(s+f'{i}')
        i+=1
    return ', '.join(k)


def saveText(file, path):
    """give a text file and a path and it will save it"""
    files = os.listdir(path)
    for fil in files:
        if filetype.guess(os.path.join(path, fil)) is None:
            os.remove(os.path.join(path, fil))
    tx = open(os.path.join(path, str(file)), 'wb')
    file.open()
    tx.write(file.read())
    file.close()
    tx.close()


def saveImage(image, path):
    """give the path and image and it will save it"""
    im = Image.open(image)
    imgname = str(image).split('.')[0]
    savename = imgname+'.'+str(image).split('.')[-1]
    while os.path.exists(os.path.join(path, savename)):
        imgname = imgname + '(1)'
        savename = imgname+'.'+str(image).split('.')[-1]
    
    im.save(os.path.join(path, savename))
    im.close()
    image.close()


def moveDir(path, target):
    if os.path.exists(path):
        shutil.move(path, target)
    else:
        raise Exception('path doesn\'t exists')


def copyDir(path, targets):
    if os.path.exists(path):
        for target in targets:
            shutil.copytree(path, target)
    else:
        raise Exception('path doesn\'t exists')


def deleteDir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        raise Exception('path doesn\'t exists')


# def expireClient(user, client):
#     # TODO: database
#     d = getPath(user, client, 'EXPIRE')
#     for path in d['todelete']:
#         deleteDir(path)
#     moveDir(d['tomove'][0], d['tomove'][1])


# def changeDrives(user, client, drives):
#     d = getPath(user, client, drives)
#     for path in d['todelete']:
#         deleteDir(path)
#     copyDir(d['tocopy'][0], d['tocopy'][1])


# def saveClient():

#     pass
# def createClient():
#     saveClient()
#     copyDir()  # to all the drives


# def expireClient():
#     moveDir()
#     deleteDir()


# def deleteClient():
#     deleteDir()


# def expireClient():
#     moveDir()
#     deleteDir()


def getPath(user, client, driveIndex=None,):
    # user name client name and set of drives
    # tomove expire to home or vice versa
    # tocopy sync, update drives or save to drive
    # todelete update drives, delete client
    # tosave first time client
    tomove = None
    tocopy = []
    tosave = None
    todelete = []
    if not Client.objects.all().filter(user=user, name=client).exists():
        if driveIndex == None:
            raise Exception('can\'t save a client with no drives')
        else:
            tosave = os.path.join(homedir, user, client)
            tocopy = [os.path.join(homedir, user, client), [os.path.join(
                drives[i], user, client) for i in driveIndex]]
    else:
        if driveIndex == None:
            pass
        elif driveIndex == 'EXPIRE':
            if drivesof(user, client) == set([]):
                pass
            else:
                todelete = [os.path.join(drives[i], user, client)
                            for i in drivesof(user, client)]
                tomove = [os.path.join(homedir, user, client), os.path.join(
                    homedir, user, 'expire', client)]
        else:
            if drivesof(user, client) == set([]):
                tomove = [os.path.join(homedir, user, 'expire', client), os.path.join(
                    homedir, user, client)]
                tocopy = [os.path.join(homedir, user, client), [os.path.join(
                    drives[i], user, client) for i in driveIndex]]
            else:
                todelete = [os.path.join(drives[i], user, client)
                            for i in drivesof(user, client) - driveIndex]
                tocopy = [os.path.join(homedir, user, client), [os.path.join(
                    drives[i], user, client) for i in driveIndex - drivesof(user, client)]]
    return {'tocopy': tocopy, 'tomove': tomove, 'todelete': todelete, 'tosave': tosave}


def drivesof(user, client):
    # return set
    k = []
    query = Client.objects.get(user =user, name = client)
    if not query.thumbs =='EXPIRE':
        k = [int(n)-1 for n in query.thumbs]
    return set(k)


def syncdrive():
    deleteDir()
    copyDir()


# create client Done
# delete client
# update client
# expire client


def storeToThumbAndHome(cd, user, client):
    drivedatas = alldrivedata()
    drivefull = False
    fulllist = []
    for drive in [int(n)-1 for n in str(cd['thumbs'])]:
        if drivedatas[drive][2]<=drivelimit:
            drivefull = True
            fulllist.append(str(drive+1))
    if drivefull:
        return f'Sorry but drive No. {",".join(fulllist)} you opt for is full. Try to choose other drives or ask to get it replaced.'
    print('saving the client')
    # return None
    if Client.objects.filter(user=user,name=client).exists():
        return f"Client already exists try {suggest(user,client)}"
    if not os.path.exists(os.path.join(homedir,user,client)):
        os.makedirs(os.path.join(homedir,user,client))
    for imagename in ['image','image1','image2']:
        if cd[imagename] is not None:
            saveImage(cd[imagename],os.path.join(homedir,user,client))
    saveText(cd['textfile'],os.path.join(homedir,user,client))
    tocopy = []
    for thumbs in str(cd['thumbs']):
        tocopy.append(os.path.join(drives[int(thumbs)-1],user,client))
    copyDir(os.path.join(homedir,user,client),tocopy)
    obj = Client(user=user,name=client,thumbs = cd['thumbs'])
    obj.save()


def fileTypeof(filename):
    textset = {'txt','html'}
    imageset = {'png','jpg','jpeg'}
    domain = filename.split('.')[-1]
    if domain in textset:
        return 'text'
    if domain in imageset:
        return 'image'
    return 'NA'


def clientPathAndInfo(client):
    clientpath = ''
    textpath = ''
    imgpath = []
    if client.thumbs == 'EXPIRE':
        clientpath = os.path.join('expire', client.name)
    else:
        clientpath = client.name
    clientpath = os.path.join(homedir, client.user, clientpath)
    
    for j in os.listdir(clientpath):
        if fileTypeof(j) == 'text':
            textpath = os.path.join(clientpath, j)
        elif fileTypeof(j) == 'image':
            imgpath.append(os.path.join(clientpath, j))     
    return imgpath, client.name, client.thumbs, textpath


def getPathsAndInfo(user):
    # false if no client and
    # return list of imagePath, clientname, thumbs,textPath
    # get list of all the clients set path seeeing the drive is expired or not
    clients = Client.objects.filter(user=user)
    toret = [clientPathAndInfo(client) for client in clients]
    return toret


def deleteClient(user, client):
    thumbs = Client.objects.get(user=user, name=client).thumbs
    todel = []
    if thumbs == 'EXPIRE':
        todel.append(os.path.join(homedir, user, 'expire', client))
    else:
        todel.append(os.path.join(homedir, user, client))
        for drive in drivesof(user, client):
            todel.append(os.path.join(drives[drive], user, client))
    for entry in todel:
        deleteDir(entry)
    Client.objects.get(user=user, name=client).delete()


def expireClient(user, client):
    d = getPath(user, client, 'EXPIRE')
    for path in d['todelete']:
        deleteDir(path)
    moveDir(d['tomove'][0], d['tomove'][1])
    cl = Client.objects.get(user=user, name=client)
    cl.thumbs = 'EXPIRE'
    cl.save()


def deleteImage(path):
    os.remove(path)


def UpdateClient(cd, user, client):
    # if name is changed-> change name of all directories and update client
    if cd['name'] is not None and cd['name'] != '':
        thumbs = Client.objects.get(user=user, name=client).thumbs
        src = []
        dst = []
        if thumbs == 'EXPIRE':
            src.append(os.path.join(homedir, user, 'expire', client))
            dst.append(os.path.join(homedir, user, 'expire', cd['name']))
        else:
            src.append(os.path.join(homedir, user, client))
            dst.append(os.path.join(homedir, user, cd['name']))
            for drive in drivesof(user, client):
                src.append(os.path.join(drives[drive], user, client))
                dst.append(os.path.join(drives[drive], user, cd['name']))
        for entry in range(len(src)):
            os.rename(src[entry], dst[entry])
        myclient = Client.objects.get(user=user, name=client)
        myclient.name = cd['name']
        myclient.save()
        client = cd['name']
    oldclientpath = os.path.join(homedir, user, client)
    if Client.objects.get(user=user, name=client).thumbs == 'EXPIRE':
        oldclientpath = os.path.join(homedir, user, 'expire', client)
    for imageName in ['image', 'image1', 'image2']:
        if cd[imageName] is not None:
            saveImage(cd[imageName], oldclientpath)
    if cd['textfile'] != None:
        for item in os.listdir(oldclientpath):
            if fileTypeof(item) == 'text':
                os.remove(os.path.join(oldclientpath, item))
        saveText(cd['textfile'], oldclientpath)
    d = getPath(user, client, 'EXPIRE')
    for path in d['todelete']:
        deleteDir(path)
    drivechange = cd['thumbs']
    if drivechange == None or drivechange == '':

        copyDir(oldclientpath, d['todelete'])
    else:
        

        d = getPath(user, client, set([int(n)-1 for n in str(drivechange)]))
        copyDir(oldclientpath, d['tocopy'][1])
        if d['tomove'] is not None:
            moveDir(d['tomove'][0],d['tomove'][1])
        query = Client.objects.get(user=user,name=client)
        query.thumbs=drivechange
        query.save()


def sync(user, client, drive=None):
    query = Client.objects.get(user= user, name=client)
    if drive is None:
        for drive in drivesof(user,client):
            if os.path.exists(os.path.join(drives[drive],user,client)):
                shutil.rmtree(os.path.join(drives[drive],user,client))
        if query.thumbs != 'EXPIRE':
            d = getPath(user,client,'EXPIRE')
            copyDir(os.path.join(homedir,user,client),d['todelete'])
    else:
        if drive in  drivesof(user,client):
            shutil.rmtree(os.path.join(drives[drive],user,client))
            copyDir(os.path.join(homedir,user,client),[os.path.join(drives[drive],user,client)])
        else:
            raise Exception('not valid drive for this user and client')
    return None
