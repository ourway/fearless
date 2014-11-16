var fearlessShowtimeApp = angular.module('fearlessShowtimeApp', ['ngResource', 'ngCookies', 'restangular', 'ngRoute']);





function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 8; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}



    fearlessShowtimeApp.controller('showtimeCtrl', function($scope, $rootScope, $cookies,$http,
                                                      $timeout, $location, $routeParams, Restangular, $interval) {


             $scope.asset = {};
             $scope.master = false;
             $scope.modetext = 'MASTER';
             $scope.hey = function(){
                 console.log($scope.asset);
             }
             $scope.timeConverter = function(UNIX_timestamp){
             var a = new Date(UNIX_timestamp*1000);
             var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                 var year = a.getFullYear();
                 var month = months[a.getMonth() - 1];
                 var date = a.getDate();
                 var hour = a.getHours();
                 var min = a.getMinutes();
                 var sec = a.getSeconds();
                 var time = date + month + year + '-' + hour + ':' + min;
                 return time;
             }

$scope.$watch(function(){return $location.$$path},
    function(){
        //project.command = 'window.location = ' + $location.$$path;
            //clearInterval(project.showSyncWsInterval.$$intervalId);
            //project.showSyncWs.close();  // close latest websocket connection
            //project.imgsA = {};
            if (project.showSyncWs)
            {
                $('.thmb').fadeOut(400);
                $timeout(function(){
                $('#thumbnails .thmb').remove();}, 500);
                
                //console.log($location.$$path)
                //var project = new showtime();
                //location.reload()
                project.imgsA = [];
                project.imgsB = [];
                project.zip = null;
                project.video = null;
                project.imgsAdata = {};
                project.imgsBdata = {};
                project.thumbstate = [];
                //project.BFromFile = false;

                goToFrame(0);
                $scope.master = false;
                $scope.slave = false;
                $scope.modetext = 'MASTER';
            }
            //$scope.command = null;
            //progressPyChart.update();
    
        $scope.masterme = function(){
            if (!$scope.slave && $scope.master==false)
            {
                $scope.master = true;
                //project.master = true;
                project.slave = false;
                $scope.modetext = 'MASTER';
                $timeout(function(){
                        project.command = 'goToFrame(' + project.currentFrame() + ')';
                    }, 500);
            }
            else
            {
                $scope.master = false;
                //project.master = false;
                $scope.modetext = 'REVIEW';
            }
            }
            req = $http.post('/api/auth/getUserInfo');
            req.success(function(result){
            if (result.message == 'ERROR'){
                window.location = '/app/#/auth/login/' + btoa('showtime');
                return
            }
            else {
                    //$location.path(cur);

                //project = new showtime()
                $scope.user = result
                loc = $location.$$path
                name = loc.slice(1)

                //x = Restangular.one('api', 'asset').post(name+'.zip', {'name':true})
                //x.then(function(ass){
                //    console.log(ass);
                //})
                if (name.length==8){
                    $scope.loading = true;
                    $scope.name = name;
                    //var project = new showtime();
                    project.projectName = $scope.name;
                    req = $http.post('/api/asset/'+$scope.name+'.zip?name=true');
                    req.error(function(resp){
                        if (resp.title=='Authentication required')
                            window.location = '/app/#/auth/login/' + btoa('showtime');
                            })
                    req.success(function(assetInfo){


                        if (assetInfo.url) {
                            JSZipUtils.getBinaryContent(assetInfo.url + '?rn=' + makeid(), function (err, data) {
                                if (err) {
                                    return false;
                                    //throw err; // or handle err
                                }
                                //var project = new showtime();
                                loadWithFile(data);


                                $scope.asset = assetInfo;
                                project.assetId = $scope.asset.id;

                                if (!project.showSyncWs)
                                    project.showSyncWs = new WebSocket("ws://"+$scope.user.server.ip+":5004/media/syncshow");
                                project.showSyncWs.onopen = function() {
                                    //
                                project.showSyncWs.onmessage = function (evt) {
                                        serverMessage = JSON.parse(evt.data);
                                        project.master = serverMessage.master;
                                        //console.log(serverMessage);
                                        
                                        if (project.master && $scope.user.id != project.master)
                                        {
                                            $scope.slave = true;
                                            project.slave = true;
                                            //project.master = false;
                                            $scope.modetext = 'REVIEW';
                                        }
                                        else
                                        {
                                            $scope.slave = false;
                                            project.slave = false;
                                            //project.master = true;
                                            
                                            $scope.modetext = 'MASTER';
                                        }

                                    
                                        if ($scope.user.id != project.master){

                                            if (serverMessage.note && serverMessage.note!='None'){
                                                var note = serverMessage.note;
                                                    project.notes[JSON.parse(serverMessage.slide)] = note;
                                            }
                                            else
                                                delete project.notes[JSON.parse(serverMessage.slide)]
                                            if (serverMessage.frame && serverMessage.frame != 'None'){
                                                var frame = serverMessage.frame;
                                                    project.frames[JSON.parse(serverMessage.slide)] = frame;
                                            }
                                            else
                                                delete project.frames[JSON.parse(serverMessage.slide)]
                                            project.getNotes();

                                        }


                                        if (($scope.user.id != project.master) && (serverMessage.command != project.command) && serverMessage.command != 'None')
                                        {
                                            project.command = serverMessage.command;
                                            //console.log(serverMessage.command);
                                            eval(serverMessage.command)  // server tels me what to do

                                        
                                            //console.log(serverMessage.command, project.command);
                                        }


                                        //if (project.lock && serverMessage.frames && serverMessage.frames!='None' && serverMessage.frames != project.frames){
                                        //    project.frames = serverMessage.frames;
                                        //}
                                        //console.log(serverMessage)

                                };
                                project.showSyncWsInterval = $interval(function(){
                                        if (project.assetId)
                                        {
                                            if ($scope.master){
                                                f = project.currentFrame()
                                                frame =  project.frames[f];
                                                    dataToSend = JSON.stringify({'id':project.assetId,
                                                        'command':project.command, 'client':$scope.user.id,
                                                        'frame':frame,
                                                        'slide': f,
                                                        'i_want_to_be_master':$scope.master, 'note':project.notes[f]});
                                            }
                                            else
                                                dataToSend = JSON.stringify({'id':project.assetId, 'client':$scope.user.id});
                                            
                                            project.showSyncWs.send(dataToSend)
                                        }
                                }, 1000/fps)
                                $scope.loading = false;
                                $scope.$apply()
                                };
                            });
                         }


                         //$scope.changed = new Date(assetInfo.modified_on * 1000)


                    })
                    // here I should try to load data from asset server
                }
                else {
                    $scope.name = makeid();
                    project.projectName = $scope.name;
                    $location.path($scope.name);
                }


            showtimeUserInfos = Restangular.one('api', 'showtime').getList($scope.user.id);
            showtimeUserInfos.then(function(result){

                $scope.userShows = result;
                $scope.goto = function(to){
                    $location.path(to);
                    location.reload();
                }
            })


        }
        })

                    });

///////////////////////////////////////end///////////////////
    });
