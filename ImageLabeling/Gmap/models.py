from django.db import models

# class Marker(models.Model):
#      latitude = models.DecimalField(max_digits=15,decimal_places=8)
#      longitude = models.DecimalField(max_digits=15,decimal_places=8)
#      marked_date = models.DateTimeField(auto_now_add=True, blank=True)



class Image(models.Model):
    image_name = models.CharField(max_length=100)
    captured_date = models.DateTimeField(auto_now_add=True, blank=True)
    image_location = models.CharField(max_length=300)
    image_height = models.DecimalField(max_digits=5,decimal_places=0)
    image_width = models.DecimalField(max_digits=5,decimal_places=0)
    is_annotated = models.BooleanField(default=False)

class GMapMarker(models.Model):
     source_image = models.ForeignKey(Image, on_delete=models.CASCADE,blank=True,null=True)
     latitude = models.DecimalField(max_digits=15,decimal_places=8)
     longitude = models.DecimalField(max_digits=15,decimal_places=8) 
     marked_date = models.DateTimeField(auto_now_add=True, blank=True)    


class Annotation(models.Model):
    source_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    top_left_x = models.DecimalField(max_digits=5,decimal_places=0)
    top_left_y = models.DecimalField(max_digits=5,decimal_places=0)
    bottom_right_x = models.DecimalField(max_digits=5,decimal_places=0)
    bottom_right_y = models.DecimalField(max_digits=5,decimal_places=0)
    class_label = models.CharField(max_length=200,blank=True)
    annotation_date = models.DateTimeField(auto_now_add=True, blank=True)
