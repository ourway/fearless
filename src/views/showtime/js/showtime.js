/*

 Showtime JavaScript RAM Player
 by: Farsheed Ashouri
 originally by John Martini and Shawn Olson

 */



/*Element Vars*/
var canvas;
var context;
var currentWidth = 960;
var currentHeight = 540;
var timeline;

/*Drawing Vars*/
var paint = false;
var paintColor = "#009bff"
var activeTool = "marker"; //marker or eraser
var nibSize = 8;
var opacity = 1;
var nib = new Image();
var nibShape = "circle";//circle or square
var lastMouseX;
var lastMouseY;

/*Control Vars*/
var playInterval;
var fps = 24;
var stopAtNotes = true;
var loop = true;
var sequence = 1;
var manifest;
var allowKBD = true;

/*Image paths*/
var imageUrl = "../images/hideicon.svg";

function pad(num, size) {
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}

var convertDataURL2binaryArray = function(dataURL){

    var blobBin = atob(dataURL.split(',')[1]);
    var array = [];
    for(var i = 0; i < blobBin.length; i++) {
        array.push(blobBin.charCodeAt(i));
    }
    return new Uint8Array(array)
}

/*Draw a Stroke from the last position to the current position.*/
function updateCanvas(thisMouseX, thisMouseY) {

    context.lineWidth = nibSize;
    context.beginPath();
    context.moveTo(lastMouseX, lastMouseY);
    context.lineTo(thisMouseX, thisMouseY);
    context.closePath();
    context.globalAlpha = opacity;


    switch (nibShape) {
        case "square":
            context.lineCap = "square"
            context.lineJoin = "bevel";
            break;
        default:
            context.lineCap = "round";
            context.lineJoin = "round";
    }

    if (activeTool == "eraser") {
        context.globalCompositeOperation = "destination-out";
        context.strokeStyle = 'white';
    } else {
        context.globalCompositeOperation = "source-over";
        context.strokeStyle = paintColor;
    }


    context.stroke();


    context.restore();
    context.globalAlpha = 1;

}

/*Initialize Canvas Event Handlers.*/
function canvasInit() {

    document.getElementById("frame").value = 1;

    canvas = document.getElementById('canvas');
    context = canvas.getContext("2d");

    $('#canvas').mousedown(function (e) {

        lastMouseX = e.pageX - $('#canvas').offset().left;
        lastMouseY = e.pageY - $('#canvas').offset().top;
        paint = true;

        var radius = nibSize / 2;

        if (activeTool == "eraser") {
            context.fillStyle = 'white';

        } else {

            context.fillStyle = paintColor;
        }
        context.globalAlpha = opacity;
        context.beginPath();
        switch (nibShape) {
            case "square":
                context.rect((lastMouseX - (nibSize / 2)), (lastMouseY - (nibSize / 2) ), nibSize, nibSize);
                break;
            default:
                context.arc(lastMouseX, lastMouseY, radius, 0, 2 * Math.PI, false);
        }
        context.fill();

    });

    $('#canvas').mousemove(function (e) {
        if (paint == true) {
            var thisMouseX = e.pageX - $('#canvas').offset().left;
            var thisMouseY = e.pageY - $('#canvas').offset().top;
            updateCanvas(thisMouseX, thisMouseY);
            lastMouseX = thisMouseX;
            lastMouseY = thisMouseY;
        }
        if (e.shiftKey && !project.slave)
        {
            x = e.offsetX;
            percent = x/currentWidth;
            goal = Math.round(project.imgsA.length * percent);
            if (goal != project.currentFrame())
                goToFrame(goal);
        }
    });

    $('#canvas').mouseup(function (e) {
        paint = false;
        updateCanvas();
    });

    $('#canvas').mouseleave(function (e) {
        paint = false;
    });


}


function goToFrame(fr) {
    $("#frame").val(fr * 1);
    project.command = 'goToFrame('+fr+')';
    project.setBackground();
    context.clearRect(0, 0, canvas.width, canvas.height);
    project.getNotes();
    $("#timeline").slider({value: (fr * 1)});

    progressPyChart.segments[0].value = fr;
    progressPyChart.segments[1].value = project.imgsA.length-fr-1;
    progressPyChart.update();

}


/*Move the time slider forward and display the correct frame and notes.*/
function goToNextFrame(clear) {

    var fr = project.currentFrame();

    fr++;

    if (fr > $("#frame").prop("max") * 1) {

        if (loop == true) {
            fr = 0;
        } else {
            if (clear == true) {
                clearInterval(playInterval);
                playInterval = undefined;
                return false;
            }
        }
    }

    goToFrame(fr);

    if (clear == true && stopAtNotes == true && (project.frames[fr] != undefined || project.notes[fr] != undefined)) {
        clearInterval(playInterval);
        playInterval = undefined;
        return false;
    }

}

