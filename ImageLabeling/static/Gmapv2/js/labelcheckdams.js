
//Global variable Initializations
	var markers = [];
  var allOldMarkers = [];
	var latlng;
  var selectedShape;  
  var allObjects={};
  var totalObjects=0;
  var allIds=[];
  allLocs=[];
  var workTypeIds=[];
  var drawingManager;
  var zoomLevel=19;  
  var vlat = 19.859317;
  var vlong = 75.516106;//Somewhere in Kubephal,Aurangabad
  //initialize(vlat,vlong); 


/*-------Functions--------*/  
	function initialize(vlat,vlong){  
        var vlat = 19.859317;
		var vlong = 75.516106;
        $('#btnPolygon').hide() 
        $('#btnCircle').hide() 
        $('#btnReset').hide()
        $('#inform').hide()     
        
        //var latlng = new google.maps.LatLng(19.910915, 73.876757);
        latlng = new google.maps.LatLng(vlat,vlong);		
        var myOptions = {
            zoom: 19,
            center: latlng,
            disableDefaultUI: true,
            mapTypeId: google.maps.MapTypeId.SATELLITE,
            scaleControl: true            
        };        
        map = new google.maps.Map(document.getElementById("googleMap"), myOptions); 
        drawingManager = new google.maps.drawing.DrawingManager({
          drawingMode: google.maps.drawing.OverlayType.MARKER,
          drawingControl: true,
          drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_CENTER,
            //drawingModes: ['marker', 'circle', 'polygon', 'polyline', 'rectangle']
            drawingModes: ['circle','polygon','rectangle']
          },          
          circleOptions: {
            fillColor: 'transparent',
            fillOpacity: 0.4,
            strokeColor:'black',
            strokeWeight: 2,
            clickable: true,
            editable: true,
            zIndex: 1
          },
          polygonOptions: {
            fillOpacity:0,
            //fillColor: '#e6dc03',
            fillColor: 'transparent',
            strokeWeight: 1,
            clickable: true,
            draggable:true,
            editable: true,
            zIndex: 1

          },
          rectangleOptions: {
            fillOpacity:0.4,
            fillColor: '#e6dc03',
            strokeWeight: 1,
            clickable: true,
            draggable:true,
            editable: true,
            zIndex: 1

          }

        });
        //drawingManager.setMap(map);
        // Newly defined                  
        $('#btnCircle').click(function(){                 
          drawingManager.setOptions({
              drawingMode : google.maps.drawing.OverlayType.CIRCLE,
              drawingControl : true,
              drawingControlOptions : {
                  position : google.maps.ControlPosition.TOP_CENTER,
                  drawingModes : [google.maps.drawing.OverlayType.CIRCLE]
              }
          })
          drawingManager.setMap(map);
        })
        $('#btnRectangle').click(function(){          
          drawingManager.setOptions({
              drawingMode : google.maps.drawing.OverlayType.RECTANGLE,
              drawingControl : true,
              drawingControlOptions : {
                  position : google.maps.ControlPosition.TOP_CENTER,
                  drawingModes : [google.maps.drawing.OverlayType.RECTANGLE]
              }
          })
          drawingManager.setMap(map);
        })
        $('#btnPolygon').click(function(){          
          drawingManager.setOptions({
              drawingMode : google.maps.drawing.OverlayType.POLYGON,
              drawingControl : true,
              drawingControlOptions : {
                  position : google.maps.ControlPosition.TOP_CENTER,
                  drawingModes : [google.maps.drawing.OverlayType.POLYGON]
              }
          })
          drawingManager.setMap(map);
          $('#btnPolygon').addClass("disabled");
        })
        
        
        google.maps.event.addListener(drawingManager, 'overlaycomplete', function(e) {
            if (e.type != google.maps.drawing.OverlayType.MARKER) {
                // Switch back to non-drawing mode after drawing a shape.
                drawingManager.setDrawingMode(null);
                // To hide:
                //drawingManager.setOptions({
                // drawingControl: false
                //});

                // Add an event listener that selects the newly-drawn shape when the user
                // mouses down on it.          
                var newShape = e.overlay;
                newShape.type = e.type; 
                //var totalObjects=Object.keys(allObjects).length
                var objNo=totalObjects++;                
                var idName="obj"+objNo
                var idSelect="sel"+objNo
                google.maps.event.addListener(newShape, 'click', function() {                  
                  setSelection(newShape,idName);
                });
                setSelection(newShape,idName);
                
                allObjects[idName]=newShape
                //allObjects.push(newShape)
                allIds.push(idName)
                
                //Adding label
                var ptsStr=getPoints(newShape)
                var dropdownStr="<form><div class='form-group'>"+ 
                                  //"<p>"+ptsStr+"</p><br>"+                 
                                  "<select id='"+idSelect+"' class='form-control'>"+
                                    "<option>Select Class</option>"+
                                    "<option>Wall Based Checkdam</option>"+
                                    "<option>Gate Based Checkdam</option>"+                    
                                  "</select>"+         
                                "</div></form>";
                var htmlCont="<div id='"+idName+"' class='panel panel-info'>"+
                                "<div class='panel-heading'>"+
                                   "<b> Annotation "+(objNo+1)+"</b>"+
                                 "</div>"+
                                 "<div class='panel-body'>"+dropdownStr+                                    
                                    "<a id='btnDelete' type='button' class='btn btn-danger'>"+
                                    "<span class='glyphicon glyphicon-minus-sign'></span>"+
                                    " Remove Annotation"+
                                    "</a>"+
                                 "</div>"+
                              "</div>";
                $("#annotations").append(htmlCont);
                $('#btnPolygon').removeClass("disabled");
            }
        });
        google.maps.event.addListener(drawingManager, 'drawingmode_changed', clearSelection)
        google.maps.event.addListener(map, 'click', clearSelection);
        $('#SelDistrict  option:contains("Akola")').attr  ('selected', 'selected');
        var districtName=$('#SelDistrict option:selected').val()   
        var dataOfYear=$('#SelYear option:selected').val() 
        getJSMappedWorksDistrictAjax(districtName,dataOfYear)
        
  }  
  function clearSelection() {
      if (selectedShape) {
        if (selectedShape.type !== 'marker') {
            selectedShape.setEditable(false);
        }
        selectedShape = null;
        //var totalObjects=allObjects.length
        for (var key in allObjects) {
          //$('#obj'+key).attr('class', 'panel panel-default');  
          $('#'+key).attr('class', 'panel panel-default');  
        }
        // for(i=0;i<totalObjects;i++)
        // {          
        //   $('#obj'+i).attr('class', 'panel panel-default');
        // }
      }
  }

  function setFocusOnShape(index){    
    //var totalObjects=allObjects.length     
    //console.log("Selected:"+index)
    for (var key in allObjects) {        
        if(key==index){
        
          $('#'+key).attr('class', 'panel panel-info');
        }
        else{          
          $('#'+key).attr('class', 'panel panel-default');
        }
    }        
  }
  function setSelection(shape,index) {
      clearSelection();
      shape.setEditable(true);
      selectedShape = shape;       
      setFocusOnShape(index)                   
      //selectColor(shape.get('fillColor') || shape.get('strokeColor'));
  }
  function getPoints(selectedShp){
    if (selectedShp) {
          if(selectedShp.type == google.maps.drawing.OverlayType.RECTANGLE)
          {
            bounds=selectedShp.getBounds()
            ne=bounds.getNorthEast()
            sw=bounds.getSouthWest()
            var north= ne.lat().toFixed(8);
            var east=ne.lng().toFixed(8);
            var south=sw.lat().toFixed(8);
            var west=sw.lng().toFixed(8);
            //neLat=radians(ne.lat())
            //neLng=radians(ne.lng())
            //$('#dispText').html("North East :"+ne+"<br> South West:"+sw)
            var str="Points:("+north+","+west+")"+",("+north+","+east+"),("+south+","+east+"),("+south+","+west+")"
            return str;
          }
          if(selectedShp.type == google.maps.drawing.OverlayType.POLYGON)
          {
            var path=selectedShp.getPath()
            var len=path.getLength()
            var dispText=""
            // for(var i=0;i<len;i++)
            // {
            //   pair=path.getAt(i)
            //   dispText+="("+i+"): ("+pair.lat().toFixed(8)+", "+pair.lng().toFixed(8)+")<br>"
            // }
            //var area=google.maps.geometry.spherical.computeArea(path).toFixed(2)
            //dispText+="Area: "+area+" sq.m"
            return dispText;
            //$('#dispText').html(dispText)

          }
          if(selectedShp.type == google.maps.drawing.OverlayType.CIRCLE)
          {
            var center=selectedShp.getCenter()
            var radius=selectedShp.getRadius()
            var area=(radius*radius*Math.PI).toFixed(2)
            var str="Center: ("+center.lat().toFixed(8)+", "+center.lng().toFixed(8)+")<br>Radius: "+radius.toFixed(2)+"m<br>Area: "+area+" sq.m"
            //$('#dispText').html("Center : "+center+"<br>Radius : "+radius)
            return str;
          }    
        }  
  }

  //For setting map based on lat long
  function latlngchng(){
  		var latlngtext=$('#inp_latlng').val()
  		var str_array = latlngtext.split(',');
  		var vlat=str_array[0] 
  		var vlong=str_array[1]  
  		latlng = new google.maps.LatLng(vlat,vlong);
  		map.setCenter(latlng);
  		//initialize(vlat, vlong);
  }
  function searchPlace(){
  	var place=$('#inp_place').val()  	
  	var request = {
          query: place,
          fields: ['name', 'geometry'],
        };

    service = new google.maps.places.PlacesService(map);

    service.findPlaceFromQuery(request, function(results, status) {    	
       if (status === google.maps.places.PlacesServiceStatus.OK) {
            // for (var i = 0; i < results.length; i++) {
            //   createMarker(results[i]);
            // }            
            map.setCenter(results[0].geometry.location);
       }
    });
  } 
  function mercY(lat) { return Math.log(Math.tan(lat/2 + Math.PI/4)); }
  function radians(degrees){ return degrees * Math.PI / 180; }
  function degrees(radians){ return radians * 180 / Math.PI; }

  function getPixelCoords(slat,slng){
    lat=radians(slat)
    lon=radians(slng)
    
    var south = radians(map.getBounds().getSouthWest().lat());
    var north = radians(map.getBounds().getNorthEast().lat());
    var west = radians(map.getBounds().getSouthWest().lng());
    var east = radians(map.getBounds().getNorthEast().lng());

    // This also controls the aspect ratio of the projection
    width = 640;
    height = 640;

    // Formula for mercator projection y coordinate:
    

    // Some constants to relate chosen area to screen coordinates
    ymin = mercY(south);
    ymax = mercY(north);
    xFactor = width/(east - west);
    yFactor = height/(ymax - ymin);

    // function mapProject($lat, $lon) { // both in radians, use deg2rad if neccessary        
    x = lon;
    y = mercY(lat);
    x = (x - west)*xFactor;
    y = (ymax - y)*yFactor; // y points south
    return new Array(x, y);
    // }
  }
  function freezeMap(){
          zoomLevel=map.getZoom();
          map.setOptions({gestureHandling:"none"})
          map.setOptions({mapTypeId: google.maps.MapTypeId.SATELLITE})
          var southpt = map.getBounds().getSouthWest().lat()
          var northpt = map.getBounds().getNorthEast().lat()
          var westpt = map.getBounds().getSouthWest().lng()
          var eastpt = map.getBounds().getNorthEast().lng()            
          
          // console.log("North:"+northpt);
          // console.log("West:"+westpt);
          // console.log("South:"+southpt);
          // console.log("East:"+eastpt);
          
          var restrictionJson = {
            restriction: { 
            latLngBounds: {north:northpt , south:southpt , west:westpt , east:eastpt },
            strictBounds: true,
            }
          }
          map.setOptions(restrictionJson)
          $('#inform').show()
  }
  function unFreezeMap(){
    map.setOptions({gestureHandling:"auto"})
    var restrictionJson = {
      restriction: {
        latLngBounds:{north:89.97835325843884 , south:-89.90858218066927 , west:-180 , east:180},
        strictBounds: false,
      }
    }
    map.setOptions(restrictionJson)
  }
  function getJSMappedWorksDistrictAjax(districtName,dataOfYear){
    $('#SelDistrictLoc').empty()
    $('#total_samples').text("0");
    $('#total_done_samples').text("0");
    $('#percentage').text("0%");
    $('#total_img_district').text("0");
    $.ajax({
            type:"POST",
                url: 'ajax/get_jsmapped_work',
                data: {
                    'districtName':districtName,
                    'workType':'checkdams',
                    'dataOfYear':dataOfYear                   
                },
                dataType: 'json',
                success: function (data) {                
                    if (data.status==1) {
                       
                        var json_jsmapped_list = data.records;
                        var Arrjsmapped=JSON.parse(json_jsmapped_list);
                        //console.log(Arrjsmapped[0]['fields'])                        
                        var total=Arrjsmapped.length
                        allLocs=[];  						
                        for(var i=0;i<total;i++){
                          //var fieldll = jsmapped.fields;
                          //console.log(Arrjsmapped[i]['fields'])
                          var loc=[];
                          var lat=Arrjsmapped[i]['fields']['latitude'];
                          loc.push(lat)
                          var lat=parseFloat(lat).toFixed(8);
                          var lng=Arrjsmapped[i]['fields']['longitude'];
						  var worktypeid=Arrjsmapped[i]['fields']['work_type'];
                          loc.push(lng)
						  loc.push(worktypeid)
                          var lng=parseFloat(lng).toFixed(8);
                          var str = '<option value="'+i+'">'+lat+' , '+lng+'</option>';
                          $('#SelDistrictLoc').append(str); 
                          allLocs.push(loc)						  						  
                          var perc=parseFloat(data.done_percentage).toFixed(2) + "%"                                                    
                          $('#total_samples').text(data.total_samples);
                          $('#total_done_samples').text(data.total_done_samples);
                          $('#percentage').text(perc);
                          $('#total_img_district').text(data.total_img_district);
                          $('#SelDistrictLoc :nth-child(1)').prop('selected', true);
                          $('#SelDistrictLoc').trigger('change');
                        }
                    }                                      
                },
                error: function(xhr, textStatus, errorThrown) {
                alert("Something went wrong.");
              }
        });

  }
  function resetMapCanvas(){
    //unFreezeMap();
    //var totalIds=allIds.length
    //var totalObjects=allObjects.length
    $('#annotations').empty()
    for (var key in allObjects) {
      selShp=allObjects[key];
      selShp.setMap(null);
    }
    /*for(i=0;i<totalObjects;i++){
      selShp=allObjects[i];
      selShp.setMap(null);
    }*/
    allObjects={};
    allIds=[];
    totalObjects=0;    
    drawingManager.setOptions({drawingControl: false});
    $('#btnPolygon').removeClass("disabled");
    drawingManager.setMap(null);
    $('#btnPolygon').hide()
    $('#btnCircle').hide()
    $('#btnReset').hide()
    $('#btnAnnotate').show()
    $('#SelDistrict').prop("disabled", false);
    $('#SelDistrictLoc').prop("disabled", false);
  }
  // Sets the map on all markers in the array.
  /*function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(map);
    }
  }*/    
  // Save markers to database
  /*function saveMarkers(){
    var lat = latlng.lat();
    var lng = latlng.lng(); 
    var locations=[];
    for (var i = 0; i < markers.length; i++) {
        locations.push(markers[i].position);        
      } 
      markers_json=JSON.stringify(locations); 
      alert(markers_json)  
      $.ajax({
        type:"POST",
            url: 'ajax/save_markers',
            data: {                
                'markers': markers_json               
            },
            dataType: 'json',
            success: function (data) {                
                if (data.status==1) {
                  alert("Markers saved");                   
                }
          }         
      });
  }*/

