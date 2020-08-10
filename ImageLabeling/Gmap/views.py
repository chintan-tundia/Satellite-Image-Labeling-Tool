#from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.files import File
from Gmap.models import Image
from Gmap.models import GMapMarker
from Gmap.models import Annotation

from django.db import models
import cv2
import os
import base64
import datetime
import json
import base64
import pandas as pd 
import math
import imutils
import numpy as np

def index(request):    
    template = loader.get_template('Gmap/index.html')    
    allMarkers = GMapMarker.objects.all()
    context = {  
        'allMarkers':allMarkers,        
    }    
    return HttpResponse(template.render(context, request))

def displayImages(request):
    template = loader.get_template('Gmap/displayImages.html')    
    # imgs = Image.objects.filter(is_annotated=False)
    imgs = Image.objects.all().extra(order_by = ['image_name']);
    # imgs = Image.objects.all().extra(order_by = ['-captured_date']);
    # imgs = imgs.extra(order_by = ['image_name']);
    # img_sample = imgs.get(image_name="Ahmednagar_Wet_2.jpg")    
    # print(img_sample)
    # annotations=Annotation.objects.all()
    # annotations_sample=annotations.filter(source_image=img_sample)
    
    context = {        
        'images':imgs,        
    }
    return HttpResponse(template.render(context, request))
def get_annotations(request):
    data = {} 
    if request.method == 'POST':
        imageName = request.POST.get('image_name') 
        try:        
            currImg = Image.objects.get(image_name=imageName)
            print(currImg)
            annots=Annotation.objects.filter(source_image=currImg)
            # annots_json=json.dumps(annots);
            listArr=[]
            for annots_i in annots:
                list1={}
                list1['top_left_x']=str(annots_i.top_left_x);
                list1['top_left_y']=str(annots_i.top_left_y);
                list1['width']=str(abs(annots_i.top_left_x-annots_i.bottom_right_x));
                list1['height']=str(abs(annots_i.top_left_y-annots_i.bottom_right_y));
                list1['class_label']=annots_i.class_label;
                listArr.append(list1)
            annots_json=json.dumps(listArr);                    
            data={
                'annotations':annots_json
            }        
            return JsonResponse(data)
        except Image.DoesNotExist:    
            data={
                'annotations':-1
            }
    return JsonResponse(data)

def label_image(request):  
    template = loader.get_template('Gmap/tool/index.html')    
    image_name=request.POST.get('imageName');
    encoded_string=request.POST.get('canvasImg64')
    # with open("static/Gmap/images/"+image_name, "rb") as image_file:
    #     encoded_string = base64.b64encode(image_file.read())    
    # encoded_string = 'data:image/png;base64,{}'.format(encoded_string)
    context = {  
        'image_name':image_name,
        'encoded_string':encoded_string
    }
    return HttpResponse(template.render(context, request))

def show_all_markers(request):  
    template = loader.get_template('Gmap/showAllMarkers.html')
    allMarkers = GMapMarker.objects.all()
    context = {  
        'allMarkers':allMarkers,        
    }
    return HttpResponse(template.render(context, request))    

def save_image(request):
    data = {}    
    if request.method == 'POST':
        imagesrc = request.POST.get('imagesrc')    
        filename = request.POST.get('filename')
        filename = filename+'.jpg'
        markers_json = request.POST.get('markers') 

        # data  = json.loads(markers_json)   
        image_parts=imagesrc.split(';base64,')
        image_base64 = base64.b64decode(image_parts[1]);    
        location = 'static/Gmap/images/'+filename;
        img=Image.objects.filter(image_name=filename)
        if img.count() > 0:            
            data ={
                'status':-1
            }
            return JsonResponse(data)

        with open(location, 'wb') as f:
            myfile = File(f)
            myfile.write(image_base64)
            myfile.closed
            f.closed

            
        # img = cv2.imread(location)
        # x=0;y=0;h=640;w=640;
        # crop_img = img[y:y+h, x:x+w]
        # cv2.imwrite(location,crop_img);
        imgHeight=640;
        imgWidth=640;        
        saveImg = Image(image_name=filename,image_location=location,image_height=imgHeight,image_width=imgWidth) 
        saveImg.save() 
        markers_data  = json.loads(markers_json)    
        for i in markers_data:
            latitude=None
            longitude=None
            count=1
            for key, value in i.items():
                if(key=='lat'):
                    latitude = value            
                if(key=='lng'):
                    longitude = value
        
            try:
                checked = GMapMarker.objects.get(latitude=latitude, longitude=longitude)
            except GMapMarker.DoesNotExist:
                saveMarker = GMapMarker(latitude=latitude,longitude=longitude,source_image=saveImg)        
                saveMarker.save()
        data = {
            'status': 1
        }
        return JsonResponse(data)
    return JsonResponse(data)

