from django.contrib import admin
from .models import Image
from .models import GMapMarker
from .models import Annotation

admin.site.register(Image)
admin.site.register(GMapMarker)
admin.site.register(Annotation)



