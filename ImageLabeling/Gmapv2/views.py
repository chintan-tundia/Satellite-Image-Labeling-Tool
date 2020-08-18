#from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.files import File
from django.core import serializers
from Gmapv2.models import Image
from Gmapv2.models import GMapMarker
from Gmapv2.models import Annotation
from Gmapv2.models import WorkType
from Gmapv2.models import DeptName
from Gmapv2.models import DistrictName
from Gmapv2.models import JSMappedWorks
from Gmapv2.models import JSMappedWorksImage

from django.db import models
from django.db.models import Q
from django.db.models import Count
from django.db import connection
import sys
import cv2
import os
import base64
import datetime
from datetime import datetime as dttm
import json
import base64
import pandas as pd 
import math
import imutils
import numpy as np
import shutil
import requests
from pathlib import Path
import glob
import zipfile
import enum 

from django.contrib.gis.gdal import OGRGeometry
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point

class FarmPondLabel(enum.Enum):     
    WetFPLined = 0 #cyan
    WetFPUnlined = 1 #green
    DryFPLined = 2 #red
    DryFPUnlined = 3 #yellow

    

WORKTYPE_MARATHI = ["अनघड दगडी बांध" ,"ओढा/ नाले / कॅनॉल जोड प्रकल्प" ,"कंपार्टमेन्ट बंडीग" ,"कालवा दुरुस्त करणे" ,\
    "कोल्हापूर टाईप बंधारा/साठवण बंधारा दुरुस्ती" ,"खोल सलग समतल चर" ,"गाळ काढणे (गाव तलाव)" ,"गाळ काढणे (पाझर तलाव)" ,\
    "गाळ काढणे (माजी मालगुजारी तलाव)" ,"गाळ काढणे (शिवकालीन तलाव)" ,"गाळ काढणे (सिमेंट बंधारा/माती नाला बांध)" ,"गुरे प्रतिबंधक चर",\
    "गॅबियन बंधारे" ,"ग्रेडेड बंडींग" ,"जुने सिमेंट काँक्रिट नाला बांध"  ,"जुन्या जलस्त्रोतांची दुरुस्ती ( माती नाला बांध / स" ,\
    "झरा बळकटीकरण करणे" ,"ट्रेंच गॅलरी करणे" ,"ठिबक सिंचन" ,"तुषार सिंचन" ,"दगडी ताल बांधणे" ,"नाला खोलीकरण" ,\
    "नैसर्गिक जलस्त्रोत बळकटीकरण" ,"नैसर्गिक पाण्याच्या स्त्रोत्रांचे झ-यांचे सभोवती" ,"पाझर तलाव दुरुस्ती (COT/सांडवा/इतर दुरुस्ती)",\
    "पुर्नभरण चर" ,"बोडी दुरुस्ती" ,"भातखचरे पुर्नजीवन" ,"मजगी" ,"माजी मालगुजारी तलाव दुरुस्ती" ,"माती नाला बांध" ,"रिचार्ज शाफ्ट",\
    "लहान मातीचा बांध" ,"वनतळी" ,"वनीकरण/वृक्ष लागवड" ,"वन्यप्राणी प्रतिबंधक चर" ,"वळण बंधारा"  ,"विंधन विहीर पुनर्भरण करणे" ,\
    "विहीर पुर्नभरण करणे" ,"शेततळे"  ,"सलग समतल चर" ,"सिमेंट काँक्रीट नाला बांध" ,"हायड्रो फ्रॅक्चरींग","NA" ]

WORKTYPE_ENGLISH = ["Loose Boulder Structure","Stream / Canal / Canal Joints Project",\
"Compartment bunding","Canal Repair","KT Weir / Storage Bandhara Repair","Deep CCT",\
"Nala Desiliting (village tank)","Nala Desiliting (percolation tank)",\
"Nala Desiliting (Former Malugari tank)","Nala Desiliting (Shiva Winter tank)",\
"Nala Desiliting (Cement bandhara / Earthern Nala Bandh)","TCM","Gabion bandhara",\
"Graded bunding","Old CNB","Repair of old water bodies (Earthern Nala Bund / )","Stream Strengthening",\
"Trench Gallery","Drip irrigation","Sprinkler irrigation","Rock bunding","Nala Deepening",\
"Strengthening Natural Water Resources","Stream Surrounding Natural Water Sources",\
"PT Repairing (COT / Sandwa / Other Repairs)","Refill variable","Body Repair (unclear translation)" ,\
"Rice Field Rejuvination","Majagi","Former Malgujari Talav Repair (unclear translation)",\
"Earthern Nala Bund","Recharge shaft","Small earthen Bund","Forest pond","Afforestation / Plantation",\
"TCM 2 / Wildlife protection char (unclear translation)","Turning bandhara","Vindhan Well rehabilitation",\
"Well rehabilitation","Farm Pond","CCT","Cement Concrete Nala Bandh","Hydro Fracturing","NA"]    

DEPTNAME_MARATHI = ["कृषि","वन","लघु सिंचन (जलसंधारण)","लघु सिंचन जिल्हा परिषद","जलसंपदा",\
"पाणी पुरवठा व स्वच्छता विभाग जिल्हा परीषद","भुजल सर्वेक्षण व विकास यंत्रणा","ग्रामपंचायत विभाग",\
"सामाजिक वनीकरण","जलसंपदा (यांत्रिकी)","जलसंपदा (लघु पाटबंधारे विभाग)","कृषि (जिल्हा परिषद)","पंचायत समिती","महसूल","वन्यजीव"];

DISTRICTNAME_MARATHI=["अकोला","अमरावती","अहमदनगर","उस्मानाबाद","औरंगाबाद","कोल्हापूर","गडचिरोली","गोंदिया","चंद्रपूर",\
"जळगाव","जालना","ठाणे","धुळे","नंदुरबार","नांदेड","नागपूर","नाशिक","परभणी","पालघर","पुणे","बीड","बुलडाणा","भंडारा","यवतमाळ",\
"रत्नागिरी","रायगड","लातूर","वर्धा","वाशिम","सांगली","सातारा","सिंधुदुर्ग","सोलापूर","हिंगोली","मुंबई","मुंबई उपनगर"]

DISTRICTNAME_ENGLISH=["Akola","Amravati","Ahmednagar","Usmanabad","Aurangabad","Kolhapur","Gadchiroli",\
"Gondiya","Chandarpur","Jalgaon","Jalna","Thane","Dhule","Nandurbar","Nanded","Nagpur","Nashik",\
"Parbhani","Palghar","Pune","Beed","Buldhana","Bhandara","Yavatmal","Ratnagiri","Raigadh","Latur",\
"Wardha","Vashim","Sangli","Satara","Sindhudurg","Solapur","Hingoli","Mumbai","Mumbai Suburb"]


def index(request):    
    template = loader.get_template('Gmapv2/index.html')    
    allMarkers = GMapMarker.objects.all()
    context = {  
        'allMarkers':allMarkers,        
    }    
    return HttpResponse(template.render(context, request))
def labelWells(request):
    template = loader.get_template('Gmapv2/labelWells.html')    
    # allMarkers = GMapMarker.objects.all()
    DISTRICTNAME_ENGLISH.sort()
    context = {  
        'districtNames':DISTRICTNAME_ENGLISH
        #'allMarkers':allMarkers,        
    }    
    return HttpResponse(template.render(context, request)) 
	
def labelFarmPonds(request):
    template = loader.get_template('Gmapv2/labelFarmPonds.html')  
    print(template)  
    # allMarkers = GMapMarker.objects.all()
    DISTRICTNAME_ENGLISH.sort()
    context = {  
        'districtNames':DISTRICTNAME_ENGLISH
        #'allMarkers':allMarkers,        
    }    
    return HttpResponse(template.render(context, request))

def labelCheckDams(request):
    template = loader.get_template('Gmapv2/labelCheckDams.html')  
    print(template)  
    # allMarkers = GMapMarker.objects.all()
    DISTRICTNAME_ENGLISH.sort()
    context = {  
        'districtNames':DISTRICTNAME_ENGLISH
        #'allMarkers':allMarkers,        
    }    
    return HttpResponse(template.render(context, request))

	
def checkArea(request):    
    template = loader.get_template('Gmapv2/checkArea.html')        
    context = {          
    }    
    return HttpResponse(template.render(context, request))