/*Move the time slider backward and display the correct frame and notes.*/
function goToLastFrame() {
    var fr = project.currentFrame();

    fr--;

    if (fr < 0) {

        if (loop == true) {
            fr = $("#frame").prop("max") * 1;
        } else {

        }
    }

    goToFrame(fr);

}


/*Create an interval object to play the sequence at the correct rate.*/
function startPlaying(f) {
    if (f)
        goToFrame(f);
    //project.command='startPlaying('+project.currentFrame()+')';
    if (playInterval == undefined) { //only start the interval if it isn't already playing
        playInterval = setInterval(function () {
            goToNextFrame(true)

        }, (1000 / fps));
    }
}


function convertImgToBase64(data) {

    //console.log(data)

    var img = new Image();

        // this





    img.src = data;

    var canvas = document.createElement('CANVAS');
    canvas.width = currentWidth;
    canvas.height = currentHeight;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, currentWidth, currentHeight);
    dataURL = canvas.toDataURL("image/jpeg");
    canvas = null;
    img = null;
    return dataURL;
}

function toggleChannelButtons() {
    var viewers = $("#viewerControls button");
    // TOGGLE CONTROLS
    viewers.each(function () {
        var item = $(this);
        item.toggleClass('current');
    });
    switch (sequence) {
        case 1:
            sequence = 2;
            project.command = 'toggleChannelButtons();sequence = 2';
            break;
        case 2:
            sequence = 1;
            project.command = 'toggleChannelButtons();sequence = 1';
            break;
        default:
            sequence = 1;
    }


    project.setBackground();


    return false;
};