def save_markers(request):    
    markers_json = request.POST.get('markers') 
    markers_data  = json.loads(markers_json)    
    for i in markers_data:
        latitude=None
        longitude=None
        count=1
        for key, value in i.items():
            if(key=='lat'):
                latitude = value            
            if(key=='lng'):
                longitude = value
        
        try:
            obj = GMapMarker.objects.get(latitude=latitude, longitude=longitude)
        except GMapMarker.DoesNotExist:
            obj = GMapMarker(latitude=latitude,longitude=longitude)        
            obj.save()               

    

    data = {
            'status': 1
    }
    return JsonResponse(data)


def load_images_into_db(request):    
    template = loader.get_template('Gmap/testCanvas.html');
    directory="static/Gmap/images/";    
    imgHeight=640;
    imgWidth=640;

    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            loc=directory+filename
            obj = Image(image_name=filename,image_location=loc,image_height=imgHeight,image_width=imgWidth) 
            obj.save()                  
    
   
    
    # allMarkers = GMapMarker.objects.all()
    context = {  
    
    }    
    return HttpResponse(template.render(context, request))   

def load_markers_from_csv(request):    
    template = loader.get_template('Gmap/showAllMarkers.html');
    records = pd.read_csv("static/Gmap/geolocatedFPs.csv");
    for index, row in records.iterrows():
        obj = GMapMarker(latitude=row['latitude'],longitude=row['longitude'],marked_date=row['marked_date']) 
        obj.save()        
   
    
    allMarkers = GMapMarker.objects.all()
    context = {  
        'allMarkers':allMarkers,        
    }
    
    return HttpResponse(template.render(context, request))   

def save_annotations(request):
    bbox_json = request.POST.get('bbox_json')
    imgName= request.POST.get('image_name')
    json_data  = json.loads(bbox_json) 
        
    try:
        sourceImg = Image.objects.get(image_name=imgName) 
        wfp="Wet Farm Pond";
        dfp="Dry Farm Pond";
        wetFP={};
        dryFP={};
        if( wfp in json_data):
            wetFP=json_data[wfp]
            

        if( dfp in json_data):
            dryFP=json_data[dfp]
           
        saved=False
        for bounds in wetFP:
            tlx=bounds["top_left_x"];
            tly=bounds["top_left_y"];
            blx=bounds["bottom_right_x"];
            bly=bounds["bottom_right_y"];
            classnm="Wet Farm Pond"
            ann=Annotation(source_image=sourceImg,top_left_x=tlx,top_left_y=tly,bottom_right_x=blx,bottom_right_y=bly,class_label=classnm)                        
            ann.save()
            saved=True
            

        for bounds in dryFP:
            tlx=bounds["top_left_x"];
            tly=bounds["top_left_y"];
            blx=bounds["bottom_right_x"];
            bly=bounds["bottom_right_y"];
            classnm="Dry Farm Pond"
            ann=Annotation(source_image=sourceImg,top_left_x=tlx,top_left_y=tly,bottom_right_x=blx,bottom_right_y=bly,class_label=classnm)
            ann.save()   
            saved=True

        if(saved==True):
            sourceImg.is_annotated=True;
            sourceImg.save()



    except Image.DoesNotExist:
        data = {
            'status': -1
        }               
        return JsonResponse(data)
    data = {
        'status': 1
    }    
    return JsonResponse(data)

def downloadNegatives(request):
    template = loader.get_template('Gmap/testCode.html');
    context = {}    
    return HttpResponse(template.render(context, request))  