def checkFPat19(request):
    template = loader.get_template('Gmapv2/checkFPat19.html')      
    allJSON=[];    
    objs= GMapMarker.objects.raw('SELECT "Gmapv2_gmapmarker".id, "Gmapv2_gmapmarker".locality, "Gmapv2_gmapmarker".source_image_id FROM \
                                 "Gmapv2_gmapmarker" JOIN (SELECT Orig.id FROM "Gmapv2_image" as Orig WHERE Orig.id NOT IN \
                                 (SELECT I1.id FROM "Gmapv2_image" as I1 JOIN "Gmapv2_image" as I2\
                                  ON I1.id=I2.derived_from_image_id)) as Res ON Res.id="Gmapv2_gmapmarker".source_image_id')
    # for obj in objs:
    #     print(obj.id)
    objs=GMapMarker.objects.filter(Q(source_image__annotation__class_label="Wet Farm Pond - Lined")|\
                                   Q(source_image__annotation__class_label="Wet Farm Pond - Unlined")|\
                                   Q(source_image__annotation__class_label="Dry Farm Pond - Lined")|\
                                   Q(source_image__annotation__class_label="Dry Farm Pond - Unlined"),\
                                   source_image__derived_from_image__derived_from_image=None)\
                                   .annotate(total=Count('source_image')).values_list('id','locality','source_image')\
                                   .filter(total=1).order_by("id")


    print("{} : {}".format("Count",str(objs.count())))
    for obj in objs:
        #allJSON.append(obj.geometryJSON)    
        allJSON.append(obj)    
    allMarkers={}
    allMarkers['allJSON']=allJSON
    #allMarkers=json.dumps(allMarkers)
    #print(allJSON)
    context = {  
        #'allMarkers':allMarkers,        
        'allMarkers':allJSON,        
    }    
    return HttpResponse(template.render(context, request))



def getMarkerFromId(request):
    data = {
                'status': -1
    }
    if request.method == 'POST':
        markerId = request.POST.get('marker_id')
        
        marker=GMapMarker.objects.get(pk=markerId)
        
        data = {
                'status': 1,
                'geometryJSON':marker.geometryJSON
        }
        return JsonResponse(data)

    return JsonResponse(data)    

   
def getImageList(request):
    if request.method == 'POST':
        try:
            wfpl = request.POST.get('wfpl')
            wfpu = request.POST.get('wfpu')
            dfpl = request.POST.get('dfpl')
            dfpu = request.POST.get('dfpu')
            neg = request.POST.get('neg')
            zl18 = request.POST.get('zl18')
            zl19 = request.POST.get('zl19')
            print(neg)
            wfplc = 0;
            wfpuc = 0;
            dfplc = 0;
            dfpuc = 0;
            negc = 0;  
            results=Image.objects.none()
            print("Zl18"+str(zl18))

            if(zl18=='1'):
                if(wfpl=='1'):
                    wfplr=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined"),zoom_level=18)
                    results=results|wfplr
                    wfplc=wfplr.count()
                    print("YASS")
                if(wfpu=='1'):
                    wfpur=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Unlined"),zoom_level=18)
                    results=results|wfpur
                    wfpuc=wfpur.count()
                if(dfpl=='1'):
                    dfplr=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Lined"),zoom_level=18)
                    results=results|dfplr
                    dfplc=dfplr.count()
                if(dfpu=='1'):
                    dfpur=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Unlined"),zoom_level=18)
                    results=results|dfpur
                    dfpuc=dfpur.count()
                if(neg=='1'):
                    negr=Image.objects.filter(is_annotated=False,zoom_level=18)
                    results=results|negr
                    negc=negr.count()

            if(zl19=='1'):
                if(wfpl=='1'):
                    wfplr=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined"),zoom_level=19)
                    results=results|wfplr
                    wfplc=wfplr.count()
                if(wfpu=='1'):
                    wfpur=Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Unlined"),zoom_level=19)
                    results=results|wfpur
                    wfpuc=wfpur.count()
                if(dfpl=='1'):
                    dfplr=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Lined"),zoom_level=19)
                    results=results|dfplr
                    dfplc=dfplr.count()
                if(dfpu=='1'):
                    dfpur=Image.objects.filter(Q(annotation__class_label="Dry Farm Pond - Unlined"),zoom_level=19)
                    results=results|dfpur
                    dfpuc=dfpur.count()
                if(neg=='1'):
                    negr=Image.objects.filter(is_annotated=False,zoom_level=19)
                    results=results|negr
                    negc=negr.count()

            #print(type(results))
            results=results.distinct().order_by('image_name')

            totalImages = results.count(); 
            print(totalImages)                       
            images_list = serializers.serialize('json', results,\
                                                fields=('image_name','is_annotated','is_approved','image_location'))            

            data={
                'status':1,
                'images':images_list,
                'wfpl':wfplc,
                'wfpu':wfpuc,
                'dfpl':dfplc,
                'dfpu':dfpuc,
                'negImgs':negc,
                'totalImages':totalImages
            }             
        except Exception as e:
            print(str(e))
            data={
                'status':-1
            }

    return JsonResponse(data)
def displayImagesCD(request):
    template = loader.get_template('Gmapv2/displayWells.html')    
    # imgs = Image.objects.filter(is_annotated=False)
    imgs = Image.objects.filter(annotation__class_label="Checkdam").distinct().extra(order_by = ['image_name']);
    wells=Annotation.objects.filter(class_label="Checkdam").count();    
    totalImages=imgs.count();
    # imgs = Image.objects.all().extra(order_by = ['-captured_date']);
    # imgs = imgs.extra(order_by = ['image_name']);
    # img_sample = imgs.get(image_name="Ahmednagar_Wet_2.jpg")    
    # print(img_sample)
    # annotations=Annotation.objects.all()
    # annotations_sample=annotations.filter(source_image=img_sample)
    
    context = {        
        'images':imgs,
        'wells':wells,
        'totalImages':totalImages
    }
    return HttpResponse(template.render(context, request)) 
	
