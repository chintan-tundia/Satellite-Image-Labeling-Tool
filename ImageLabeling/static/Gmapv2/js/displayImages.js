{% load static %} 
var imageList = document.getElementById("imageList")
var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");
var imageListIndex=0;
canvas.width = 640;
canvas.height = 640;

function setCanvasBackground()
{
	var background = new Image();
    var txtAnn = document.getElementById("is_annotated");
	selectedImgName=imageList.options[imageListIndex].innerHTML;
    txtAnn.innerHTML=imageList.options[imageListIndex].getAttribute('data');
	var image_path="{% static '/Gmapv2/images/'%}"+selectedImgName;        
	background.src = image_path;
	// Make sure the image is loaded first otherwise nothing will draw.
	background.onload = function(){
	    ctx.drawImage(background,0,0);   
	    var canvasImg = canvas.toDataURL(); 
	    var hidden = document.getElementById("canvasImg64");
        hidden.value=canvasImg;

        var canvas1 = document.getElementById('canvas');
        var ctx1 = canvas.getContext('2d');

        $.ajax({
            type:"POST",
                url: 'ajax/get_annotations',
                data: {                
                    'image_name': selectedImgName               
                },
                dataType: 'json',
                success: function (data) {                
                    annots=data.annotations;
                    console.log(annots)
                    var wfpl="Wet Farm Pond - Lined";
                    var wfpu="Wet Farm Pond - Unlined";
                    var dfpl="Dry Farm Pond - Lined";
                    var dfpu="Dry Farm Pond - Unlined";
                    if (annots==-1) {
                      alert("Image not in database");                                             
                    }
                    else{                            
                        annotsp=JSON.parse(annots)   
                        /*if(annotsp.length<=0){
                            document.getElementById("btnSave").disabled = false;
                        } 
                        else{
                            document.getElementById("btnSave").disabled = false; 
                        } */                       
                        for(i=0;i<annotsp.length;i++){
                            ctx.lineWidth = 3;
                            if(annotsp[i].class_label==wfpl){
                                ctx.strokeStyle = "cyan";
                                ctx.fillStyle = "rgba(00,255,255,0.2)";
                                ctx.lineWidth = 2;
                                // ctx.strokeRect(annotsp[i].top_left_x, annotsp[i].top_left_y, annotsp[i].width, annotsp[i].height)
                            } 
                            if(annotsp[i].class_label==wfpu){
                                ctx.strokeStyle = "green";
                                ctx.fillStyle = "rgba(00,255,00,0.2)";
                                ctx.lineWidth = 2;
                                // ctx.strokeRect(annotsp[i].top_left_x, annotsp[i].top_left_y, annotsp[i].width, annotsp[i].height)
                            } 
                            if(annotsp[i].class_label==dfpl){
                                ctx.strokeStyle = "red";
                                ctx.fillStyle = "rgba(255,00,00,0.2)";
                                ctx.lineWidth = 2;
                                // ctx.strokeRect(annotsp[i].top_left_x, annotsp[i].top_left_y, annotsp[i].width, annotsp[i].height)
                            } 
                            if(annotsp[i].class_label==dfpu){
                                ctx.strokeStyle = "yellow";
                                ctx.fillStyle = "rgba(255,255,00,0.2)";
                                ctx.lineWidth = 2;
                                // ctx.strokeRect(annotsp[i].top_left_x, annotsp[i].top_left_y, annotsp[i].width, annotsp[i].height)
                            } 

                            ctx.beginPath();
                            geometryJSON=JSON.parse(annotsp[i].geometryJSON)
                            var pixCoords=geometryJSON.pixelCoords;
                            var totalPts=geometryJSON.pixelCoords.length;
                            ctx.moveTo(pixCoords[0].x, pixCoords[0].y);
                            for(pt=1;pt<totalPts;pt++){         
                                ctx.lineTo(pixCoords[pt].x, pixCoords[pt].y);   
                                ctx.stroke(); 
                            }                                           
                            ctx.lineTo(pixCoords[0].x, pixCoords[0].y);   
                            ctx.stroke(); 
                            ctx.closePath();
                            ctx.fill();

                        }
                        
                    }
                },         
                error: function(xhr, textStatus, errorThrown) {
                    console.log(errorThrown)
                    alert("Something went wrong.");
                }
        });
                
        


	}
	
	var nameEle = document.getElementById("imageName");
    nameEle.value=selectedImgName;
}
function initialize()
{
	loadImageNames()
	setCanvasBackground()
	listenKeyboard()
}

function loadImageNames()
{
	
	let i=0;
	//let imgName="";
	let option=null;

	{% for img in images %}   
		var imgName="{{ img.image_name }}";
        isAnnotated="{{ img.is_annotated }}";
		option = document.createElement("option");
		option.value = imgName;
        option.innerHTML = imgName;
        if(isAnnotated=="True"){
            option.setAttribute('data',"Yes")
        }
        else{
            option.setAttribute('data',"No")   
        }            
        if (i === 0) {
        	option.selected = true
        }
    	imageList.appendChild(option);
   		i++;
	{% endfor %} 
	imageList.addEventListener("change", () => {
        imageListIndex = imageList.selectedIndex
        setCanvasBackground()            
    }) 

}
function b64()
{
	var canvastemp = document.getElementById('canvas');
	alert(canvastemp.toDataURL())

}
const listenKeyboard = () => {
    const imageList = document.getElementById("imageList")
    const classList = document.getElementById("classList")

    document.addEventListener("keydown", (event) => {
        const key = event.keyCode || event.charCode            

        if (key === 37) {
            if (imageList.length > 1) {
                imageList.options[imageListIndex].selected = false

                if (imageListIndex === 0) {
                    imageListIndex = imageList.length - 1
                } else {
                    imageListIndex--
                }

                imageList.options[imageListIndex].selected = true
                imageList.selectedIndex = imageListIndex

                setCanvasBackground() 
                document.body.style.cursor = "default"
            }

            event.preventDefault()
        }

        if (key === 39) {
            if (imageList.length > 1) {
                imageList.options[imageListIndex].selected = false

                if (imageListIndex === imageList.length - 1) {
                    imageListIndex = 0
                } else {
                    imageListIndex++
                }

                imageList.options[imageListIndex].selected = true
                imageList.selectedIndex = imageListIndex

               setCanvasBackground() 

                document.body.style.cursor = "default"
            }

            event.preventDefault()
        }
        
    })
}
initialize();