from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^ajax/save_image$', views.save_image, name='save_image'),
    url(r'^ajax/save_markers$', views.save_markers, name='save_markers'),
    url(r'^ajax/save_annotations$', views.save_annotations, name='save_annotations'),
    url(r'^ajax/get_annotations$', views.get_annotations, name='get_annotations'),
    url(r'^ImageLabelingTool$', views.label_image, name='label_image'),
    # url(r'^LoadMarkersCSV$', views.load_markers_from_csv, name='load_markers_from_csv'), 
    # url(r'^LoadImagesDB$', views.load_images_into_db, name='load_images_into_db'),       
    url(r'^showAllMarkers$', views.show_all_markers, name='showAllMarkers'),
    url(r'^DisplayImages$', views.displayImages, name='displayImages'),
    url(r'^ExtractFPs$', views.extractFPs, name='extractFPs'),
]