def displayImagesFP(request):
    template = loader.get_template('Gmapv2/displayFarmPonds.html')    
    # imgs = Image.objects.filter(is_annotated=False)
    imgs = Image.objects.filter(Q(is_annotated=False)|Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"))\
                                .distinct().extra(order_by = ['image_name']);
    wfpl18=Annotation.objects.filter(class_label="Wet Farm Pond - Lined",source_image__zoom_level=18).count();
    wfpu18=Annotation.objects.filter(class_label="Wet Farm Pond - Unlined",source_image__zoom_level=18).count();
    dfpl18=Annotation.objects.filter(class_label="Dry Farm Pond - Lined",source_image__zoom_level=18).count();
    dfpu18=Annotation.objects.filter(class_label="Dry Farm Pond - Unlined",source_image__zoom_level=18).count();
    negImgs18 = Image.objects.filter(is_annotated=False,zoom_level=18).count() 
    wfpl19=Annotation.objects.filter(class_label="Wet Farm Pond - Lined",source_image__zoom_level=19).count();
    wfpu19=Annotation.objects.filter(class_label="Wet Farm Pond - Unlined",source_image__zoom_level=19).count();
    dfpl19=Annotation.objects.filter(class_label="Dry Farm Pond - Lined",source_image__zoom_level=19).count();
    dfpu19=Annotation.objects.filter(class_label="Dry Farm Pond - Unlined",source_image__zoom_level=19).count();
    negImgs19 = Image.objects.filter(is_annotated=False,zoom_level=19).count()
    totalImages=imgs.count();
    # imgs = Image.objects.all().extra(order_by = ['-captured_date']);
    # imgs = imgs.extra(order_by = ['image_name']);
    # img_sample = imgs.get(image_name="Ahmednagar_Wet_2.jpg")    
    # print(img_sample)
    # annotations=Annotation.objects.all()
    # annotations_sample=annotations.filter(source_image=img_sample)
    wfpl=str(wfpl18)+", "+str(wfpl19)
    wfpu=str(wfpu18)+", "+str(wfpu19)
    dfpl=str(dfpl18)+", "+str(dfpl19)
    dfpu=str(dfpu18)+", "+str(dfpu19)
    negImgs=str(negImgs18)+", "+str(negImgs19)
    context = {        
        'images':imgs,
        'wfpl':wfpl,
        'wfpu':wfpu,
        'dfpl':dfpl,
        'dfpu':dfpu,
        'negImgs':negImgs,
        'totalImages':totalImages
    }
    return HttpResponse(template.render(context, request))

def displayImagesWells(request):
    template = loader.get_template('Gmapv2/displayWells.html')    
    # imgs = Image.objects.filter(is_annotated=False)
    imgs = Image.objects.filter(annotation__class_label="Well").distinct().extra(order_by = ['image_name']);
    wells=Annotation.objects.filter(class_label="Well").count();    
    totalImages=imgs.count();
    # imgs = Image.objects.all().extra(order_by = ['-captured_date']);
    # imgs = imgs.extra(order_by = ['image_name']);
    # img_sample = imgs.get(image_name="Ahmednagar_Wet_2.jpg")    
    # print(img_sample)
    # annotations=Annotation.objects.all()
    # annotations_sample=annotations.filter(source_image=img_sample)
    
    context = {        
        'images':imgs,
        'wells':wells,
        'totalImages':totalImages
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
                list1['geometryJSON']=annots_i.geometryJSON;               
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

def get_jsmappedwork_district_wise(request):
    data = {};
    jsmappedworks_list ={};
    if request.method == 'POST':
        districtName = request.POST.get('districtName')
        worktype = request.POST.get('workType')
        dataOfYear=request.POST.get('dataOfYear')         
        try:
            if(worktype=="wells"):
                print("Wells")
                print(dataOfYear)
                print(districtName)
                jsmappedworks=JSMappedWorks.objects.filter(Q(dataOfYear=dataOfYear),\
                          Q(district__english_name=districtName),\
                          Q(work_type__english_name='Well rehabilitation')|\
                          Q(work_type__english_name='Vindhan Well rehabilitation')|\
                          Q(work_type__english_name='Well Deepening')|\
                          Q(work_type__english_name='Irrigation Well')|\
                          Q(work_type__english_name='KT Well Desilting'))
                print(jsmappedworks.count())
                total_img_district=Annotation.objects.filter(class_label='Well',\
                                source_image__gmapmarker__district=districtName).\
                                values('source_image').distinct().count()
								
            if(worktype=="checkdams"):
                print("Checkdams")
                print(dataOfYear)
                print(districtName)
                jsmappedworks=JSMappedWorks.objects.filter(Q(dataOfYear=dataOfYear),\
                          Q(district__english_name=districtName),\
                          Q(work_type__english_name='Cement Concrete Nala Bandh'))
                print("Total Checkdams: ", jsmappedworks.count())
                total_img_district=Annotation.objects.filter(class_label='Checkdam',\
                                source_image__gmapmarker__district=districtName).\
                                values('source_image').distinct().count()

            if(worktype=="farmponds"):
                print("Farm Ponds")
                jsmappedworks=JSMappedWorks.objects.filter(dataOfYear=dataOfYear,\
                          district__english_name=districtName,\
                          work_type__english_name='Farm Pond')

                print(jsmappedworks.count())
                total_img_district=Annotation.objects.filter(Q(class_label="Wet Farm Pond - Lined")|\
                                Q(class_label="Wet Farm Pond - Unlined")|\
                                Q(class_label="Dry Farm Pond - Lined")|\
                                Q(class_label="Dry Farm Pond - Unlined"),\
                                Q(source_image__gmapmarker__district=districtName)).\
                                values('source_image').distinct().count()
               
                

            total_count=jsmappedworks.count()
            jsmapped_done=jsmappedworks.filter(is_marked=True);
            jsmapped_not_done=jsmappedworks.filter(is_marked=False); 
            total_done_count=jsmapped_done.count()
            percentage=0
            if(total_count>0):
                percentage=(total_done_count/total_count) * 100;
            jsmappedworks_list = serializers.serialize('json', jsmapped_not_done,\
                                                fields=('latitude','longitude'))            

            data={
                'status':1,
                'total_samples':total_count,
                'total_done_samples':total_done_count,
                'total_img_district':total_img_district,
                'done_percentage':percentage,
                'records':jsmappedworks_list
            }      
        except Exception as e:
            print(str(e))
            data={
                'status':-1
            }

    return JsonResponse(data)    

def label_image(request):  
    template = loader.get_template('Gmapv2/tool/index.html')    
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

def show_all_markers_cd(request):  
	template = loader.get_template('Gmapv2/showAllMarkers.html')
	allJSON=[];
	objs = GMapMarker.objects.filter(Q(source_image__annotation__class_label="Checkdam"))
	for obj in objs:
	 allJSON.append(obj.geometryJSON)    
	allMarkers={}
	allMarkers['allJSON']=allJSON
	allMarkers=json.dumps(allMarkers)
	#print(allMarkers)
	context = {  
		'allMarkers':allMarkers,        
	}
	return HttpResponse(template.render(context, request))
	

def show_all_markers_fp(request):  
    template = loader.get_template('Gmapv2/showAllMarkers.html')
    allJSON=[];

    objs=GMapMarker.objects.filter(Q(source_image__annotation__class_label="Wet Farm Pond - Lined")|\
                                   Q(source_image__annotation__class_label="Wet Farm Pond - Unlined")|\
                                   Q(source_image__annotation__class_label="Dry Farm Pond - Lined")|\
                                   Q(source_image__annotation__class_label="Dry Farm Pond - Unlined"))
    for obj in objs:
        allJSON.append(obj.geometryJSON)    
    allMarkers={}
    allMarkers['allJSON']=allJSON
    allMarkers=json.dumps(allMarkers)
    #print(allMarkers)
    context = {  
        'allMarkers':allMarkers,        
    }
    return HttpResponse(template.render(context, request))

def show_all_markers_wells(request):  
    template = loader.get_template('Gmapv2/showAllMarkersWells.html')
    allJSON=[];

    objs=GMapMarker.objects.filter(source_image__annotation__class_label="Well")
    for obj in objs:
        allJSON.append(obj.geometryJSON)    
    allMarkers={}
    allMarkers['allJSON']=allJSON
    allMarkers=json.dumps(allMarkers)
    print(allMarkers)
    context = {  
        'allMarkers':allMarkers,        
    }
    return HttpResponse(template.render(context, request))


def downloadImage(imgUrl,filepath): #taken from Debanjan's code
    response = requests.get(imgUrl, stream=True)    
    with open(filepath, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def save_image_fps(request):
    data = {}
    if request.method == 'POST':        
        topLeftLat = request.POST.get('topLeftLat')
        topLeftLng = request.POST.get('topLeftLng')
        bottomRightLat = request.POST.get('bottomRightLat')
        bottomRightLng = request.POST.get('bottomRightLng')
        centerLat = request.POST.get('centerLat') 
        centerLng = request.POST.get('centerLng')        
        district  = request.POST.get('district')
        locality = request.POST.get('locality')             
        markersJson = request.POST.get('markersJSON')
        annotationsJson = request.POST.get('annotationJSON')
        ground_truthing_done = request.POST.get('groundTruthingDone')
        gmapMarkerId=request.POST.get('gmapMarkerId')
        derivedFromImageId = request.POST.get('derivedFromImageId')
        zoom =int(float(request.POST.get('zoom')))        
        zoom = str(zoom)  
        if(gmapMarkerId!=None):
            gmm=GMapMarker.objects.get(pk=gmapMarkerId)
            district=gmm.district

        filename=str(district)+"_"+str(locality)+"_"+str(centerLat)+"_"+str(centerLng);        
        # data  = json.loads(markers_json)           
        is_annotated_flag=False
        markers  = json.loads(markersJson)
        annotations  = json.loads(annotationsJson)          
        if(len(annotations)>0):
            is_annotated_flag=True
        location='static/Gmapv2/images/';    
        if(is_annotated_flag):
            location = 'static/Gmapv2/images/FarmPonds/';
            if(zoom=="19"):
                location = 'static/Gmapv2/images/FarmPonds/zoom19/';
        else:
            location = 'static/Gmapv2/images/FarmPonds/';    

        key = 'AIzaSyDQrhuv_BxZGPpB1WGF-dLTKbumKYchpvo';
        maptype = 'satellite';
        size = '640x640';
        url_center = centerLat+","+centerLng
        imgUrl = "https://maps.googleapis.com/maps/api/staticmap?center="+url_center + '&size=' + size + '&zoom=' + zoom + '&maptype=' + maptype + '&key='+key        
        newFileName=filename+"_z"+zoom+"_0.png";
        filepath=location+newFileName;        
        lastpos=len(filepath)-filepath.rfind('_')
        filepathpattern=filepath[:-lastpos]
        my_file = Path(filepath)
        if my_file.exists():
             files=glob.glob(filepathpattern+"*")
             total=len(files)            
             newFileName=filename+"_"+str(total)+".png"
             filepath=location+newFileName;            
        #print(filepath)
        if(derivedFromImageId!=None):
            img=Image.objects.get(pk=derivedFromImageId)
            #Save Image in Database
            imgHeight=640;
            imgWidth=640;        
            saveImg = Image(image_name=newFileName,\
                image_location=location,\
                image_height=imgHeight,\
                image_width=imgWidth,\
                is_annotated=is_annotated_flag,\
                centerLatitude=centerLat,\
                centerLongitude=centerLng,\
                zoom_level=zoom,\
                derived_from_image=img) 
            saveImg.save() 

        else:    
            img=Image.objects.filter(image_name=filename)

            # if img.count() > 0:            
            #     data ={
            #         'status':-1
            #     }
            #     return JsonResponse(data)
        
            #Save Image in Database
            imgHeight=640;
            imgWidth=640;        
            saveImg = Image(image_name=newFileName,\
                image_location=location,\
                image_height=imgHeight,\
                image_width=imgWidth,\
                is_annotated=is_annotated_flag,\
                centerLatitude=centerLat,\
                centerLongitude=centerLng,zoom_level=zoom) 
            saveImg.save() 


        # #Download Image on server 
        downloadImage(imgUrl,filepath)        
        if(ground_truthing_done=='true'):
            ground_truthing_done=True
        else:
            ground_truthing_done=False

        if(is_annotated_flag):            
            #Save Marker to Database
            if(gmapMarkerId==None):            
                for marker_i in markers:                      
                    json_marker_i=json.dumps(marker_i)                         
                    saveMarker = GMapMarker(source_image=saveImg,locality=locality,district=district,\
                                        geometryJSON=json_marker_i,ground_truthing_done=ground_truthing_done)
                    saveMarker.save()    
        
            #Save Annotations on database                
            print(len(annotations))            
            for ann_i in annotations:            
                classnm=''            
                for key, value in ann_i.items():                                    
                    if(key=='classnm'):
                        classnm = value  
                        json_ann_i=json.dumps(ann_i);                                  
                saveAnnot = Annotation(source_image=saveImg,class_label=classnm,geometryJSON=json_ann_i)
                saveAnnot.save()    

            #Make a relationship between image saved and JSmapped work. 
            #Thus to be removed from list of JSMapped work on interface
            if(derivedFromImageId==None):
                #Loop Thru District wise jsmappedworks and flag those which are covered in one image
                mapBounds = Polygon.from_bbox((topLeftLat,topLeftLng,bottomRightLat,bottomRightLng))
                print(district)
                # jsmappedworks = JSMappedWorks.objects.filter(dataOfYear='2015-16',\
                #                   district__english_name=district,\
                #                   work_type__english_name='Farm Pond')
                jsmappedworks = JSMappedWorks.objects.filter(district__english_name=district,\
                                   work_type__english_name='Farm Pond')

                #obj=jsmappedworks[0]
                #print(obj)      
                for obj in jsmappedworks:
                    latlng=(obj.latitude,obj.longitude)
                    point = Point(latlng)
                    flag=mapBounds.contains(point)             
                    if(flag):
                        # markedObj = JSMappedWorks.objects.get(latitude=latlng[0],longitude=latlng[1],\
                        #                         dataOfYear='2015-16',district__english_name=district,\
                        #                         work_type__english_name='Farm Pond')            
                        # print("-----------------")
                        # print(obj)
                        # print(obj.is_marked)
                        obj.is_marked = True  # update record
                        # print("Changed"+str(obj.is_marked))
                        # print(obj)
                        # print("**-----------------**")
                        #obj.save()
                        #Map Image(Dataset) with JSMappedWorks
                        jsmappedworksimg=JSMappedWorksImage(jsmappedwork=obj,image=saveImg)
                        #jsmappedworksimg.save()
                
                #flag=mapBounds.contains(ls2)
                # ls1=LineString(((19.85849090,75.51621409),(19.85849594,75.51662715),(19.85804186,75.51666470),(19.85803176,75.51624092)))    
                # ls2=LineString(((19.85731082,75.50629352),(19.85728055,75.50688360),(19.85690719,75.50686215),(19.85696773,75.50631498)))
                # bb1 = Polygon.from_bbox((19.86093151780648,75.5143893862305,19.85770246576097,75.51782261376957))
                # ans=bb1.contains(ls2)
                # print(ans)
      

        #Send success signal to the caller
        data = {
             'status': 1
        }        
        return JsonResponse(data)
    return JsonResponse(data)
def save_image_wells(request):
    data = {}
    if request.method == 'POST':
        topLeftLat = request.POST.get('topLeftLat')
        topLeftLng = request.POST.get('topLeftLng')
        bottomRightLat = request.POST.get('bottomRightLat')
        bottomRightLng = request.POST.get('bottomRightLng')
        centerLat = request.POST.get('centerLat') 
        centerLng = request.POST.get('centerLng')        
        district  = request.POST.get('district')
        locality = request.POST.get('locality')             
        markersJson = request.POST.get('markersJSON')
        annotationsJson = request.POST.get('annotationJSON')
        ground_truthing_done = request.POST.get('groundTruthingDone')
        zoom =int(float(request.POST.get('zoom')))        
        zoom = str(zoom)        
        filename=str(district)+"_"+str(locality)+"_"+str(centerLat)+"_"+str(centerLng);
        print(filename)
        # data  = json.loads(markers_json)           
        location = 'static/Gmapv2/images/Wells/';        
        key = 'AIzaSyDQrhuv_BxZGPpB1WGF-dLTKbumKYchpvo';
        maptype = 'satellite';
        size = '640x640';
        url_center = centerLat+","+centerLng
        imgUrl = "https://maps.googleapis.com/maps/api/staticmap?center="+url_center + '&size=' + size + '&zoom=' + zoom + '&maptype=' + maptype + '&key='+key
        print(imgUrl)
        newFileName=filename+"_0.png";
        filepath=location+newFileName;        
        lastpos=len(filepath)-filepath.rfind('_')
        filepathpattern=filepath[:-lastpos]
        my_file = Path(filepath)
        if my_file.exists():
            files=glob.glob(filepathpattern+"*")
            total=len(files)            
            newFileName=filename+"_"+str(total)+".png"
            filepath=location+newFileName;            
    
        # img=Image.objects.filter(image_name=filename)
        # if img.count() > 0:            
        #     data ={
        #         'status':-1
        #     }
        #     return JsonResponse(data)
        is_annotated_flag=False
        if(len(annotationsJson)>0):
            is_annotated_flag=True

        #Save Image in Database
        imgHeight=640;
        imgWidth=640;        
        saveImg = Image(image_name=newFileName,\
            image_location=location,\
            image_height=imgHeight,\
            image_width=imgWidth,\
            is_annotated=is_annotated_flag,\
            centerLatitude=centerLat,\
            centerLongitude=centerLng) 
        saveImg.save() 


        #Download Image on server 
        downloadImage(imgUrl,filepath)        
        if(ground_truthing_done=='true'):
            ground_truthing_done=True
        else:
            ground_truthing_done=False

        #Save Marker to Database
        markers  = json.loads(markersJson)        
        for marker_i in markers:                      
            json_marker_i=json.dumps(marker_i)                         
            saveMarker = GMapMarker(source_image=saveImg,locality=locality,district=district,\
                                    geometryJSON=json_marker_i,ground_truthing_done=ground_truthing_done)
            saveMarker.save()    
        
        #Save Annotations to Database    
        annotations  = json.loads(annotationsJson)          
        for ann_i in annotations:            
            classnm=''            
            for key, value in ann_i.items():                
                if(key=='classnm'):
                    classnm = value  
                    json_ann_i=json.dumps(ann_i); 

                    #print(json_ann_i)
            saveAnnot = Annotation(source_image=saveImg,class_label=classnm,geometryJSON=json_ann_i)
            saveAnnot.save()    


        #Loop Thru District wise jsmappedworks and flag those which are covered in one image
        mapBounds = Polygon.from_bbox((topLeftLat,topLeftLng,bottomRightLat,bottomRightLng))
        #print(district)
        jsmappedworks = JSMappedWorks.objects.filter(Q(district__english_name=district),\
                          (Q(work_type__english_name='Well rehabilitation')|\
                          Q(work_type__english_name='Vindhan Well rehabilitation')))
        print(jsmappedworks.count())
        #obj=jsmappedworks[0]        
        for obj in jsmappedworks:
            latlng=(obj.latitude,obj.longitude)
            point = Point(latlng)
            flag=mapBounds.contains(point)                         
            if(flag):        
                obj.is_marked = True  # update record
                # print("Changed"+str(obj.is_marked))
                # print(obj)
                # print("**-----------------**")
                obj.save()
                #Map Image(Dataset) with JSMappedWorks
                jsmappedworksimg=JSMappedWorksImage(jsmappedwork=obj,image=saveImg)
                jsmappedworksimg.save()

        #Send success signal to the caller
        data = {
             'status': 1
        }
        return JsonResponse(data)
    return JsonResponse(data)

#Deletes image and annotation from database
def deleteImage(request):
    data = {
                'status': -1
    }
    if request.method == 'POST':
        image_name = request.POST.get('image_name')
        deleteImg=Image.objects.get(image_name=image_name)
        jsmappedworksimgs=JSMappedWorksImage.objects.filter(image=deleteImg)
        for jsmwi in jsmappedworksimgs:
            jsmw=jsmwi.jsmappedwork
            jsmw.is_marked=False
            jsmw.save()
            jsmwi.delete()


        print(deleteImg)
        image_location=deleteImg.image_location+"/"+deleteImg.image_name        
        if os.path.exists(image_location):
          os.remove(image_location)
          deleteImg.delete()
        else:
          print("The file does not exist")
          data = {
                'status': -1
          } 
          return JsonResponse(data)
        

        data = {
                'status': 1
        }
        return JsonResponse(data)

    return JsonResponse(data)
def approveImage(request):
    data = {
                'status': -1
    }
    if request.method == 'POST':
        image_name = request.POST.get('image_name')
        approveFlag = request.POST.get('approve_flag')
        approveImg=Image.objects.get(image_name=image_name)
        if(approveFlag=='true'):
            approveImg.is_approved=True
        if(approveFlag=='false'):
            approveImg.is_approved=False
        approveImg.save()
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
    template = loader.get_template('Gmapv2/testCanvas.html');
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
    template = loader.get_template('Gmapv2/showAllMarkers.html');
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
    template = loader.get_template('Gmapv2/testCode.html');
    context = {}    
    return HttpResponse(template.render(context, request))  

def extractFPs(request):
        template = loader.get_template('testCode.html');
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
def getMinCoord(coordDict):
    x=sys.maxsize;
    y=sys.maxsize;
    minCoord={};
    for coord in coordDict:
        if(x>coord['x']):
            if(coord['x']<0):
                x=0;
            else:    
                x=coord['x'];
        if(y>coord['y']):
            if(coord['y']<0):
                y=0;
            else:    
                y=coord['y'];

    minCoord["x"]=x;
    minCoord["y"]=y;     
    return minCoord;

def getMaxCoord(coordDict):
    x=0;
    y=0;
    maxCoord={};
    for coord in coordDict:
        if(x<coord['x']):
            if(coord['x']>640): #change when img size is variable
                x=640;
            else:    
                x=coord['x'];
        if(y<coord['y']):
            if(coord['y']>640): #change when img size is variable
                y=640;
            else:    
                y=coord['y'];

    maxCoord["x"]=x;
    maxCoord["y"]=y;
    return maxCoord;    

def downloadDatasetFP(request):
    zoom_level = request.GET.get('zl') 
    print(zoom_level)
    if(zoom_level=='18_19'):
        imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),\
                                #Q(is_annotated=False),
                                Q(is_approved=True), Q(zoom_level=18)|Q(zoom_level=19)).distinct().extra(order_by = ['image_name']);    


    if(zoom_level=='18'):
        imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),\
                                #Q(is_annotated=False),
                                Q(is_approved=True),zoom_level=18).distinct().extra(order_by = ['image_name']);   
        

    if(zoom_level=='19'):
        imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),\
                                #Q(is_annotated=False),
                                Q(is_approved=True),zoom_level=19).distinct().extra(order_by = ['image_name']);  
                                  
    print(len(imgs))
    filename="Dataset-FarmPonds";
    location="static/Gmapv2/zip/"
    newZipFileName=filename+"_0.zip";
    zipPath=location+newZipFileName;        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():
        files=glob.glob(filepathpattern+"*")
        total=len(files)            
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=location+newZipFileName;            

    allRows=[];
    for img in imgs:
        row={};        
        image_name=img.image_name        
        image_width=img.image_width
        image_height=img.image_height
        date_captured=img.captured_date
        img_path=img.image_location
        row["file_name"]=image_name;
        row["width"]=int(image_width);
        row["height"]=int(image_height);
        row["date_captured"]=date_captured.strftime("%m/%d/%Y");
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];
        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            currAnnJson['classnm'] = data['classnm']            
            pixelCoords = data['pixelCoords']
            currAnnJson['segmentation'] = pixelCoords
            minCoord=getMinCoord(pixelCoords)
            maxCoord=getMaxCoord(pixelCoords)
            width=maxCoord["x"]-minCoord["x"]
            height=maxCoord["y"]-minCoord["y"]
            bbox={};
            bbox["x"]=round(minCoord["x"]);
            bbox["y"]=round(minCoord["y"]);
            bbox["width"]=round(width);
            bbox["height"]=round(height);
            currAnnJson['bbox']=bbox;
            arrJson.append(currAnnJson)        
        row["annotations"]=arrJson
        allRows.append(row);              
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path=img_path #"static/Gmapv2/images/FarmPonds/"
            filename=image_name            
            oldPath=os.path.join(path,filename)
            if(not os.path.isfile(oldPath)):
                print("Not Found : "+filename)
            newPath="Images/"+filename
            newzip.write(oldPath,newPath)

    
    finalJSON=json.dumps(allRows, separators=(',', ':'))
    jsonFilename='dataset.json'
    path=os.path.join("static/Gmapv2/json/",jsonFilename);    
    with open(path, 'w') as f:
        json.dump(finalJSON, f)            
    with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:        
        newzip.write(path,jsonFilename)


    context = {        
    }      
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDataset_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response;

