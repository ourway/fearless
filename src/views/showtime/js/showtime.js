/*

 Showtime JavaScript RAM Player
 by: Farsheed Ashouri
 originally by John Martini and Shawn Olson

 */



/*Element Vars*/
var canvas;
var canvasDiv;
var context;
var SequenceImage = new Image();
var currentWidth = 720;
var currentHeight = 405;
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
var cursorStyleObject = new Object();

/*Control Vars*/
var playInterval;
var fps = 24;
var stopAtNotes = true;
var loop = true;
var sequence = 1;
var manifest;
var allowKBD = true;

/*Image paths*/
var imageUrl = "../images/hideicon.svg"

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
    project.setBackground();
    context.clearRect(0, 0, canvas.width, canvas.height);
    project.getNotes();
    $("#timeline").slider({value: (fr * 1)});

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
function startPlaying() {
    if (playInterval == undefined) { //only start the interval if it isn't already playing
        playInterval = setInterval(function () {
            goToNextFrame(true)

        }, (1000 / fps));
    }
}

function convertImgToBase64(img) {
    var canvas = document.createElement('CANVAS');
    var ctx = canvas.getContext('2d');


    var dataURL;
    canvas.height = img.height;
    canvas.width = img.width;
    ctx.drawImage(img, 0, 0);
    dataURL = canvas.toDataURL("image/png");

    canvas = null;

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
            break;
        case 2:
            sequence = 1;
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


    this.currentFrame = function () {
        return ($('#frame').val() * 1);
    };

    this.load = function () {
        var data = localStorage.getItem(projectName);
    };

    this.save = function () {
        var dataImage = canvas.toDataURL();
        var f = this.currentFrame();
        this.frames[f] = dataImage;
        localStorage.setItem((this.projectName + f.toString()), dataImage); // save image data
        $("li.seqnum_" + f).addClass("hasDrawing");


    };

    this.setCurrentWidthFromImageSource = function (dataURL) {
        var img1 = new Image();
        img1.src = dataURL;


        currentWidth = img1.width;
        currentHeight = img1.height;

        proportion = currentWidth / currentHeight //!TODO: use this to rescale h/w if window size is exceeded.


        if (currentWidth > $(window).width()) {
            currentWidth = $(window).width();


        }

        if (currentHeight > $(window).height()) {
            currentHeight = $(window).height();
        }

        img1 = null
        canvas.width = currentWidth
        canvas.height = currentHeight

        $("#canvasDiv").css("width", currentWidth + 'px');
        $("#canvasDiv").css("height", currentHeight + 'px');

        $("#canvas").css("width", currentWidth + 'px');
        $("#canvas").css("height", currentHeight + 'px');

        $("#sequenceImage").css("width", canvas.width + 'px');
        $("#sequenceImage").css("height", canvas.height + 'px');

    };


    this.setPlayerSize = function () {
        if (this.imgsA && this.imgsA[0]) {
            if (this.imgsA[0] instanceof  Blob) {
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

    this.setBackground = function () {
        var f = this.currentFrame();
        $('#frameFileFum').html((Number(f)) + 1);
        switch (sequence) {
            case 1:
                if (this.imgsA && this.imgsA[f]) {
                    $('#frameFileName').html(this.imgsA[f].name);

                    if (this.imgsA[f] instanceof Blob) {
                        var reader = new FileReader();

                        reader.onload = function (e) {
                            var dataURL = reader.result;


                            $("#sequenceImage").prop("src", dataURL);

                            if (project.imgsAdata && project.imgsAdata[f] == undefined) {
                                project.imgsAdata[f] = convertImgToBase64($("#sequenceImage")[0]);
                            }

                            updateCanvas();
                        }

                        reader.readAsDataURL(this.imgsA[f]);

                    } else if (this.imgsAdata && this.imgsAdata[f]) {
                        $("#sequenceImage").prop("src", this.imgsAdata[f]);
                    }


                } else {

                    $('#frameFileName').html("Frame Missing");
                    // $("#sequenceImage").prop("src","showtime.png");
                }
                break;
            case 2:

                if (this.imgsB && this.imgsB[f]) {
                    $('#frameFileName').html(this.imgsA[f].name);
                    if (this.imgsB[f] instanceof Blob) {
                        var reader = new FileReader();

                        reader.onload = function (e) {
                            var dataURL = reader.result;


                            $("#sequenceImage").prop("src", dataURL);
                            if (project.imgsBdata && project.imgsBdata[f] == undefined) {
                                project.imgsBdata[f] = convertImgToBase64($("#sequenceImage")[0]);
                            }

                            updateCanvas();
                        }

                        reader.readAsDataURL(this.imgsB[f]);
                    } else if (this.imgsBdata && this.imgsBdata[f]) {
                        $("#sequenceImage").prop("src", this.imgsBdata[f]);
                    }

                } else {

                    $('#frameFileName').html("Frame Missing");
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

    this.setFiles = function (files) {
        var info;
        switch (sequence) {
            case 1:
                this.imgsA = files;
                this.imgsAdata = {};
                info = this.generateSeqStats(sequence);

                this.setPlayerSize()
                if (info) {
                    $("#aInfo").html(info);

                }
                break
            case 2:
                this.imgsB = files;
                this.imgsBdata = {};
                info = this.generateSeqStats(sequence);
                if (info) {
                    $("#bInfo").html(info);

                }
                break;
        }


        if (files.length > $("#frame").prop("max")) {
            $("#frame").prop("max", files.length - 1);
            $("#frametotal").html(files.length);
            $("#timeline").slider({max: (files.length - 1)});


        } else {

            if (this.imgsB == undefined || this.imgsA.length >= this.imgsB.length) {
                $("#frame").prop("max", this.imgsA.length - 1);
                $("#frametotal").html(this.imgsA.length);
                $("#timeline").slider({max: (this.imgsA.length - 1)});
            } else {
                $("#frame").prop("max", this.imgsB.length - 1);
                $("#frametotal").html(this.imgsB.length);
                $("#timeline").slider({max: (this.imgsB.length - 1)});
            }
        }


        this.setBackground();


    };


    this.getNotes = function () {
        var f = this.currentFrame();


        if (this.frames && this.frames[f] && this.frames[f] != undefined) {
            var imgN = new Image();
            imgN.src = this.frames[f];
            context.drawImage(imgN, 0, 0, currentWidth, currentHeight);

        } else {
            context.clearRect(0, 0, currentWidth, currentHeight);

        }


        if (this.notes && this.notes[f] && this.notes[f] != undefined) {

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

        var zip = new JSZip();
        zip.file("showtime.json", this.encode(fullEncode));

        var img = zip.folder("frames");

        for (var f = 0; f < this.frames.length; f++) {
            var fr = this.frames[f];
            if (fr != undefined) {
                var imgN = new Image();
                imgN.src = fr;
                img.file("frame" + f + ".png", imgN.src.substr(imgN.src.indexOf(',') + 1), {base64: true});
            }
        }


        if (fullEncode) {

            var img = zip.folder("A");
            for (var f = 0; f < this.imgsA.length; f++) {
                var fr = this.imgsAdata[f];
                if (fr != undefined) {
                    var imgN = new Image();
                    imgN.src = fr;
                    img.file(this.imgsA[f].name, imgN.src.substr(imgN.src.indexOf(',') + 1), {base64: true});
                }
            }

            var img = zip.folder("B");
            for (var f = 0; f < this.imgsB.length; f++) {
                var fr = this.imgsBdata[f];
                if (fr != undefined) {
                    var imgN = new Image();
                    imgN.src = fr;
                    img.file(this.imgsB[f].name, imgN.src.substr(imgN.src.indexOf(',') + 1), {base64: true});
                }
            }
        }


        var content = zip.generate({'type': 'blob'});

        if (mode == 1) {
            saveAs(content, this.projectName + ".zip");
        }
        else {
            url = '/api/asset/save/showtime?collection=' + this.projectName + '&name=' + this.projectName + '.zip';
            var xmlHttpRequest = new XMLHttpRequest();
            xmlHttpRequest.open("PUT", url, true);
             // subscribe to this event before you send your request.
             xmlHttpRequest.onreadystatechange=function() {
              if (xmlHttpRequest.readyState==4) {
               //alert the user that a response now exists in the responseTest property.
               // And to view in firebug
               data = JSON.parse(xmlHttpRequest.responseText);
               console.log(data.url)
              }
             }
            xmlHttpRequest.send(content);

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
                console.log(paintColor)
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
            var zip = new JSZip(f);
            manifest = zip.file(manifestName);
            if (manifest) {

                var data = project.loadFromJson(manifest.asText());

                var startSequence = sequence;
                console.log('sdfsdf')

                if (data.A.length > 0) {

                    var newImgs = [];

                    for (i = 0; i < data.A.length; i++) {
                        A = data.A[i];
                        var tempA = zip.file("A/" + A.name);

                        if (tempA != undefined) {


                            newImgs[i] = "data:" + A.type + ";base64," + btoa(tempA.asBinary());

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
                        var tempB = zip.file("B/" + B.name);

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
                goToNextFrame()

            } else {
                alert("No Manifest found...");
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
            return false;
        });

        $("#next").click(function () {
            if (playInterval == undefined) {
                goToNextFrame(false)
            }
            return false;
        });

        $("#previousFrame").click(function () {
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
                    console.log("nope");
                    $(canvas).show();
                    break;

            }
            return false;
        });


        $(".stopKBD").focus(function () {
            allowKBD = false;
        });

        $(".stopKBD").blur(function () {
            allowKBD = true;
        });

        $("#frameNotes").change(function () {
            var f = project.currentFrame();
            project.setNote(f, $("#frameNotes").val());
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
            return toggleChannelButtons();
        });
    });


    timeline = $("#timeline").slider({
        range: "min",
        /* value: $( "#frame" ).val(),*/
        min: 1,
        max: 100,
        slide: function (event, ui) {

            goToFrame(ui.value);

        }
    });

    $(document).keydown(function (e) {

        if (allowKBD) {
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
		 