/*Class for storing the Sequence Data.*/
function showtime() {
    this.projectName = "";

    this.AFromFile = false;
    this.BFromFile = false;

    this.imgsA = {}; // array of original image paths for A
    this.imgsB = {}; // array of original image paths for B

    this.imgsAdata = {}; // array of image data urls for A
    this.imgsBdata = {}; // array of image data urls for B

    this.frames = {};// array of modified frames in local storage
    this.notes = {};

    this.thumbstate = {};
    this.currentFrame = function () {
        return ($('#frame').val() * 1);
    };

    this.load = function () {
        //var data = localStorage.getItem(projectName);
    };

    this.save = function () {
        var dataImage = canvas.toDataURL();
        var f = this.currentFrame();
        this.frames[f] = dataImage;
        //localStorage.setItem((this.projectName + f.toString()), dataImage); // save image data
        $("li.seqnum_" + f).addClass("hasDrawing");


    };

    this.setCurrentWidthFromImageSource = function (dataURL) {
        var img1 = new Image();
        img1.onload = function() {
            // this
                var maxWidth = 960,
                    maxHeight = 540,
                    currentWidth = this.width,
                    currentHeight = this.height;

                if (currentWidth > currentHeight) {
                  if (currentWidth > maxWidth) {
                    currentHeight *= maxWidth / currentWidth;
                    currentWidth = maxWidth;
                  }
                }
                else {
                  if (currentHeight > maxHeight) {
                    currentWidth *= maxHeight / currentHeight;
                    currentHeight = maxHeight;
                  }
                }

        canvas.width = currentWidth;
        canvas.height = currentHeight;

        $("#canvasDiv").css("width", currentWidth + 'px');
        $("#canvasDiv").css("height", currentHeight + 'px');

        $("#canvas").css("width", currentWidth + 'px');
        $("#canvas").css("height", currentHeight + 'px');

        $("#sequenceImage").css("width", canvas.width + 'px');
        $("#sequenceImage").css("height", canvas.height + 'px');
        }

        img1.src = dataURL;
        img1 = null;
    };

    this.clean = function(){
        this.frames = {};
        this.notes = {};
        this.imgsA = [];
        this.imgsAdata = {};
        this.imgsB = [];
        this.imgsBdata = {};

        goToFrame(0);
        $("#aInfo").html("");
        $("#bInfo").html("");
        $("#sequenceImage").prop('src', '');
        $("#frame").prop("max", 0);
        $("#frametotal").html(1);
        $("#timeline").slider({max: 1});
    }



    this.setPlayerSize = function () {
        if (this.imgsA && this.imgsA[0]) {
            if (!this.imgsAdata[0] && this.imgsA[0] instanceof  Blob) {
                var reader = new FileReader();

                reader.onload = function (e) {
                    var dataURL = reader.result;

                    project.setCurrentWidthFromImageSource(dataURL);


                }
                reader.readAsDataURL(this.imgsA[0]);
            } else {
                if (this.imgsAdata && this.imgsAdata[0]) {
                    this.setCurrentWidthFromImageSource(this.imgsAdata[0]);
                }
            }

        }

    };
//////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////
    this.addThumb = function(data){
        img = new Image()
        img.onload = function(){
        ratio = this.width/this.height;
        tWidth = 96;
        tHeight= tWidth/ratio;
        skips = Math.ceil(project.imgsA.length/(($(window).width()-200)/tWidth))
        _f = project.currentFrame()
        if (_f%skips) {
            project.thumbstate[_f] = true;
            return null;
        }
        var canvas = document.createElement('canvas');
        canvas.width = tWidth
        canvas.height = tHeight ;
        ctx = canvas.getContext("2d");
        ctx.drawImage(this, 0, 0, tWidth, tHeight);
        finalFile = canvas.toDataURL('image/jpeg'); //Always convert to png
        appendix = '<a class="thmbLink" onClick="goToFrame('+_f+')"><img class="thmb" id="thmb_'+ _f +'" src="' + finalFile + '"/></a>';
        $('#thumbnails').append(appendix);
        $("#thmb_"+_f).fadeIn();
        project.thumbstate[_f] = true;
        canvas = null;
        }
        img.src = data;
        img=null;

    }

    this.setBackground = function () {
        var f = this.currentFrame();

        $('#frameFileFum').html((Number(f)) + 1);
        switch (sequence) {
            case 1:
                if (this.imgsA && this.imgsA[f]) {
                    _name = this.imgsA[f].name;
                    $('#frameFileName').html(pad(f+1, 4));

                    if (!this.imgsAdata[f] && this.imgsA[f] instanceof Blob) {
                        var reader = new FileReader();

                        reader.onload = function (e) {
                            var dataURL = reader.result;

                            $("#sequenceImage").prop("src", convertImgToBase64(dataURL));

                            if (project.imgsAdata && project.imgsAdata[f] == undefined) {
                                dataURL = convertImgToBase64(dataURL);
                                project.imgsAdata[f] = dataURL;
                                $("#sequenceImage").prop("src", dataURL);

                                // background zipping
                                //

                                project.folderA.file(_name, dataURL.substr(dataURL.indexOf(',')+1), {base64: true});
                                console.log('zipped: '+_name)
                                //
                                //
                                //
                                //_f = new File([project.imgsAdata[f]], _fn, {type: "image/jpeg"});
                                //project.imgsA[f]=_f;
                            }

                            updateCanvas();
                        }

                        reader.readAsDataURL(this.imgsA[f]);

                    } else if (this.imgsAdata && this.imgsAdata[f]) {
                        $("#sequenceImage").prop("src", this.imgsAdata[f]);
                        if (!project.folderA.files['A/'+ _name])
                        {
                                project.folderA.file(_name, this.imgsAdata[f].substr(this.imgsAdata[f].indexOf(',')+1), {base64: true});
                                console.log('zipped: '+_name)
                        }


                        if (!this.thumbstate[f])
                        {
                            //console.log('here');
                            this.addThumb(this.imgsAdata[f]);
                        }

                    }


                } else {

                    $('#frameFileName').html("----");
                    // $("#sequenceImage").prop("src","showtime.png");
                }
                break;
            case 2:

                if (this.imgsB && this.imgsB[f]) {
                    _name = this.imgsB[f].name;
                    $('#frameFileName').html(pad(f+1, 4));
                    if (!this.imgsBdata[f] && this.imgsB[f] instanceof Blob) {
                        var reader = new FileReader();

                        reader.onload = function (e) {
                            var dataURL = reader.result;
                            $("#sequenceImage").prop("src", convertImgToBase64(dataURL));
                            if (project.imgsBdata && project.imgsBdata[f] == undefined) {
                                dataURL = convertImgToBase64(dataURL);
                                project.imgsBdata[f] = dataURL;
                                $("#sequenceImage").prop("src", dataURL);
                                
                                project.folderB.file(_name, dataURL.substr(dataURL.indexOf(',')+1), {base64: true});
                                console.log('zipped: '+_name)
                            }

                            updateCanvas();
                        }

                        reader.readAsDataURL(this.imgsB[f]);
                    } else if (this.imgsBdata && this.imgsBdata[f]) {
                        $("#sequenceImage").prop("src", this.imgsBdata[f]);
                        if (!project.folderB.files['B/'+ _name])
                        {
                                project.folderB.file(_name, this.imgsBdata[f].substr(this.imgsBdata[f].indexOf(',')+1), {base64: true});
                                console.log('zipped: '+_name)
                        }
                        if (!this.thumbstate[f])
                            this.addThumb(this.imgsAdata[f]);
                    }

                } else {

                    $('#frameFileName').html("----");
                    // $("#sequenceImage").prop("src","showtime.png");
                }
                break;
        }
    };

    this.nextNoteFrame = function () {

        var f = this.currentFrame() * 1;
        var startF = f;

        var limit = ($("#frame").prop("max") * 1);


        if (f + 1 > limit) {
            f = 0;
        } else {
            f++;
        }

        for (; f <= limit; f++) {
            if (this.frames[f] != undefined || this.notes[f] != undefined) {
                return f;
            }

        }


        for (f = 0; f < startF; f++) {
            if (this.frames[f] != undefined || this.notes[f] != undefined) {
                return f;
            }

        }


    }

    this.lastNoteFrame = function () {

        var f = this.currentFrame();


        var limit = $("#frame").prop("max") * 1;


        if (f <= 0) {
            f = limit;
        } else {
            f--;

        }


        for (; f >= 0; f--) {
            if (this.frames[f] != undefined || this.notes[f] != undefined) {
                return f;
            }

        }


    }
    this.generateSeqStats = function (s) {

        var SeqUse = this.imgsA;
        switch (s) {
            case 1:
                SeqUse = this.imgsA;
                break
            case 2:
                SeqUse = this.imgsB;

                break;
        }

        out = "<p>Frames: " + (SeqUse.length) + "</p><ol start=\"1\">";

        if (SeqUse && SeqUse[0] && SeqUse[0].name) {

            for (var i = 0; i < SeqUse.length; i++) {

                var notestatus = "";
                if (this.notes && this.notes[i]) {

                    notestatus += " hasNotes"
                }
                if (this.frames && this.frames[i]) {
                    notestatus += " hasDrawing"
                }
                out += "<li id=\"seq_" + s + "_" + i + "\" class=\"seqClick seqnum_" + i + " " + notestatus + "\">" + SeqUse[i].name + "</li>";
            }
        } else {
            for (var i = 0; i < SeqUse.length; i++) {

                var notestatus = "";
                if (this.notes && this.notes[i]) {
                    notestatus += " hasNotes"
                }
                if (this.frames && this.frames[i]) {
                    notestatus += " hasDrawing"
                }

                out += "<li id=\"seq_" + s + "_" + i + "\" class=\"seqClick seqnum_" + i + " " + notestatus + "\">" + (i + 1) + "</li>";
            }

        }
        out += "</ol>";
        return out;
    }
//////////////////////////////////////////////////
    ////////////// read files  ///////////////////

    
    this.makeVideo = function(file){
        var reader = new FileReader();
            if (!project.imgsAdata)
                project.imgsAdata = {};
            if (project.imgsBdata)
                project.imgsBdata = {};
            var videoconverted = [];
            var lastframe = null;
            var count = 0;

        reader.onprogress = function(evt){
           if (evt.lengthComputable)
           {  //evt.loaded the bytes browser receive
              //evt.total the total bytes seted by the header
              //
             var percentComplete = (evt.loaded / evt.total)*100;
               progressPyChart.segments[0].value = percentComplete;
               progressPyChart.segments[1].value = 100-percentComplete;
        // Would update the first dataset's value of 'Green' to be 10
               progressPyChart.update();
               if (percentComplete>99)
                   progressPyChart.segments[0].value = 0;


             //$('#progressbar').progressbar( "option", "value", percentComplete );
           }
        }
        reader.onloadend = function (e) {
            var dataURL = reader.result;
            sourceVid=document.getElementById('myvid');
            sourceVid.src=dataURL;
            var hCanvas = document.getElementById('vidcanvas');
            var show = document.getElementById("sequenceImage");
            //canvas.width = currentWidth;
            //canvas.height = currentHeight;
            var hContext = hCanvas.getContext('2d');
            sourceVid.addEventListener('play', function() {
                runAnalysis();
            });

            var runAnalysis = function() {

            if (sourceVid.paused || sourceVid.ended) {
                return
            }
            
            frameSave();
                if (window.requestAnimationFrame) {
                    requestAnimationFrame(runAnalysis);
                } else {
                    setTimeout(runAnalysis, 0);
                }
            };

            var frameSave = function()
            {
                //hCanvas.width = sourceVid.videoWidth;
                //hCanvas.height = sourceVid.videoHeight;
                  //hContext.drawImage(sourceVid, 0, 0, sourceVid.videoWidth, sourceVid.videoHeight);
                hContext.drawImage(sourceVid,0,0,sourceVid.videoWidth, sourceVid.videoHeight, 0,0,hCanvas.width,hCanvas.height);
                  
                frame = hCanvas.toDataURL('image/jpeg');
                if (frame && lastframe!=frame)
                {
                    show.src = frame;
                    lastframe = frame;

                    switch (sequence) {
                        case 1:
                            project.imgsAdata[count] = frame;
                        case 2:
                            project.imgsBdata[count] = frame;
                    }
                    //goToFrame(count);
                    fblob = convertDataURL2binaryArray(frame);
                    count +=1;
                    videoconverted.push(new File([fblob], pad(count)+'.jpg', {type: 'image/jpeg'}));
                    $('#frameFileName').html(pad(count, 4));
                    progressPyChart.segments[0].value = count;
                    progressPyChart.segments[1].value = sourceVid.duration*fps - count;
                    progressPyChart.update();
                    //project.addThumb(frame);

                }

                  //duration = imgsData.length - 1
                  //if (frame != imgsData[duration]) 
                  //      imgsData.push(frame);
                  //var frame  = hContext.getImageData(0, 0, sourceVid.videoWidth, sourceVid.videoHeight);
                  //console.log(frame);
                      //length = data.length;
            };



            sourceVid.addEventListener('ended', function() {
                project.setFiles(videoconverted);
                progressPyChart.segments[0].value = 1;
                progressPyChart.segments[1].value = videoconverted.length;
                progressPyChart.update();

                    //clearInterval(project.vit);
            });

            sourceVid.addEventListener('loadeddata', function() {
                sourceVid.playbackRate = .5;
                sourceVid.play();
            }

            );


//myvid.source
            //console.log(dataURL);
        }
        reader.readAsDataURL(file);
    }


    this.setFiles = function (files) {
        var info;
        project.zip = new JSZip();  // main zip file for background archiving
        project.folderA = project.zip.folder("A");
        project.folderB = project.zip.folder("B");
        switch (sequence) {
            case 1:
                this.imgsA = files;
                project.cutout = this.imgsA.length - 1;
                if (!this.imgsAdata)
                    this.imgsAdata = {};
                info = this.generateSeqStats(sequence);

                this.setPlayerSize()
                if (info) {
                    $("#aInfo").html(info);

                }
                break
            case 2:
                this.imgsB = files;
                project.cutout = this.imgsB.length - 1;
                if (!this.imgsBdata)
                    this.imgsBdata = {};
                info = this.generateSeqStats(sequence);
                if (info) {
                    $("#bInfo").html(info);

                }
                break;
        }


    console.log(project.cutout);
    $("#frame").prop("max", project.cutout);
    $("#frametotal").html(project.cutout-1);
    $("#timeline").slider({max: (project.cutout)});



        this.setBackground();


    };


    this.getNotes = function (f, note) {
        if (!f)
            var f = this.currentFrame();


        if (this.frames && this.frames[f] && this.frames[f] != undefined) {
            var imgN = new Image();
            imgN.src = this.frames[f];
            context.drawImage(imgN, 0, 0, currentWidth, currentHeight);

        } else {
            context.clearRect(0, 0, currentWidth, currentHeight);

        }


        if (this.notes && this.notes[f] && this.notes[f] != undefined) {
            
            if (/^[\x00-\x7F]+$/.test(this.notes[f])) //false
                $('#frameNotes').attr('style', 'direction:ltr');
            else
                $('#frameNotes').attr('style', 'direction:rtl');

            $("#frameNotes").val(this.notes[f]);
        } else {
            $("#frameNotes").val("");

        }


    };


    this.setNote = function (fr, val) {

        if (val != "") {
            $("li.seqnum_" + fr).addClass("hasNotes");
        } else {

            $("li.seqnum_" + fr).removeClass("hasNotes");
        }

        this.notes[fr] = val;

    }

    this.clearFrame = function (f) {
        this.frames[f] = undefined;
        $("li.seqnum_" + f).removeClass("hasDrawing");
    }

    this.encode = function (fullEncode) {
        var data = new Object();
        data.A = this.imgsA;
        data.B = this.imgsB;


        data.frames = this.frames;
        data.notes = this.notes;
        //var res = (JSON.stringify(data));

        /*if (fullEncode){
         data.Adata = this.imgsAdata;
         data.Bdata = this.imgsBdata;

         }*/


        return (JSON.stringify(data));
    }

    this.loadFromJson = function (json) {
        data = JSON.parse(json);


        var startingSeq = sequence


        sequence = startingSeq

        this.frames = data.frames;
        this.notes = data.notes;
        this.setBackground();
        context.clearRect(0, 0, canvas.width, canvas.height);
        this.getNotes();
        return data;
    }

    this.getDataFromZip = function (zipBlob) {


    }

    this.download = function (fullEncode, mode) {

        //var zip = new JSZip();
        if (!project.zip)
            project.zip = new JSZip();  // main zip file for background archiving
        dump = this.encode(fullEncode)
        project.zip.file("showtime.json", dump);

        var img = project.zip.folder("frames");
        for (var f = 0; f < this.frames.length; f++) {
            $('#frameFileName').html(pad(f, 4));
            var fr = this.frames[f];
            if (fr != undefined) {
                var imgN = new Image();
                imgN.src = fr;
                img.file("frame" + f + ".png", imgN.src.substr(imgN.src.indexOf(',') + 1), {base64: true});
            }
        }


        if (fullEncode) {

            if (!project.folderA)
                project.folderA = project.zip.folder("A");
            //var img = zip.folder("A");
            //
            for (var f = 0; f < this.imgsA.length; f++) {
                $('#frameFileName').html(pad(f, 4));
                //progressPyChart.segments[0].value = f;
                //progressPyChart.segments[1].value = this.imgsA.length - f;
                //progressPyChart.update();
                var _name = this.imgsA[f].name;
                if (!project.folderA.files['A/'+ _name])
                    goToFrame(f);
            }
            if (!project.folderB)
                project.folderB = project.zip.folder("B");
            //var img = zip.folder("A");
            for (var f = 0; f < this.imgsB.length; f++) {
                $('#frameFileName').html(pad(f, 4));
                var _name = this.imgsB[f].name;
                if (!project.folderB.files['B/'+ _name])
                    goToFrame(f);   
                
            }

        }

        console.log('generating...');
        var content = project.zip.generate({'type': 'blob'});
        console.log('generated');

        if (mode == 1) {
            saveAs(content, this.projectName + ".zip");
        }
        else {
            desc = $("#description").val()
            if (!desc)
                alert('Please Describe your show')
            else {
                url = '/api/asset/save/showtime?collection='+this.projectName+'&name='+this.projectName+'.zip'+'&description='+desc;
                var xmlHttpRequest = new XMLHttpRequest();
                xmlHttpRequest.open("PUT", url, true);
                // subscribe to this event before you send your request.
                xmlHttpRequest.onreadystatechange = function () {
                    if (xmlHttpRequest.readyState == 4) {
                        //alert the user that a response now exists in the responseTest property.
                        // And to view in firebug
                        data = JSON.parse(xmlHttpRequest.responseText);
                        project.latest_dump  = dump;
                        //location.reload();

                    }
                }
                xmlHttpRequest.send(content);
                project.command = 'setTimeout(function(){location.reload();goToFrame('+project.currentFrame()+');}, 1000)';
                setTimeout(function(){
                    project.command = 'goToFrame('+project.currentFrame()+')';
                }, 1000)

            }
        }
    }
}