def downloadDatasetFPYOLO(request):
    imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),
                                Q(is_approved=True)).distinct().extra(order_by = ['image_name']);   

    filename="Dataset-FarmPonds";
    location="static/Gmapv2/zip/yolo/"
    newZipFileName=filename+"_0.zip";
    zipPath=os.path.join(location,newZipFileName)        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():        
        files=glob.glob(filepathpattern+"*")
        total=len(files)        
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=os.path.join(location,newZipFileName)

    allRows=[];
    for img in imgs:
        row={};        
        image_name=img.image_name                
        row["file_name"]=image_name;
                    
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];
        annotLines="";
        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            classnm = data['classnm']            
            pixelCoords = data['pixelCoords']            
            minCoord=getMinCoord(pixelCoords)
            maxCoord=getMaxCoord(pixelCoords)
            diffx=maxCoord["x"]/640-minCoord["x"]/640
            diffy=maxCoord["y"]/640-minCoord["y"]/640
            width=round(diffx,6)
            height=round(diffy,6)
            center_x=round(((minCoord["x"]/640)+(diffx/2)),6)
            center_y=round(((minCoord["y"]/640)+(diffy/2)),6)
            classnmlab=-1
            if(classnm=="Wet Farm Pond - Lined"):
                classnmlab=FarmPondLabel.WetFPLined.value;
            if(classnm=="Wet Farm Pond - Unlined"):            
                classnmlab=FarmPondLabel.WetFPUnlined.value;
            if(classnm=="Dry Farm Pond - Lined"):            
                classnmlab=FarmPondLabel.DryFPLined.value;
            if(classnm=="Dry Farm Pond - Unlined"):            
                classnmlab=FarmPondLabel.DryFPUnlined.value;
            bbox = str(classnmlab) 
            bbox = bbox + " " + str(center_x);
            bbox = bbox + " " + str(center_y);
            bbox = bbox + " " + str(width);
            bbox = bbox + " " + str(height);
            annotLines = annotLines + bbox + "\n"
                        
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/FarmPonds/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="images/"+filename
            newzip.write(oldPath,newPath)

        fname=os.path.splitext(image_name)[0]
        txtFilename=fname+".txt"
        path=os.path.join("static/Gmapv2/txt/",txtFilename);    
        with open(path, "w") as file:
            file.write(annotLines)
        
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            newPath="labels/"+txtFilename
            newzip.write(path,newPath)
        
    context = {        
    }        
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDatasetYOLO_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response;    


