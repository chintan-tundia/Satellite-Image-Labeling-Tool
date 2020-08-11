from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^ajax/save_image_fps$', views.save_image_fps, name='save_image_fps'),
    url(r'^ajax/save_image_wells$', views.save_image_wells, name='save_image_wells'),
    # url(r'^ajax/save_markers$', views.save_markers, name='save_markers'),
    # url(r'^ajax/save_annotations$', views.save_annotations, name='save_annotations'),
    url(r'^ajax/get_annotations$', views.get_annotations, name='get_annotations'),
    url(r'^ajax/save_js_data_to_db$', views.saveJSDataToDb, name='saveJSDataToDb'),
    url(r'^ajax/get_jsmapped_work$', views.get_jsmappedwork_district_wise, name='get_jsmappedwork_district_wise'),
    url(r'^ajax/delete_image_and_annotations$', views.deleteImage, name='deleteImage'),
    url(r'^ajax/approve_image$', views.approveImage, name='approveImage'),
    url(r'^ajax/get_image_list$', views.getImageList, name='getImageList'),
    # url(r'^ImageLabelingTool$', views.label_image, name='label_image'),
    # # url(r'^LoadMarkersCSV$', views.load_markers_from_csv, name='load_markers_from_csv'), 
    # # url(r'^LoadImagesDB$', views.load_images_into_db, name='load_images_into_db'),       
	url(r'^showmarkerscheckdams$', views.show_all_markers_cd, name='show_all_markers_cd'),
    url(r'^showmarkersfarmponds$', views.show_all_markers_fp, name='show_all_markers_fp'),
    url(r'^showmarkerswells$', views.show_all_markers_wells, name='show_all_markers_wells'),
	url(r'^displayimagescheckdams$', views.displayImagesCD, name='displayImagesCD'),
    url(r'^displayimagesfarmponds$', views.displayImagesFP, name='displayImagesFP'),
    url(r'^displayimageswells$', views.displayImagesWells, name='displayImagesWells'),
    url(r'^testLoading$', views.testLoading, name='testLoading'),
	url(r'^labelcheckdams$', views.labelCheckDams, name='labelCheckDams'),
    url(r'^labelfarmponds$', views.labelFarmPonds, name='labelFarmPonds'),
    url(r'^labelwells$', views.labelWells, name='labelWells'),
	url(r'^checkFPat19$', views.checkFPat19, name='checkFPat19'),
    url(r'^checkArea$', views.checkArea, name='checkArea'),
    url(r'^ajax/getmarkerfromid$', views.getMarkerFromId, name='getMarkerFromId'),        
    url(r'^downloaddatasetwells$', views.downloadDatasetWells, name='downloadDatasetWells'),
    url(r'^downloaddatasetwellscsv$', views.downloadDatasetWellsCSV, name='downloadDatasetWellsCSV'),
    url(r'^downloaddatasetwellscustom1$', views.downloadDatasetWellsCustom1, name='downloadDatasetWellsCustom1'),
    url(r'^downloaddatasetfarmponds$', views.downloadDatasetFP, name='downloadDatasetFP'),
    url(r'^downloaddatasetfarmpondsyolo$', views.downloadDatasetFPYOLO, name='downloadDatasetFPYOLO'),
    url(r'^downloaddatasetfarmpondsyolodet$', views.downloadDatasetFPYOLODetection, name='downloadDatasetFPYOLODetection'),
    url(r'^downloaddatasetfarmpondscoco$', views.downloadDatasetFPCOCO, name='downloadDatasetFPCOCO'),
    url(r'^downloaddatasetfarmpondscsv$', views.downloadDatasetFPCSV, name='downloadDatasetFPCSV'),
    url(r'^downloaddatasetfarmpondscustom1$', views.downloadDatasetFPCustom1, name='downloadDatasetFPCustom1'),
    
    
    
    #url(r'^loadWorkType$', views.fillWorkTypeTable, name='fillWorkTypeTable'),
    #url(r'^loadDeptName$', views.fillDeptNameTable, name='fillDeptNameTable'),
    #url(r'^loadDistrict$', views.fillDistrictTable, name='fillDistrictTable'),
    #url(r'^ExtractFPs$', views.extractFPs, name='extractFPs'),
]