$(document).ready(function () {
    canvasInit();

    if (typeof(Storage) !== "undefined") {
        canvas.onmouseup = function () {
            project.save();
        };

        $("#fileUpload").change(function () {

            project.setFiles(this.files);

        });
        $("#videoUpload").change(function () {

            project.makeVideo(this.files[0]);

        });
        /*
         Make a preivew of the nib in the nibCanvase and make a snapshot of the nib for the hover nib image.
         */
        function setPreview() {
            var preview = document.getElementById('brushPreview');

            preview.width = (nibSize);
            preview.height = (nibSize);


            previewContext = preview.getContext("2d");

            var centerX = preview.width / 2;
            var centerY = preview.height / 2;
            var radius = nibSize / 2;

            if (activeTool == "eraser") {
                previewContext.fillStyle = 'white';

            } else {

                previewContext.fillStyle = paintColor;
            }
            previewContext.globalAlpha = opacity;
            previewContext.beginPath();
            switch (nibShape) {
                case "square":
                    previewContext.rect(0, 0, nibSize, nibSize);
                    break;
                default:
                    previewContext.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
            }


            previewContext.fill();
            nib.src = preview.toDataURL();

        }

        nib = $("#nibImage")[0];
        setPreview();
        /*Move the nib to the mouse location and show it.*/
        function showNibAtEvent(e) {
            nib.style.top = e.pageY - (nibSize / 2) + "px";
            nib.style.left = e.pageX - (nibSize / 2) + "px";
            nib.style.display = "block";
        }

        $("#canvasDiv").hover(function (e) {
            showNibAtEvent(e);
        });

        $("#canvasDiv").mousemove(function (e) {
            showNibAtEvent(e);
        });

        $("#canvasDiv").mouseleave(function (e) {
            nib.style.display = "none";
        });
        $("#canvasDiv").mousedown(function (e) {

            nib.style.display = "none";
        });

        // Spectrum color picker implementation
        $("#toolColorpicker").spectrum({
            hide: function (tinycolor) {
                var col = $("#toolColorpicker").spectrum("get");
                paintColor = col.toHexString()
                setPreview()
            },
            color: "rgb(0, 155, 255)",
            showPalette: true,
            showPaletteOnly: true,
            hideAfterPaletteSelect: true,
            palette: [
                ['black', 'rgb(128, 128, 128);', 'white'],
                ['rgb(255, 0, 0);', 'rgb(255, 153, 0);', 'rgb(255, 255, 0);'],
                ['rgb(0, 255, 0);', 'rgb(0, 255, 255);', 'rgb(0, 155, 255);'],
                ['rgb(0, 0, 255);', 'rgb(153, 0, 255);', 'rgb(255, 0, 255);']
            ]
        });

        $('#brushOpacity').change(function () {
            opacity = $('#brushOpacity').val();
            setPreview()
        });

        $("#size").change(function () {
            nibSize = this.value;
            setPreview()
        });

        $("#toolMarker").click(function () {
            activeTool = "marker";
            setPreview();
            return false;
        });

        $("#toolEraser").click(function () {
            activeTool = "eraser";
            setPreview();
            return false;
        });


        $("#square").click(function () {
            nibShape = "square";
            setPreview();
            return false;
        });

        $("#circle").click(function () {
            nibShape = "circle";
            setPreview();
            return false;
        });


        $("#frame").change(function () {

            project.setBackground();
            context.clearRect(0, 0, canvas.width, canvas.height);
            project.getNotes();

        });


        /*
         $("#sequence1").click(function(){

         if (sequence != 1){
         toggleChannelButtons();
         }

         sequence = 1;
         project.setBackground();
         return false;
         });

         $("#sequence2").click(function(){


         toggleChannelButtons();

         sequence = 2;
         project.setBackground();
         return false;
         });*/

        $("#loop").change(function () {
            loop = $("#loop").prop("checked");
        });
        $("#stopAtNotes").change(function () {
            stopAtNotes = $("#stopAtNotes").prop("checked");
        });
        $("#play").click(function () {
            startPlaying();
            return false;
        });

        $("#stop").click(function () {
            if (playInterval != undefined) {

                clearInterval(playInterval);
                playInterval = undefined;
            }
            return false;
        });

        $("#fps").change(function () {
            fps = $("#fps").val();
            if (playInterval != undefined) {
                clearInterval(playInterval);
                playInterval = undefined;
                startPlaying();
            }

        });
        $(window).resize(function(){

               project.setPlayerSize();
               return false;

        })
        $("#name").change(function () {
            project.projectName = $("#name").val();
            return false;
        });
        $("#download").click(function () {

            if (project.projectName && project.projectName.length > 0) {
                project.download($("#allData").prop("checked"), 1);
            } else {
                alert('You must give this project a Name before you can download.');
            }
            return false;
        });

        $("#save").click(function () {

            if (project.projectName && project.projectName.length > 0) {
                project.download($("#allData").prop("checked"), 0);
            } else {
                alert('You must give this project a Name before you can download.');
            }
            return false;
        });
        /*

         $("#import").click(function(){

         if (project.projectName.length > 0) {
         project.download();
         } else {
         alert('You must give this project a Name before you can download.');
         }
         return false;
         });
         */

        loadWithFile = function(f){


             var manifestName = "showtime.json";
            // read the content of the file with JSZip
            try
            {
            project.zip = new JSZip(f);
            manifest = project.zip.file(manifestName);
            if (manifest) {

                var data = project.loadFromJson(manifest.asText());

                var startSequence = sequence;

                if (data.A.length > 0) {

                    var newImgs = [];

                    for (i = 0; i < data.A.length; i++) {
                        A = data.A[i];
                        var tempA = project.zip.file("A/" + A.name);

                        if (tempA != undefined) {


                            newImgs[i] = "data:" + 'image/jpeg' + ";base64," + btoa(tempA.asBinary());

                        }
                    }

                    if (newImgs.length > 0) {
                        sequence = 1;
                        project.setFiles(data.A);
                        project.imgsAdata = newImgs;

                        project.setCurrentWidthFromImageSource(project.imgsAdata[0]);
                    }


                }


                if (data.B.length > 0) {

                    var newImgs = [];

                    for (i = 0; i < data.B.length; i++) {
                        B = data.B[i];
                        var tempB = project.zip.file("B/" + B.name);

                        if (tempB != undefined) {


                            newImgs[i] = "data:" + B.type + ";base64," + btoa(tempB.asBinary());

                        }


                    }


                    if (newImgs.length > 0) {
                        sequence = 2;
                        project.setFiles(data.B);
                        project.imgsBdata = newImgs;
                    }

                }
                sequence = startSequence;
                project.setBackground();
                //goToNextFrame()
                startPlaying();
            } else {
                alert("No Manifest found...");
            }
            }
        catch(err) {
            console.log(err);
            $('#frameFileName').html('ER:(');
        }



        }

        laodzipfile = function (e) {
            f = e.target.result;
            loadWithFile(f);
        }

        importzip = function (evt) {
            var files = evt.target.files;
            for (var i = 0, f; f = files[i]; i++) {

                var reader = new FileReader();

                // Closure to capture the file information.
                reader.onloadend = (function (theFile) {
                    return laodzipfile;
                })(f);

                // read the file !
                // readAsArrayBuffer and readAsBinaryString both produce valid content for JSZip.
                reader.readAsArrayBuffer(f);
                // reader.readAsBinaryString(f);
            }
        };

        $("#import").on("change", importzip);


        $("#toolClear").click(function () {
            project.clearFrame($("#frame").val());
            context.clearRect(0, 0, canvas.width, canvas.height);
            _f = project.currentFrame()
            delete project.notes[_f]
            delete project.frames[_f]
            return false;
        });

        $("#next").click(function () {
            if (playInterval == undefined) {
                goToNextFrame(false)
            }
            return false;
        });

        $("#clean").click(function () {
            project.clean();
            return false;
        });

        $("#new").click(function () {
            location = '/app/showtime';
            return false;
        });        $("#previousFrame").click(function () {
            if (playInterval == undefined) {
                goToLastFrame()
            }
            return false;
        });

        $("#nextNote").click(function () {
            if (playInterval == undefined) {
                var f = project.nextNoteFrame();

                if (f != undefined) {
                    goToFrame(f);
                }

            }
            return false;
        });

        $("#lastNote").click(function () {
            if (playInterval == undefined) {
                var f = project.lastNoteFrame();

                if (f != undefined) {
                    goToFrame(f);
                }

            }
            return false;
        });


        $("#canvasToggle").click(function () {
            $("#canvasToggle").toggleClass('hideDrawings');
            $("#canvasToggle").toggleClass('showDrawings');

            switch ($("#canvasToggle").data("state")) {
                case "on":
                    $("#canvasToggle").data("state", "off");
                    // $("#canvasToggle").html("Show");
                    $(canvas).hide();
                    break;

                case "off":
                    $("#canvasToggle").data("state", "on");
                    // $("#canvasToggle").html("Hide");
                    $(canvas).show();
                    break;

            }
            return false;
        });


        $(".stopKBD").on('focus', function () {
            allowKBD = false;
        });

        $(".stopKBD").on('blur', function () {
            allowKBD = true;
        });
        $("#frameNotes").bind('input propertychange', function() {
            var f = project.currentFrame();
            note = $("#frameNotes").val();
            project.command = 'project.getNotes('+f+','+JSON.stringify(note)+')';
            project.setNote(f, note);
            if (/^[\x00-\x7F]+$/.test(note) && note) //false
                $('#frameNotes').attr('style', 'direction:ltr');
            else
                $('#frameNotes').attr('style', 'direction:rtl');
            //project.command = 'project.setNote('+ f +', "'+ note +'")';

        });

        $("#info").click(function (e) {
            if (($(e.target)).hasClass("seqClick")) {

                var dat = e.target.id.split("_");
                var clickedSequence = dat[1] * 1;

                if (sequence != clickedSequence) {
                    toggleChannelButtons();
                }
                //sequence = clickedSequence;

                goToFrame(dat[2] * 1);
            }
        });


    } else {
        alert("Uh Oh... you need to update your browser to use showtime!");
    }


    //ADDED FOR BUTTON TOGGLING
    $(function () {
        $('#viewerControls button').click(function () {
            if (!project.slave)
                return toggleChannelButtons();
        });
    });


    timeline = $("#timeline").slider({
        range: "min",
        /* value: $( "#frame" ).val(),*/
        min: 1,
        max: Math.max(project.imgsA.length, project.imgsB.length),
        //range:true,
        slide: function (event, ui) {
            if (!project.slave)
            {
                goToFrame(ui.value);
                progressPyChart.segments[0].value = ui.value;
                progressPyChart.segments[1].value = project.imgsA.length-ui.value-1;
                progressPyChart.update();
            }


        }
    });






    $(document).keydown(function (e) {

        if (allowKBD && !project.slave) {
            /*Necessary so user can use these keys when typing.*/
            switch (e.keyCode) {




                case 37: //LEFT ARROW
                    e.preventDefault();
                    goToLastFrame();

                    break;
                case 65: //A: strafe left in video games
                    e.preventDefault();
                    goToLastFrame();

                    break;

                case 39: //RIGHT ARROW
                    e.preventDefault();
                    goToNextFrame(false);

                    break;
                case 68: //D: strafe left in video games
                    e.preventDefault();
                    goToNextFrame(false);

                    break;
                case 32: // Spacebar
                    e.preventDefault();
                    if (playInterval == undefined) {
                        startPlaying();
                    } else {
                        clearInterval(playInterval);
                        playInterval = undefined;
                    }


                    break;

                case 81: // Q
                    e.preventDefault();
                    toggleChannelButtons();

                    break;

                default: //do nothing

            }
        }

    });



});


var project = new showtime();
function goodbye(e) {
    if (!project.latest_dump || project.latest_dump != project.encode(true)) {
        if (!e) e = window.event;
        //e.cancelBubble is supported by IE - this will kill the bubbling process.
        e.cancelBubble = true;
        e.returnValue = 'You have unsaved data!'; //This is displayed on the dialog

        //e.stopPropagation works in Firefox.
        if (e.stopPropagation) {
            e.stopPropagation();
            e.preventDefault();
        }
    }
}
//window.onbeforeunload=goodbye;
		 
progressChartOptions = {
    segmentShowStroke : false,
    segmentStrokeColor : "#ccc",
    segmentStrokeWidth : 1,
    percentageInnerCutout : 85, // This is 0 for Pie charts
    animationSteps : 100,
    animationEasing : "liner",
    //animateRotate : true,
    animateScale : false,
    animation : false
}
var progressData = [
    {
        value: 0,
        color:"#aaa",
        highlight: "#eee",
        label: "Loaded"

    },
     {
        value: 100,
        color:"#333",
        highlight: "#555",
        label: "Remaining"

    },


]

var ctx = $("#progressChart").get(0).getContext("2d");
var progressPyChart = new Chart(ctx).Pie(progressData, progressChartOptions);