def downloadDatasetFPYOLODetection(request):
    imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),
                                Q(is_approved=True)).distinct().extra(order_by = ['image_name']);   

    filename="Dataset-FarmPonds";
    location="static/Gmapv2/zip/yolo/"
    newZipFileName=filename+"_0.zip";
    zipPath=os.path.join(location,newZipFileName)        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():        
        files=glob.glob(filepathpattern+"*")
        total=len(files)        
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=os.path.join(location,newZipFileName)

    allRows=[];
    for img in imgs:
        #row={};        
        image_name=img.image_name                
        #row["file_name"]=image_name;
                    
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];
        annotLines="";
        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            classnm = data['classnm']            
            pixelCoords = data['pixelCoords']            
            minCoord=getMinCoord(pixelCoords)
            maxCoord=getMaxCoord(pixelCoords)
            diffx=maxCoord["x"]/640-minCoord["x"]/640
            diffy=maxCoord["y"]/640-minCoord["y"]/640
            width=round(diffx,6)
            height=round(diffy,6)
            center_x=round(((minCoord["x"]/640)+(diffx/2)),6)
            center_y=round(((minCoord["y"]/640)+(diffy/2)),6)
            classnmlab=-1
            if(classnm=="Wet Farm Pond - Lined"):
                classnmlab=FarmPondLabel.WetFPLined.value;
            if(classnm=="Wet Farm Pond - Unlined"):            
                classnmlab=FarmPondLabel.WetFPUnlined.value;
            if(classnm=="Dry Farm Pond - Lined"):            
                classnmlab=FarmPondLabel.DryFPLined.value;
            if(classnm=="Dry Farm Pond - Unlined"):            
                classnmlab=FarmPondLabel.DryFPUnlined.value;
            # bbox = str(classnmlab) 
            bbox = "0" 
            bbox = bbox + " " + str(center_x);
            bbox = bbox + " " + str(center_y);
            bbox = bbox + " " + str(width);
            bbox = bbox + " " + str(height);
            # bbox = "FarmPond" 
            # bbox = bbox + " " + str(minCoord["x"]);
            # bbox = bbox + " " + str(minCoord["y"]);
            # bbox = bbox + " " + str(maxCoord["x"]);
            # bbox = bbox + " " + str(maxCoord["y"]);
            annotLines = annotLines + bbox + "\n"
        '''                
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/FarmPonds/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="images/"+filename
            newzip.write(oldPath,newPath)
        '''

        fname=os.path.splitext(image_name)[0]
        txtFilename=fname+".txt"
        path=os.path.join("static/Gmapv2/txt/",txtFilename);    
        with open(path, "w") as file:
            file.write(annotLines)
        
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            newPath="labels/"+txtFilename
            newzip.write(path,newPath)
        
    context = {        
    }        
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDatasetYOLO_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response; 

