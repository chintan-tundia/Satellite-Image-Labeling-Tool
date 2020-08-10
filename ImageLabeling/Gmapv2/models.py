from django.db import models

# class Marker(models.Model):
#      latitude = models.DecimalField(max_digits=15,decimal_places=8)
#      longitude = models.DecimalField(max_digits=15,decimal_places=8)
#      marked_date = models.DateTimeField(auto_now_add=True, blank=True)



class Image(models.Model):
    image_name = models.CharField(max_length=100) #District_Locality_Lat_Long.png(Akola_Balapur_20.688889_76.789942.png)
    captured_date = models.DateTimeField(auto_now_add=True, blank=True)
    image_location = models.CharField(max_length=300) #Store parent directory
    image_height = models.DecimalField(max_digits=5,decimal_places=0)
    image_width = models.DecimalField(max_digits=5,decimal_places=0)
    is_annotated = models.BooleanField(default=False)
    centerLatitude = models.DecimalField(max_digits=15,decimal_places=8,default=None) 
    centerLongitude = models.DecimalField(max_digits=15,decimal_places=8,default=None)
    is_approved = models.BooleanField(default=True)
    zoom_level = models.DecimalField(max_digits=3,decimal_places=0,default=None, null=True) 
    derived_from_image = models.ForeignKey('self', on_delete=models.SET_NULL,blank=True,null=True)
     

class GMapMarker(models.Model):
    source_image = models.ForeignKey(Image, on_delete=models.CASCADE,blank=True,null=True)    
    marked_date = models.DateTimeField(auto_now_add=True, blank=True)    
    locality = models.CharField(max_length=50,default=None) 
    district = models.CharField(max_length=50,default=None) 
    geometryJSON = models.TextField()
    #geom = models.geometry
    ground_truthing_done = models.BooleanField(default=False)



class Annotation(models.Model):
    source_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    class_label = models.CharField(max_length=200,blank=True)
    annotation_date = models.DateTimeField(auto_now_add=True, blank=True)
    geometryJSON = models.TextField()



#Web Scraped data
class WorkType(models.Model):
    marathi_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
class DeptName(models.Model):
    marathi_name = models.CharField(max_length=50)    

class DistrictName(models.Model):
    marathi_name = models.CharField(max_length=50)
    english_name = models.CharField(max_length=50)

class JSMappedWorks(models.Model):
    latitude = models.DecimalField(max_digits=20,decimal_places=15,default=None, null=True) 
    longitude = models.DecimalField(max_digits=20,decimal_places=15,default=None,  null=True) 
    remark = models.TextField(blank=True, null=True)
    date_recorded = models.DateField(blank=True, null=True)    
    time_recorded = models.TimeField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    work_name = models.TextField(blank=True, null=True)
    work_type = models.ForeignKey(WorkType, on_delete=models.SET_NULL, null=True)
    dept_name = models.ForeignKey(DeptName, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(DistrictName, on_delete=models.SET_NULL, null=True)
    dataOfYear = models.CharField(max_length=10,default=None) #2015-16,2016-17,2017-18,2018-19
    is_marked = models.BooleanField(null=True)
    #photoname = models.TextField(blank=True, null=True)

class JSMappedWorksImage(models.Model):
    jsmappedwork = models.ForeignKey(JSMappedWorks, on_delete=models.SET_NULL, null=True)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    mapped_date = models.DateTimeField(auto_now_add=True, blank=True)

#addMarker(lat,lng,remark,date,photoname,work_name,work_code,work_type)
#addMarker(19.49444776,73.81622249,"","2015-05-23 13:22:50.0","357089057499818_23052015_132320","सावरकुटे ठिबक सिंचन अविनाश हरी फटांगरे डाळींब","5","ठिबक सिंचन");
#addMarker(lat, lng, img1_s, img2_s, img1_i, img2_i, img1_c, img2_c, workname, workcode, worktype, deptname, asscode)
#addMarker("19.506483333333332", "73.76638666666666", "null", "null", "null", "null", "861116033439334_24062017_170724", "861116033439334_24062017_170753", "सामुदायिक", "557163AG071", "गॅबियन बंधारे", "कृषि", "WC07");
#addMarker(lat, lng, img1_s, img2_s, img1_i, img2_i, img1_c, img2_c, workname, workcode, worktype, deptname, asscode)
#addMarker("null", "null", "null", "null", "866248037765029_16062018_151339", "null", "null", "null", "सामुदायिक", "4208N01AG025", "सलग समतल चर", "कृषि", "WC02");
#addMarker(lat, lng, img1_s, img2_s, img1_i, img2_i, img1_c, img2_c, workname, workcode, worktype, deptname)
#addMarker("19.444574508816004", "74.37740854918957", "null", "null", "null", "null", "354741088027488_12062019_124604", "null", "सामुदायिक", "4202N01GS941", "जलभंजक ", "भुजल सर्वेक्षण व विकास यंत्रणा");


#Split date and time
#Get Address from geocode api