/*-------Functions End--------*/


/*-------Event Listeners--------*/
$(document).ready(function(){
  map.addListener('zoom_changed', function() {
      zoomLevel = map.getZoom();
      $('#zoomLvlTxt').text(zoomLevel);
  });  
  $(document).on('click','.panel',function(){
    var idxStr=this.id;  
    //var idx=idxStr[idxStr.length-1];
    if(idxStr in allObjects){
      //setSelection(allObjects[idx],idx)
      setSelection(allObjects[idxStr],idxStr)
    }
  });
  $(document).on('change','.form-control',function(){ 
    if(this.value=="Checkdam"){
      selectedShape.setOptions({fillOpacity:0.3})
      // var divId=this.parentNode.parentNode.parentNode.parentNode.id
      // $('#'+divId).collapse()        
      //selectedShape.setOptions({fillColor:'#13dde8'})      
      selectedShape.setOptions({fillColor:'cyan'})      
    }
  });  
  $(document).on('click','#btnDelete',function(){
    var panelElemId=this.parentNode.parentNode.id;    
    var idx=panelElemId.substring(3, panelElemId.length);          
    $('#'+panelElemId).remove()
    selShp=allObjects[panelElemId]
    if (selShp) {          
      selShp.setMap(null);        
      drawingManager.setOptions({drawingControl: true});
    } 
    if(idx>-1){
      //allObjects.splice(idx,1)
      delete allObjects[panelElemId]
      allIds.splice(idx,1)
    }
  });    
  $('#btnAnnotate').click(function(){
    //freezeMap()      
    $('#btnPolygon').show()
    $('#btnCircle').show()
    $('#btnReset').show()
    $('#btnAnnotate').hide()
    $('#SelDistrict').prop("disabled", true);
    $('#SelDistrictLoc').prop("disabled", true);
  })
  $('#btnReset').click(function(){        
    resetMapCanvas()    ;
  })
  $("#btnSave").click(function(e){      
    //var totalObj=allObjects.length
    var totalObj=Object.keys(allObjects).length    
    var zoomLevel = map.getZoom();
    var okFlag = true;
    var zoomFlag = true;
    if(zoomLevel!=19){
      alert("Set Zoom Level to 19 and save.");      
      zoomFlag=false;
      return;
    }
    if(totalObj<=0){
      var txt;
      var r = confirm("There are no annotations. Are you sure you want to save anyways?");
      if (r == false) {
        okFlag = false;
        return;
      }
    }

    if(zoomFlag==true && okFlag==true){
          //Get Freezed Map Bounds   
          var centerLat = map.getCenter().lat().toFixed(8);
          var centerLng = map.getCenter().lng().toFixed(8);
          var mapBounds = map.getBounds()
          var ne=mapBounds.getNorthEast();
          var sw=mapBounds.getSouthWest();
          var topLeftLat = sw.lat().toFixed(8);
          var topLeftLng = ne.lng().toFixed(8);
          var bottomRightLat = ne.lat().toFixed(8);
          var bottomRightLng = sw.lng().toFixed(8);
          var zoomLevel = map.getZoom().toFixed(8);		  
          var groundTruthingDone = true;
          var selectedClass;
          var jsonGmapMarker='';
          var jsonAnnotations='';
          //Get all annotations.
         
          var flag=1;
          var finalJson='';
          var finalArray=[];
          var arrAnnotations=[];
          var arrGmapMarker=[];
          //for(i=0;i<totalObj;i++)
          var i=0;
          for (var key in allObjects)  
          {       
            //var idxStr=allIds[i];
            var idxStr=key;
            var idx=idxStr.substring(3, idxStr.length);;                    
            selectedClass=$('#sel'+idx).val();
            if(selectedClass=='Select Class'){
              flag=0;
              alert("Please select class for each annotation.");
              break;
            }
            else{          
              //var currentShape = allObjects[i];
              var currentShape = allObjects[key];
              path=currentShape.getPath();
              var len = path.getLength();
              var lat,lng,latlngPix,lt,ln;
              var arrPixelCoords=[];
              var arrWorldCoords=[];
              for(var j=0;j<len;j++)
              {
                var pixelCoords={};
                var worldCoords={};            
                pair=path.getAt(j);
                lat=pair.lat().toFixed(8);
                lng=pair.lng().toFixed(8);
                latlngPix=getPixelCoords(lat,lng);
                lt=Math.round(latlngPix[0]);
                ln=Math.round(latlngPix[1]);
                pixelCoords["x"] = lt;      
                pixelCoords["y"] = ln;
                worldCoords["lat"] = lat; 
                worldCoords["lng"] = lng;
                arrPixelCoords.push(pixelCoords);
                arrWorldCoords.push(worldCoords);
              }
    
              var annotation = {};
              var gmapmarker = {};
              annotation ["type"] = "polygon";
              gmapmarker ["type"] = "polygon";
              annotation ["objectNo"] = i;
              gmapmarker ["objectNo"] = i;
              annotation ["pixelCoords"] = arrPixelCoords;
              gmapmarker ["worldCoords"] = arrWorldCoords;   
              annotation ["classnm"] = selectedClass;
              gmapmarker ["classnm"] = selectedClass;
              arrAnnotations.push(annotation);
              arrGmapMarker.push(gmapmarker);
            }
            i++;

          }
          
          if(flag){
            finalItem = {}
            var mapCenterArr={};
            mapCenterArr["lat"] = centerLat;      
            mapCenterArr["lng"] = centerLng;            
            finalItem ["mapCenter"] = mapCenterArr;
            finalItem ["annotations"] = arrAnnotations;
            finalItem ["gmapmarker"] = arrGmapMarker;
            finalArray.push(finalItem);
            //arrPixelCoords.push(pixelCoords);
            jsonGmapMarker=JSON.stringify(arrGmapMarker);
            jsonAnnotations=JSON.stringify(arrAnnotations);
            finalJson=JSON.stringify(finalArray);            
          
    
          //District_Locality_Lat_Long.png(Akola_Balapur_20.688889_76.789942.png)
          var filename='';
          var district='';         
          var locality='';
          var latlng   = new google.maps.LatLng(centerLat, centerLng)
          var centerLat=latlng.lat()
          var centerLng=latlng.lng()          
          geocoder = new google.maps.Geocoder();
                
          geocoder.geocode({'latLng': latlng}, function(results, status) {
           if (status == google.maps.GeocoderStatus.OK) {        
             if (results[0]) {
                for (var ac = 0; ac < results[0].address_components.length; ac++) {
                    var component = results[0].address_components[ac];
    
                    switch(component.types[0]) {
                        case 'locality':
                            locality = component.long_name;
                            break;
                        case 'administrative_area_level_2':
                            district = component.short_name;
                            break;
                        // case 'country':
                        //     storableLocation.country = component.long_name;
                        //     storableLocation.registered_country_iso_code = component.short_name;
                        //     break;
                    }
                }
                var district=$('#SelDistrict option:selected').val() //only for JS
                $.ajax({
                  type:"POST",
                      url: 'ajax/save_image_checkdams',
                      data: {
                          'topLeftLat':topLeftLat,
                          'topLeftLng':topLeftLng,
                          'bottomRightLat':bottomRightLat,
                          'bottomRightLng':bottomRightLng,
                          'centerLat':centerLat,
                          'centerLng':centerLng,
                          'zoom':zoomLevel,
                          'district':district, 
                          'locality': locality,                
                          'markersJSON': jsonGmapMarker,
                          'annotationJSON':jsonAnnotations,
                          'groundTruthingDone':groundTruthingDone
                      },
                      dataType: 'json',
                      success: function (data) {                
                          if (data.status==1) {
                            //alert("Image is captured and annotations are saved.");   
                            //var selIndex=$("#SelDistrictLoc").prop('selectedIndex');
                            resetMapCanvas();
                            var districtName=$('#SelDistrict option:selected').val() 
                            var dataOfYear=$('#SelYear option:selected').val()                                 
                            getJSMappedWorksDistrictAjax(districtName,dataOfYear)
                            $('#btnReset').trigger('click');
                            $('#SelDistrictLoc :nth-child(1)').prop('selected', true);
                            $('#SelDistrictLoc').trigger('change');
                            
                          }
                          else if(data.status==-1){
                            alert("File with same name exists. Try some other name.");                
                          }
                          else{
                            alert("Something went wrong.");
                          }
                      },
                      error: function(xhr, textStatus, errorThrown) {
                      alert("Something went wrong.");
                    }
                });      
             }
            else{
              console.log("No reverse geocode results.")
              alert("Something went wrong.[No reverse geocode results]");
            }
           }
           else {
            console.log("Geocoder failed: " + status)
            alert("Something went wrong.[geocoder failed]");
           }
          }); 
        }
    }
    
  });
  $('#SelYear').change(function(e){
    var districtName=$('#SelDistrict option:selected').val()    
    var dataOfYear=$('#SelYear option:selected').val()
    getJSMappedWorksDistrictAjax(districtName,dataOfYear)
  })
  $('#SelDistrict').change(function(e){
    var districtName=$('#SelDistrict option:selected').val()    
    var dataOfYear=$('#SelYear option:selected').val()
    getJSMappedWorksDistrictAjax(districtName,dataOfYear)
  })
  $('#SelDistrictLoc').change(function(e){
    var loc=$('#SelDistrictLoc option:selected').val()
    if(loc){
      var lat=allLocs[loc][0]
      var lng=allLocs[loc][1] 
	  var worktype = allWorkTypes[allLocs[loc][2]-1]
      var ll=new google.maps.LatLng(lat,lng);
      map.setCenter(ll);
	  $('#centerLatLng').text(lat+", "+lng)	  	  	  
	  //var ArrWorktype=JSON.parse(allWorkTypes);	  
	  $('#jsworktype').text(worktype)	  
    }
  })
  map.addListener('center_changed', function() {
      var clatlng=map.getCenter()
      var lat=clatlng.lat()
      var lng=clatlng.lng()
      $('#centerLatLng').text(lat+", "+lng)
    
  });
})  
/*-------Event Listeners End--------*/