def downloadDatasetFPCOCO(request):
    imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),
                                Q(is_approved=True)).distinct().extra(order_by = ['image_name']);   

    filename="Dataset-FarmPonds";
    location="static/Gmapv2/coco/"
    newZipFileName=filename+"_0.zip";
    zipPath=os.path.join(location,newZipFileName)        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():        
        files=glob.glob(filepathpattern+"*")
        total=len(files)        
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=os.path.join(location,newZipFileName)

    allRows=[];
    json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}
    image_id=1
    bnd_id=1
    cat = {"supercategory": "none", "id": 1, "name": "Wet Farm Pond - Lined"}        
    json_dict["categories"].append(cat)
    cat = {"supercategory": "none", "id": 2, "name": "Wet Farm Pond - Unlined"}
    json_dict["categories"].append(cat)
    cat = {"supercategory": "none", "id": 3, "name": "Dry Farm Pond - Lined"}
    json_dict["categories"].append(cat)
    cat = {"supercategory": "none", "id": 4, "name": "Dry Farm Pond - Unlined"}
    json_dict["categories"].append(cat)

    for img in imgs:
        row={};        
        image_name=img.image_name                
        row["file_name"]=image_name;
        
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];
        annotLines="";

        width=int(img.image_width)
        height=int(img.image_height)
        image = {
           "file_name": image_name,
           "height": height,
           "width": width,
           "id": image_id,
        }
        json_dict["images"].append(image)

        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            classnm = data['classnm']            
            pixelCoords = data['pixelCoords']            
            minCoord=getMinCoord(pixelCoords)
            maxCoord=getMaxCoord(pixelCoords)
            xmin=minCoord["x"]
            ymin=minCoord["y"]
            xmax=maxCoord["x"]
            ymax=maxCoord["y"]            
            width=abs(xmax-xmin)
            height=abs(ymax-ymin)
            #center_x=round(((minCoord["x"]/640)+(diffx/2)),6)
            #center_y=round(((minCoord["y"]/640)+(diffy/2)),6)
            classnmlab=-1
            if(classnm=="Wet Farm Pond - Lined"):
                category_id=1;
                classnmlab=FarmPondLabel.WetFPLined.value;
            if(classnm=="Wet Farm Pond - Unlined"):            
                category_id=2;
                classnmlab=FarmPondLabel.WetFPUnlined.value;
            if(classnm=="Dry Farm Pond - Lined"):            
                category_id=3;
                classnmlab=FarmPondLabel.DryFPLined.value;
            if(classnm=="Dry Farm Pond - Unlined"):            
                category_id=4;
                classnmlab=FarmPondLabel.DryFPUnlined.value;
            # bbox = str(classnmlab) 
            # bbox = bbox + " " + str(center_x);
            # bbox = bbox + " " + str(center_y);
            # bbox = bbox + " " + str(width);
            # bbox = bbox + " " + str(height);
            # annotLines = annotLines + bbox + "\n"

            ann = {
                "area": str(width * height),
                "iscrowd": 0,
                "image_id": image_id,
                "bbox": [xmin, ymin, width, height],
                "category_id": category_id,
                "id": bnd_id,
                "ignore": 0,
                "segmentation": [],
            }
            json_dict["annotations"].append(ann)

        
        print(json_dict)
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/FarmPonds/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="images/"+filename
            newzip.write(oldPath,newPath)

        # fname=os.path.splitext(image_name)[0]
        # txtFilename=fname+".txt"
        # path=os.path.join("static/Gmapv2/txt/",txtFilename);    
        # with open(path, "w") as file:
        #     file.write(annotLines)
        
        jsonFilename='dataset.json'
        path=os.path.join("static/Gmapv2/json/",jsonFilename); 
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json_fp = open(path, "w")
        json_str = json.dumps(json_dict)
        json_fp.write(json_str)
        json_fp.close()
        
        # with open(path, 'w') as f:
        #     json.dump(finalJSON, f)            
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:        
            newzip.write(path,jsonFilename)

        # with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
        #     newPath="labels/"+txtFilename
        #     newzip.write(path,newPath)
           
        image_id = image_id + 1
        bnd_id = bnd_id + 1   
    context = {        
    }        
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDatasetYOLO_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response;    

def downloadDatasetFPCSV(request):

    zoom_level = request.GET.get('zl') 
    if(zoom_level=='18'):
        imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),\
                                #Q(is_annotated=False),
                                Q(is_approved=True),zoom_level=18).distinct().extra(order_by = ['image_name']);   
    if(zoom_level=='19'):
        imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),\
                                #Q(is_annotated=False),
                                Q(is_approved=True),zoom_level=19).distinct().extra(order_by = ['image_name']);  
    if(zoom_level=='18_19'):
        imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),\
                                #Q(is_annotated=False),
                                Q(is_approved=True), Q(zoom_level=18)|Q(zoom_level=19)).distinct().extra(order_by = ['image_name']);
    filename="Dataset-FarmPonds";
    location="static/Gmapv2/csv/"
    newZipFileName=filename+"_0.zip";
    zipPath=os.path.join(location,newZipFileName)        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():        
        files=glob.glob(filepathpattern+"*")
        total=len(files)        
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=os.path.join(location,newZipFileName)

    allRows=[];    
    annotLines="";
    for img in imgs:        
        image_name=img.image_name                        
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];    
        width=int(img.image_width)
        height=int(img.image_height)
        

        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            classnm = data['classnm']            
            pixelCoords = data['pixelCoords']            
            minCoord=getMinCoord(pixelCoords)
            maxCoord=getMaxCoord(pixelCoords)
            xmin=minCoord["x"]
            ymin=minCoord["y"]
            xmax=maxCoord["x"]
            ymax=maxCoord["y"]            
            #width=abs(xmax-xmin)
            #height=abs(ymax-ymin)
            #center_x=round(((minCoord["x"]/640)+(diffx/2)),6)
            #center_y=round(((minCoord["y"]/640)+(diffy/2)),6)            
            # bbox = str(classnmlab) 
            
            bbox="images/"+image_name
            if(classnm=='Wet Farm Pond - Lined'):
                finalClassName='WetFPLined'
            if(classnm=='Wet Farm Pond - Unlined'):
                finalClassName='WetFPUnlined'
            if(classnm=='Dry Farm Pond - Lined'):
                finalClassName='DryFPLined'
            if(classnm=='Dry Farm Pond - Unlined'):
                finalClassName='DryFPUnlined'

            #bbox=image_name
            bbox = bbox + "," + str(minCoord["x"]);
            bbox = bbox + "," + str(minCoord["y"]);
            bbox = bbox + "," + str(maxCoord["x"]);
            bbox = bbox + "," + str(maxCoord["y"]);
            bbox = bbox + "," + finalClassName
            annotLines = annotLines + bbox + "\n"

        #Uncomment to start downloading images    
        '''
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/FarmPonds/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="images/"+filename
            newzip.write(oldPath,newPath)
        '''

        # fname=os.path.splitext(image_name)[0]
        # txtFilename=fname+".txt"
        # path=os.path.join("static/Gmapv2/txt/",txtFilename);    
        # with open(path, "w") as file:
        #     file.write(annotLines)
            
    txtFilename="annotations.csv"
    path=os.path.join("static/Gmapv2/csv/",txtFilename);    
    with open(path, "w") as file:
        file.write(annotLines)
    
    with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
        newPath="annotations/"+txtFilename
        newzip.write(path,newPath)
        
    context = {        
    }        
    
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDatasetYOLO_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response; 