def extractFPs(request):
        template = loader.get_template('Gmap/testCode.html');
        imgs = Image.objects.filter(is_annotated=True).extra(order_by = ['image_name']);        
        # imgs = Image.objects.filter(image_name='Ahmednagar_Wet_20.jpg').extra(order_by = ['image_name']);        

        # img_sample = imgs.get(image_name="Ahmednagar_Wet_2.jpg")    
        # print(img_sample)
        annotations=Annotation.objects.all()
        # maxHeight=0        
        # maxWidth=0
        minHeight=640
        minWidth=640
        totalAnnots=0
        sigma_area=0  
        sigma_diagonal=0;   
        for eachimg in imgs:
            baseFileName=eachimg.image_name;                        
            eachimgAnnotations=annotations.filter(source_image=eachimg)
            sourceLocation=eachimg.image_location
            img = cv2.imread(sourceLocation)
            
            i=1;
            wet_i=1;
            dry_i=1;
            # size=294;
            # size=24;
            size=145
            imSize=640;
            for annot in eachimgAnnotations:
                totalAnnots=totalAnnots+1;
                classnm=annot.class_label
                if(classnm=='Wet Farm Pond'):
                    filename=baseFileName[:-4]+'_'+str(wet_i)+baseFileName[-4:];
                    wet_i=wet_i+1;     
                    base='static/Gmap/extractions/Size'+str(size)+'x'+str(size)+'/WetFP/'; 
                    if not os.path.exists(base):
                        os.makedirs(base)             
                    destLocation = base+filename;
                if(classnm=='Dry Farm Pond'):                        
                    filename=baseFileName[:-4]+'_'+str(dry_i)+baseFileName[-4:];
                    dry_i=dry_i+1;
                    base='static/Gmap/extractions/Size'+str(size)+'x'+str(size)+'/DryFP/';
                    if not os.path.exists(base):
                        os.makedirs(base)
                    destLocation = base+filename;

                # destLocation = 'static/Gmap/extractions/Size294x294/'+filename;
                # destLocation = 'static/Gmap/extractions/Size24x24/'+filename;                
                
                
                

                x1=int(annot.top_left_x);                
                y1=int(annot.top_left_y);                                
                x2=int(annot.bottom_right_x);                
                y2=int(annot.bottom_right_y);                
                
                x_center=x1+int(abs(x1-x2)/2)
                y_center=y1+int(abs(y1-y2)/2)
                x_newtl=abs(x_center-int(size/2))
                y_newtl=abs(y_center-int(size/2))                
                
                # h=int(abs(y2-y1))
                # w=int(abs(x2-x1))
                # crop_img = img[y1:y1+h, x1:x1+w]
                #####OR####
                h=min(y_newtl+size,imSize)
                w=min(x_newtl+size,imSize)
                crop_img = img[y_newtl:h, x_newtl:w]
                height, width, channels = crop_img.shape
                

                diagonal_size=math.sqrt((h*h)+(w*w))
                sigma_diagonal=sigma_diagonal+diagonal_size
                # tarea=h*w;
                # sigma_area=sigma_area+tarea;
                # if(h<minHeight):                    
                #     minHeight=h;
                # if(w<minWidth):
                #     minWidth=w;                    
                if(height==size and width==size ):
                    j=0
                    for angle in np.arange(0, 360, 90):
                        rotated = imutils.rotate(crop_img, angle)
                        filename=destLocation[:-4]+'_'+str(j)+destLocation[-4:];                        
                        cv2.imwrite(filename,rotated); 
                        j=j+1;

                    # cv2.imwrite(destLocation,crop_img); 
                i=i+1;               
        
        # print("Max Width:"+str(maxWidth));
        # print("Max Height:"+str(maxHeight));
        # print("Min Width:"+str(minWidth));
        # # print("Min Height:"+str(minHeight));
        # print("Avg Area:"+str(sigma_area/totalAnnots));
        # print("Avg Height:"+str(math.sqrt(sigma_area)));
        # print("Avg Width:"+str(math.sqrt(sigma_area)));
        print("totalAnnots:"+str(totalAnnots))
        print("Avg Diagonal Size:"+str(sigma_diagonal/totalAnnots));
        context = {}    
        return HttpResponse(template.render(context, request))   

######Code snippet dumps##########
# temp='static/Gmap/images';
#             if(sourceLocation[18]!='/'):
#                 temp1=sourceLocation[0:18]+'/'+sourceLocation[18:]
#                 eachimg.image_location=temp1
#                 eachimg.save()