def downloadDatasetFPCustom1(request):
    #FORMAT
    #Row format: image_file_path box1 box2 ... boxN;
    #Box format: x_min,y_min,x_max,y_max,class_id (no space).
    imgs = Image.objects.filter(Q(annotation__class_label="Wet Farm Pond - Lined")|\
                                Q(annotation__class_label="Wet Farm Pond - Unlined")|\
                                Q(annotation__class_label="Dry Farm Pond - Lined")|\
                                Q(annotation__class_label="Dry Farm Pond - Unlined"),
                                Q(is_approved=True)).distinct().extra(order_by = ['image_name']);   

    filename="Dataset-FarmPonds";
    location="static/Gmapv2/txt/"
    newZipFileName=filename+"_0.zip";
    zipPath=os.path.join(location,newZipFileName)        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():        
        files=glob.glob(filepathpattern+"*")
        total=len(files)        
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=os.path.join(location,newZipFileName)

    allRows=[];    
    annotLines="";
    for img in imgs:        
        image_name=img.image_name                        
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];    
        width=int(img.image_width)
        height=int(img.image_height)
        
        bbox="../Dataset/FarmPondDataset_2019_12_10/images/"+image_name        
        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            classnm = data['classnm']
            xmin=0
            ymin=0
            xmax=0
            ymax=0
            if(currAnnJson['type']=='polygon'):                
                pixelCoords = data['pixelCoords']            
                minCoord=getMinCoord(pixelCoords)
                maxCoord=getMaxCoord(pixelCoords)
                xmin=minCoord["x"]
                ymin=minCoord["y"]
                xmax=maxCoord["x"]
                ymax=maxCoord["y"]            
                #width=abs(xmax-xmin)
                #height=abs(ymax-ymin)
                #center_x=round(((minCoord["x"]/640)+(diffx/2)),6)
                #center_y=round(((minCoord["y"]/640)+(diffy/2)),6)            
                # bbox = str(classnmlab)             
            finalClassName=''
            if(classnm=='Wet Farm Pond - Lined'):
                finalClassName='0'
            if(classnm=='Wet Farm Pond - Unlined'):
                finalClassName='1'
            if(classnm=='Dry Farm Pond - Lined'):
                finalClassName='2'
            if(classnm=='Dry Farm Pond - Unlined'):
                finalClassName='3'

            #bbox=image_name
            bbox = bbox + " " + str(xmin);
            bbox = bbox + "," + str(ymin);
            bbox = bbox + "," + str(xmax);
            bbox = bbox + "," + str(ymax);
            bbox = bbox + "," + finalClassName
            
        annotLines = annotLines + bbox + "\n"

        #Uncomment to start downloading images    
        '''
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/FarmPonds/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="images/"+filename
            newzip.write(oldPath,newPath)
        '''

        # fname=os.path.splitext(image_name)[0]
        # txtFilename=fname+".txt"
        # path=os.path.join("static/Gmapv2/txt/",txtFilename);    
        # with open(path, "w") as file:
        #     file.write(annotLines)
            
    txtFilename="annotations.txt"
    path=os.path.join("static/Gmapv2/txt/",txtFilename);    
    with open(path, "w") as file:
        file.write(annotLines)
    
    with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
        newPath="annotations/"+txtFilename
        newzip.write(path,newPath)
        
    context = {        
    }        
    
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDatasetYOLO_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response; 



def downloadDatasetWells(request):
    imgs = Image.objects.filter(annotation__class_label="Well",is_approved=True)\
                                .distinct().extra(order_by = ['image_name']);   

    filename="Dataset-Wells";
    location="static/Gmapv2/zip/"
    newZipFileName=filename+"_0.zip";
    filepath=location+newZipFileName;        
    lastpos=len(filepath)-filepath.rfind('_')
    filepathpattern=filepath[:-lastpos]
    my_file = Path(filepath)
    if my_file.exists():
        files=glob.glob(filepathpattern+"*")
        total=len(files)            
        newZipFileName=filename+"_"+str(total)+".zip"
        filepath=location+newZipFileName;            
    zipPath=os.path.join(location,newZipFileName)
    allRows=[];
    for img in imgs:
        row={};        
        image_name=img.image_name        
        image_width=img.image_width
        image_height=img.image_height
        date_captured=img.captured_date
        row["file_name"]=image_name;
        row["width"]=int(image_width);
        row["height"]=int(image_height);
        row["date_captured"]=date_captured.strftime("%m/%d/%Y");
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];
        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            currAnnJson['classnm'] = data['classnm']            
            if(data['type']=="polygon"):
                pixelCoords = data['pixelCoords']
                currAnnJson['segmentation'] = pixelCoords
                minCoord=getMinCoord(pixelCoords)
                maxCoord=getMaxCoord(pixelCoords)
                width=maxCoord["x"]-minCoord["x"]
                height=maxCoord["y"]-minCoord["y"]
                bbox={};
                bbox["x"]=round(minCoord["x"]);
                bbox["y"]=round(minCoord["y"]);
                bbox["width"]=round(width);
                bbox["height"]=round(height);
            if(data['type']=="circle"):
                #{"type": "circle", "objectNo": 0, 
                #"radius": 12.08278171440412, 
                #"center": {"x": 347, "y": 371}, 
                #"classnm": "Well"}
                center=data['center'];
                radius=data['radius'];
                center["x"]=round(center["x"])
                center["y"]=round(center["y"])
                currAnnJson['center']=center;
                currAnnJson['radius']=round(radius);
                bbox={};
                bbox["x"]=round(center["x"]-radius);
                bbox["y"]=round(center["y"]-radius);
                bbox["width"]=round(2*radius);
                bbox["height"]=round(2*radius);            
            currAnnJson['bbox']=bbox;
            arrJson.append(currAnnJson)        
        row["annotations"]=arrJson
        allRows.append(row);
        zipPath=os.path.join(location,newZipFileName)
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/Wells/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="Images/"+filename
            newzip.write(oldPath,newPath)

    
    finalJSON=json.dumps(allRows, separators=(',', ':'))
    jsonFilename='dataset.json'
    path=os.path.join("static/Gmapv2/json/",jsonFilename);    
    with open(path, 'w') as f:
        json.dump(finalJSON, f)            
    with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:        
        newzip.write(path,jsonFilename)


    context = {        
    }    
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    return response;

def downloadDatasetWellsCSV(request):
    imgs = Image.objects.filter(annotation__class_label="Well",is_approved=True)\
                                .distinct().extra(order_by = ['image_name']);   

    filename="Dataset-Wells";
    location="static/Gmapv2/csv/"
    newZipFileName=filename+"_0.zip";
    zipPath=os.path.join(location,newZipFileName)        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():        
        files=glob.glob(filepathpattern+"*")
        total=len(files)        
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=os.path.join(location,newZipFileName)

    allRows=[];    
    annotLines="";
    for img in imgs:        
        image_name=img.image_name                        
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];    
        width=int(img.image_width)
        height=int(img.image_height)
        

        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            classnm = data['classnm']
            xmin=0
            ymin=0
            xmax=0
            ymax=0
            if(currAnnJson['type']=='polygon'):                
                pixelCoords = data['pixelCoords']            
                minCoord=getMinCoord(pixelCoords)
                maxCoord=getMaxCoord(pixelCoords)
                xmin=minCoord["x"]
                ymin=minCoord["y"]
                xmax=maxCoord["x"]
                ymax=maxCoord["y"]            
                #width=abs(xmax-xmin)
                #height=abs(ymax-ymin)
                #center_x=round(((minCoord["x"]/640)+(diffx/2)),6)
                #center_y=round(((minCoord["y"]/640)+(diffy/2)),6)            
                # bbox = str(classnmlab) 
            if(currAnnJson['type']=='circle'):                
                radius = data['radius']
                center = data['center']
                center_x = center["x"]
                center_y = center["y"]
                xmin=round(center_x-radius)
                ymin=round(center_y-radius)
                xmax=round(center_x+radius)
                ymax=round(center_y+radius)

            bbox="images/"+image_name
            #bbox=image_name
            bbox = bbox + "," + str(xmin);
            bbox = bbox + "," + str(ymin);
            bbox = bbox + "," + str(xmax);
            bbox = bbox + "," + str(ymax);
            bbox = bbox + "," + "Well" 
            annotLines = annotLines + bbox + "\n"

        #Uncomment to start downloading images    
        '''
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/FarmPonds/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="images/"+filename
            newzip.write(oldPath,newPath)
        '''

        # fname=os.path.splitext(image_name)[0]
        # txtFilename=fname+".txt"
        # path=os.path.join("static/Gmapv2/txt/",txtFilename);    
        # with open(path, "w") as file:
        #     file.write(annotLines)
            
    txtFilename="annotations.csv"
    path=os.path.join("static/Gmapv2/csv/",txtFilename);    
    with open(path, "w") as file:
        file.write(annotLines)
    
    with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
        newPath="annotations/"+txtFilename
        newzip.write(path,newPath)
        
    context = {        
    }        
    
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDatasetYOLO_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response;  


def downloadDatasetWellsCustom1(request):
    #FORMAT
    #Row format: image_file_path box1 box2 ... boxN;
    #Box format: x_min,y_min,x_max,y_max,class_id (no space).
    imgs = Image.objects.filter(annotation__class_label="Well",is_approved=True)\
                                .distinct().extra(order_by = ['image_name']);   

    filename="Dataset-Wells";
    location="static/Gmapv2/txt/"
    newZipFileName=filename+"_0.zip";
    zipPath=os.path.join(location,newZipFileName)        
    lastpos=len(zipPath)-zipPath.rfind('_')
    filepathpattern=zipPath[:-lastpos]
    my_file = Path(zipPath)
    zipPath=os.path.join(location,newZipFileName)
    if my_file.exists():        
        files=glob.glob(filepathpattern+"*")
        total=len(files)        
        newZipFileName=filename+"_"+str(total)+".zip"
    zipPath=os.path.join(location,newZipFileName)

    allRows=[];    
    annotLines="";
    for img in imgs:        
        image_name=img.image_name                        
        annots=Annotation.objects.filter(source_image=img)        
        arrJson=[];    
        width=int(img.image_width)
        height=int(img.image_height)
        
        bbox="../Dataset/WellDataset_2019_12/images/"+image_name        
        for annot in annots:
            currAnnJson={}
            geometryJSON = annot.geometryJSON;
            data  = json.loads(geometryJSON)
            currAnnJson['type'] = data['type']
            classnm = data['classnm']
            xmin=0
            ymin=0
            xmax=0
            ymax=0
            if(currAnnJson['type']=='polygon'):                
                pixelCoords = data['pixelCoords']            
                minCoord=getMinCoord(pixelCoords)
                maxCoord=getMaxCoord(pixelCoords)
                xmin=minCoord["x"]
                ymin=minCoord["y"]
                xmax=maxCoord["x"]
                ymax=maxCoord["y"]            
                #width=abs(xmax-xmin)
                #height=abs(ymax-ymin)
                #center_x=round(((minCoord["x"]/640)+(diffx/2)),6)
                #center_y=round(((minCoord["y"]/640)+(diffy/2)),6)            
                # bbox = str(classnmlab) 
            if(currAnnJson['type']=='circle'):                
                radius = data['radius']
                center = data['center']
                center_x = center["x"]
                center_y = center["y"]
                xmin=round(center_x-radius)
                ymin=round(center_y-radius)
                xmax=round(center_x+radius)
                ymax=round(center_y+radius)

            
            #bbox=image_name
            bbox = bbox + " " + str(xmin);
            bbox = bbox + "," + str(ymin);
            bbox = bbox + "," + str(xmax);
            bbox = bbox + "," + str(ymax);
            bbox = bbox + "," + "0" 
            
        annotLines = annotLines + bbox + "\n"

        #Uncomment to start downloading images    
        '''
        with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
            path="static/Gmapv2/images/FarmPonds/"
            filename=image_name
            oldPath=os.path.join(path,filename)
            newPath="images/"+filename
            newzip.write(oldPath,newPath)
        '''

        # fname=os.path.splitext(image_name)[0]
        # txtFilename=fname+".txt"
        # path=os.path.join("static/Gmapv2/txt/",txtFilename);    
        # with open(path, "w") as file:
        #     file.write(annotLines)
            
    txtFilename="annotations.txt"
    path=os.path.join("static/Gmapv2/csv/",txtFilename);    
    with open(path, "w") as file:
        file.write(annotLines)
    
    with zipfile.ZipFile(zipPath,'a', zipfile.ZIP_DEFLATED) as newzip:
        newPath="annotations/"+txtFilename
        newzip.write(path,newPath)
        
    context = {        
    }        
    
    response = HttpResponse(open(zipPath, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % ("FarmPondDatasetYOLO_"+dttm.today().strftime('%Y_%m_%d')+".zip")    
    return response;  



######Code snippet dumps##########
# temp='static/Gmap/images';
#             if(sourceLocation[18]!='/'):
#                 temp1=sourceLocation[0:18]+'/'+sourceLocation[18:]
#                 eachimg.image_location=temp1
#                 eachimg.save()



########Web Scraping#############

def testLoading(request):    
    #Uncomment when loading
    template = loader.get_template('Gmapv2/All HTMLS/2017-18_Kolhapur_530.html')
    context = {        
    }    
    return HttpResponse(template.render(context, request))

def saveJSDataToDb(request):
    data = {}   
    if request.method == 'POST':
        try:
            latitude= request.POST.get('lat')  
            longitude = request.POST.get('lng')                                              
            remark = request.POST.get('remark')  
            date_recorded = request.POST.get('date_recorded')  
            time_recorded = request.POST.get('time_recorded')  
            address = request.POST.get('address')  
            work_name = request.POST.get('work_name')  
            work_typeMar = request.POST.get('work_type') 
            dept_nameMar = request.POST.get('dept_name') 
            districtEng = request.POST.get('district') 
            dataOfYear = request.POST.get('dataOfYear')
            
            # print(remark)
            #print(date_recorded)
            # print(time_recorded)
            # print(address)
            # print(work_name)
            # print(work_type)
            # print(dept_name)
            #print(districtEng)
            # print(dataOfYear)
            dataIgnore={
            'status':1,
            'lat':latitude,
            'lng':longitude,
            'work_type':work_typeMar
            } 
            
            if(latitude=='null'):
                print("LAT NULL")
                return JsonResponse(dataIgnore)
            if(longitude=='null'):
                print("LAT NULL")
                return JsonResponse(dataIgnore)    
            # print("Latitude,longitude:--") 
            # print(latitude)
            # print(longitude)
            dataFail={
            'status':-1,
            'lat':latitude,
            'lng':longitude,
            'work_type':work_typeMar
            } 

            lat = "{0:.14f}".format(float(latitude))
            lng = "{0:.14f}".format(float(longitude)) 
            
            try:
                date_recorded = datetime.datetime.strptime(date_recorded, "%d%m%Y").date()  #if(dataOfYear=="2016-17"):
                time_recorded = datetime.datetime.strptime(time_recorded, '%H%M%S').time()            
                #date_recorded = datetime.datetime.strptime(date_recorded, "%Y-%m-%d").date() 2015-16
                #time_recorded = datetime.datetime.strptime(time_recorded, '%H:%M:%S.%f').time()
            except Exception as e:
                print(str(e))
                print(lat+", "+lng)
                print(date_recorded)
                print(time_recorded)
                
            
            
            work_type=None
            dept_name=None
            district=None
            if(len(work_typeMar)>0):       
                try:
                    work_type = WorkType.objects.get(marathi_name=work_typeMar)
                except WorkType.DoesNotExist:                 
                    print("Exception: WorkType - "+  work_typeMar +" does not exist")                 
                    return JsonResponse(dataFail)

            if(len(dept_nameMar)>0):
                try:               
                    dept_name = DeptName.objects.get(marathi_name=dept_nameMar)
                except DeptName.DoesNotExist:                 
                    print("Exception: DeptName - "+ dept_nameMar +" Does not exist")
                    return JsonResponse(dataFail)

            if(len(districtEng)>0): 
                try:
                    print(districtEng)
                    district = DistrictName.objects.get(english_name=districtEng)
                except DistrictName.DoesNotExist:                
                    print("Exception: DistrictName Does not exist")                 
                    return JsonResponse(dataFail)
            try:        
                jsmappedwork = JSMappedWorks(latitude=lat,\
                                longitude=lng,\
                                remark=remark,\
                                date_recorded=date_recorded,\
                                time_recorded=time_recorded,\
                                address=address,\
                                work_name=work_name,\
                                work_type=work_type,\
                                dept_name=dept_name,\
                                district=district,\
                                dataOfYear=dataOfYear,\
                                is_marked=False)
                
                #Uncomment below to start saving
                #jsmappedwork.save()            
                data={
                'status':1
                }                    
                return JsonResponse(data)
            except Exception as e:
                print(str(e))

                # print("Exception Fired while saving to db")



                            
            data={
                'status':1
            }                    
            return JsonResponse(data)
        except Exception as e:
                print(str(e))
                print(e)
                print(latitude+", "+longitude)
                print(type(longitude))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
        return JsonResponse(data)

'''
def fillWorkTypeTable(request):
    template = loader.get_template('Gmapv2/testCode.html');
    totalWorkType = len(WORKTYPE_MARATHI);
    for i in range(0,totalWorkType):
        worktype = WorkType(marathi_name=WORKTYPE_MARATHI[i],english_name=WORKTYPE_ENGLISH[i]) 
        worktype.save()
    context = {  
       'status': 'success'
    }    
    return HttpResponse(template.render(context, request))     

def fillDeptNameTable(request):
    template = loader.get_template('Gmapv2/testCode.html');
    totalDeptName = len(DEPTNAME_MARATHI);
    for i in range(0,totalDeptName):
        deptname = DeptName(marathi_name=DEPTNAME_MARATHI[i]) 
        deptname.save()
    context = {  
       'status': 'success'
    }    
    return HttpResponse(template.render(context, request)) 

def fillDistrictTable(request):
    template = loader.get_template('Gmapv2/testCode.html');
    totalDistricts = len(DISTRICTNAME_MARATHI);
    for i in range(0,totalDistricts):
        district = DistrictName(marathi_name=DISTRICTNAME_MARATHI[i],english_name=DISTRICTNAME_ENGLISH[i]) 
        district.save()
    context = {  
       'status': 'success'
    }    
    return HttpResponse(template.render(context, request)) 
'''