var fearlessApp = angular.module('fearlessApp', ['ngRoute', 'ngResource', 'restangular', 'ui.grid', 'ui.bootstrap']);

fearlessApp.factory('authFactory', function($resource) {
  return $resource('/api/auth/:what',
    { what:'@action' },
    { save: { method: 'POST' }}
  );
});

function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}



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


function timeConverter(UNIX_timestamp, mode){
    if (UNIX_timestamp)
        var a = new Date(UNIX_timestamp*1000);
    else
        var a = new Date();
 //var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
     var year = a.getFullYear();
     var month = a.getMonth() + 1;
     var date = a.getDate();
     var hour = a.getHours();
     var min = a.getMinutes();
     var sec = a.getSeconds();
     var time = year+ '-' + pad(month,2) + '-' + pad(date,2)
     if (mode)
        var time = year+ '-' + pad(month,2) + '-' + pad(date,2) + ' ' + pad(hour, 2) + '-' + pad(min, 2)
     return time;
 }

var TITLE = 'TITLE';
    function TagToTip(a, b,c){
        task = c;
        target  = $("[data-task-title*='" + task + "']")
        if (target.length)
            target[0].click();
        //console.log(angular.element('#projectDetailContainer').scope.taskInfo);
    }



	fearlessApp.config(function($routeProvider, $locationProvider) {
		$routeProvider

			// route for the home page
			.when('/', {
				templateUrl : 'pages/home.html',
				controller  : 'mainController'
			})

			// route for the about page
			.when('/about/', {
				templateUrl : 'pages/about.html',
				controller  : 'mainController'
			})
			.when('/auth/login/:next', {
				templateUrl : 'pages/auth/login.html',
				controller  : 'mainController'
			})

			.when('/auth/login/', {
				templateUrl : 'pages/auth/login.html',
				controller  : 'mainController'
			})

            .when('/auth/signup', {
				templateUrl : 'pages/auth/signup.html',
				controller  : 'mainController'
			})		//$locationProvider.html5Mode(true);

			.when('/auth/reactivate', {
				templateUrl : 'pages/auth/reactivate.html',
				controller  : 'mainController'
			})		//$locationProvider.html5Mode(true);
			.when('/auth/reset', {
				templateUrl : 'pages/auth/reset.html',
				controller  : 'mainController'
			})		//$locationProvider.html5Mode(true);
			.when('/auth/changepassword/:token', {
				templateUrl : 'pages/auth/changepassword.html',
				controller  : 'mainController'
			})		//$locationProvider.html5Mode(true);
            .when('/pms', {
                templateUrl: 'pages/pms/index.html',
                controller: 'projectCtrl'
            })
            .when('/pms/:projId', {

                templateUrl: 'pages/pms/detail.html',
                controller: 'projectDetailCtrl'
            })
            .when('/pms/:projId/seq/:seqId', {

                templateUrl: 'pages/pms/sequence.html',
                controller: 'sequenceDetailCtrl'
            })
            .when('/profile', {

                templateUrl: 'pages/auth/profile.html',
                controller: 'profileCtrl'
            })
            .when('/user/:userId', {

                templateUrl: 'pages/auth/profile.html',
                controller: 'profileCtrl'
            })
            .when('/report', {

                templateUrl: 'pages/crew/report.html',
                controller: 'reportCtrl'
            })
             .when('/ua', {

                templateUrl: 'pages/auth/access.html',
                controller: 'userAccessCtrl'
            })
             .when('/ams/c/:collectionId', {
                templateUrl: 'pages/ams/collection.html',
                controller: 'collectionCtrl'
            })

	
    })



function updateImageSize(img, maxWidth, maxHeight){
        currentWidth = img.width,
        currentHeight = img.height;

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

        var canvas = document.createElement('canvas');
        canvas.width = currentWidth
        canvas.height = currentHeight ;
        ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, currentWidth, currentHeight);

        result = canvas.toDataURL('image/webp');
        canvas.width = canvas.width;
        return result;
}








	// create the controller and inject Angular's $scope
	fearlessApp.controller('mainController', function($scope, $rootScope, $http,
                                                      $timeout, authFactory, $location, $routeParams) {
		// create a message to display in our view
        $rootScope.title = "Centeral Auth - Fearless";
        $scope.login_init = function() {
            //
        }
        $scope.check_auth_area = function() {
            if ($location.$$path.split('/')[1] == 'auth')
                return true;
        }
        if ($routeParams.m) {
            try{
                $scope.AuthRespMessage = atob($routeParams.m);
                $timeout(function () {
                    $location.url($location.path());
                    }, 3000);
            }
            catch(e) {
                console.log('ok');
            }
        }


		$scope.appName = 'fearless';
        $scope.$parent.showLogin = false;
		$scope.message = $scope.appName + ', A Revolutionary Animation Production Management System!';
        $scope.userInfo = {'logged_in':false};


    $scope.doLogin = function() {
        
        if (validateEmail($scope.loginInfo.email) == false && $scope.loginInfo.action != 'changepassword')
                return null;
                $scope.AuthRespInfo = null;
        url = '/api/auth/'+$scope.loginInfo.action;
        if ($routeParams.token)
            url = url + '?token=' + $routeParams.token
        prom = $http.post(url, $scope.loginInfo);
        prom.success(function(resp){



                $scope.login_wait = resp.wait;
                $scope.AuthRespMessage = resp.message;
                $scope.AuthRespInfo = resp.info;
                if (resp.message == 'error') {
                    $scope.loginInfo.password = null;
                    $scope.loginInfo.password2= null;
                    $scope.enable_signup = true;
                }
                setTimeout(function(){$scope.login_wait=null}, resp.wait);


               if (resp.message=='success') //green light
                    {
                        
                    console.log(resp);

                        if (resp.avatar != 'null')
                            localStorage.setItem('avatar', resp.avatar);
                        $scope.userInfo.username = resp.firstname;
                        $scope.userInfo.userid = resp.id;
                        $('#loginSubmitButton').text('Done!')
                        $scope.loginInfo.email = null;
                        $scope.loginInfo.password = null;
                        $scope.userInfo.logged_in = true;
                        try {
                            next_page = atob($routeParams.next);
                            console.log(next_page)
                            if (next_page.split('/')[1] === 'api' || next_page === 'showtime' )
                            {
                                window.location = next_page;
                            }
                            else
                            {
                                $location.path(next_page);
                            }
                        }
                        catch(e){
                            $location.path( '/' ) ;
                        }
                    }

            if (resp.message=='password changed' || resp.message == 'reset key sent') //green light
            {
                    $location.path( 'auth/login' );
            }
            if (resp.message=='error in password change') //green light
            {
                    m = btoa('There is an error.  Please chack')
            }

            if (resp.message=='warning' && resp.not_active)
            {
                $timeout(function(){
                    $location.path( 'auth/reactivate' );
                }, 2000);
            }


        });
    }

    // logout actions
    $scope.doLogout = function(){
            $http.post('/api/auth/logout');
            document.cookie = 'username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/'
            document.cookie = 'userid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/'
            localStorage.setItem('avatar', '');
            $scope.userInfo = {}; // Empty user info
            //$scope.userInfo.logged_in = true;

        }
    //Check if user is logged in
    $scope.is_logged_in = function(){
        c = {};
        document.cookie.split('; ').forEach(function(e){key = e.split('=')[0];value=e.split('=')[1];c[key]=value});
        var userid = c.userid;
        if (c.groups)
            var groups = c.groups.split(',');
        $scope.isManager = false;
        $scope.isAdmin = false;
        $scope.isClient = false;
        $scope.userGroups = [];
        for (group in groups){
            _g = groups[group];
            if (_g == 'admin')
                $scope.isAdmin = true;
            else if (_g == 'managers')
                $scope.isManager = true;
            else if (_g == 'clients')
                $scope.isClient = true;
            $scope.userGroups.push(_g);
        }
        var username = c.username;
       if (userid && username)
            {
                if (!$scope.userInfo.username)
                    $scope.userInfo.username = username;
                if (!$scope.userInfo.userid)
                    $scope.userInfo.userid = userid;
                $scope.userInfo.logged_in = true;
                return true
            }
        else {
           // This is where I redirect user to login page if she/he is unauthenticated
              $scope.userInfo = {}
              next_page = btoa($location.$$path);
              if (next_page == 'Lw==')  // if its just a # sign
                next_page = ''
              $location.path('/auth/login/'+next_page);
       }
       }


      $scope.go = function ( path ) {
          $location.path( path );
        };


	});

	fearlessApp.controller('aboutController', function($scope) {
		$scope.message = $scope.appName + '! I am an about page.';
	});




fearlessApp.controller('titleCtrl', function ($scope, $http, $location) {
    console.log

});


//  NON Angular scripts
//  ========================


function validateEmail(email) { 
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}



fearlessApp.controller('pmsCtrl', function($scope, $http, $location){
    $scope.init = function() {
        $http.post('/api/auth/getUserInfo').success(function(result){
            if (result.message == 'ERROR'){
                next_page = btoa($location.$$path);
                $location.path('/auth/login/'+ next_page);  // send user to authentication page.
            }

        })

    $scope.$parent.page= 'pms';
    }

});

fearlessApp.controller('profileCtrl', function($scope, $rootScope, $http, $location, $routeParams){
        $rootScope.title = "Profile - Fearless";
        userId = $routeParams.userId;
        if (!userId)
            userId = $scope.$parent.userInfo.userid;
        
        userInfoReq = $http.get('/api/db/user/'+userId);
        userInfoReq.success(function(resp, b, c, d){
            delete resp.password;
            delete resp.created_on;
            delete resp.modified_on;
            delete resp.lastLogIn;
            delete resp.latest_session_id;
            delete resp.token;
            //console.log(resp);
           $scope.user = resp; 

            });
        userInfoReq.error(function(a, b, c, d){
                console.log(a, b, c, d);
            });


        $scope.fileNameChanged = function(e){
        
            if (!e.files.length)
                return null;
        
            picFile = e.files[0];
            reader = new FileReader();
            reader.onloadend = function(){
                picDataURL = reader.result;
                // lets create a new iimage
                img = new Image();
                img.onload = function(){
                    
                    _pic = updateImageSize(this, 300, 300);
                    $scope.user.avatar=_pic;
                    $scope.$apply();
                            


                    //$('#ProfilePicImg')[0].src = profilePic;
                }
                img.src = picDataURL;

            }
            reader.readAsDataURL(picFile);
        }

    $scope.updateUserInformation = function(){
        x = $http.post('/api/db/user/'+ userId, $scope.user); //send it
        x.success(function(resp){
                if (!$routeParams.userId)
                {
                $scope.$parent.userInfo.username = $scope.user.firstname;
                localStorage.setItem('avatar', $scope.user.avatar);
                document.cookie = 'username='+ $scope.user.firstname +'; path=/; max-age=86400;'
                mail = {};
                mail['message'] = 'Hello <b>'+ $scope.user.firstname +'</b>!<br/>'
                mail['message']+= 'Your profile information updated successfully.<br/>';
                mail['message']+= 'Visit your profile <a href="'+ location.href +'"><b>here</b></a>.';
                mail['to'] = $scope.user.email;
                mail['subject'] = 'Fearless profile';
                //console.log(mail)
                m = $http.post('/api/sendmail', mail);
                }
            });
    }

});






fearlessApp.controller('reportCtrl', function($scope, $rootScope, $http, $timeout, $location){
        $scope.report = {};
        $scope.persian = false;
        $scope.repotPlaceholder = 'Write your daily or hourly report here ...';
        $scope.sendReport = function(){
            req = $http.put('/api/report', $scope.report);
            req.success(function(resp){
                if (resp.message == 'OK'){
                        $scope.report.body = null;
                        $scope.report.messageCallBack = 'Thank you! Your report has been sent.'
                        $timeout(function(){
                                $scope.report = {};
                                $('#report_textarea').focus();

                            }, 3000)


                    }
                })
       }
        

        });

fearlessApp.controller('projectCtrl', function($scope, $rootScope, $http, $location){
    
    //$scope.newProjectStartDate = new Date();Centeral Auth
    //Centeral Auth
    $rootScope.title = "Projects - Fearless";
    $scope.timeConverter = timeConverter;
    $scope.gridOptions = {
        data: 'myData',
        enableFiltering: true,
        enableSorting:true,
        enablePinning: true,
        columnDefs: [
                    { field: "name", displayName : 'Project', width: 200,
cellTemplate: '<div>  <a style="position:absolute;margin:5px" href="#pms/{{row.entity.id}}"><span class="glyphicon glyphicon-folder-close"></span> {{row.entity.name}}</a></div>'
                    },
                    { field: "calculate_number_of_tasks", displayName : 'Tasks', enableFiltering: true, enableSorting:true, width:70,
                    
                    cellTemplate: '<div style="padding:5px"><span style="opacity:0.5" class="glyphicon glyphicon-tag"></span><Span> {{row.entity.calculate_number_of_tasks}}</span></div>'
                    },
                    { field: "duration", enableFiltering: true, enableSorting:true, width:100,
                    cellTemplate: '<div style="padding:5px"><span style="opacity:0.5" class="glyphicon glyphicon-road"></span><Span> {{row.entity.duration}}</span></div>'
                    },
                    { field: "start", enableFiltering: false, enableSorting:true, width:155,
                    cellTemplate: '<div style="padding:5px"><span style="opacity:0.5" class="glyphicon glyphicon-calendar"></span><Span> {{row.entity.start}}</span></div>'
                    },
                    { field: "end", enableFiltering: false, enableSorting:true, width:155,
                    cellTemplate: '<div style="padding:5px"><span style="opacity:0.5" class="glyphicon glyphicon-calendar"></span><Span> {{row.entity.end}}</span></div>'
                    },
                    { field: "description", enableFiltering: true, enableSorting:false, width:190 },
                    { field: "id", enableFiltering: false, enableSorting:false, width:45 },

                ] 
        };

         $scope.myData = [ ];

        $scope.getLeader = function(id){
            console.log(id)
            $http.get('/api/db/user/'+id+'?field=alias').success(function(r){
                    console.log(r)}
                );
        }

        $scope.getProjData = function(){
            _pR = $http.get('/api/project');

            _pR.error(function(resp){
                   if (resp.title == 'Not Authorized')
                        $location.path('401')
                    } )
            _pR.success(function(resp){
                // Lets fix some problems:
                for (i=0;i<resp.length;i++){
                    resp[i].duration = Math.round((resp[i].end - resp[i].start)/(3600*24)) + ' days';
                        
                    resp[i].start = timeConverter(resp[i].start);
                    resp[i].end = timeConverter(resp[i].end);
                    resp[i].created_on = timeConverter(resp[i].start);
                    resp[i].modified_on = timeConverter(resp[i].start);
                }
                $scope.myData = resp;
                });
        }


        $scope.createNewProject = function(){
           $http.put('/api/project/add', $scope.newProject).success(function(resp){
                   console.log(resp);
                   $scope.getProjData();
                    $scope.newProject = {};
                   $('#projectAddModal').modal('hide');
                   
                   });
        }

        $scope.getResources = function(){
            $http.get('/api/users').success(function(resp){
                    $scope.resources = resp;
                    }).error(function(resp, status){
                        if (status == 401)
                            $location.path('auth/login');
                        });
        }


        });



fearlessApp.controller('userAccessCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular){
        $scope.$parent.page = 'auth';
        $scope.getUsers = function(){
            $http.get('/api/db/user').success(function(resp){
                    $scope.users = resp;
                    }).error(function(resp, status){
                        if (status == 401)
                            $location.path('auth/login');
                        });
        }


        $scope.getRoles = function(){

            $http.get('/api/db/role').success(function(resp){
                    console.log(resp);
                });

        }
        $scope.getGroups = function(){

            $http.get('/api/db/group').success(function(resp){
                    console.log(resp);
                });

        }

        $scope.getUsers();
        })

fearlessApp.controller('projectDetailCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular){
        $scope.$parent.page = 'pms';
            progressChartOptions = {
                segmentShowStroke : false,
                segmentStrokeColor : "#ccc",
                segmentStrokeWidth : 1,
                percentageInnerCutout : 0, // This is 0 for Pie charts
                animationSteps : 100,
                //animationEasing : "liner",
                //animateRotate : true,
                animateScale : false,
                animation : true
            }
            var progressData = [
                {
                    value: 0,
                    color:"#419641",
                    highlight: "#58C758",
                    label: "Done"

                },
                 {
                    value: 100,
                    color:"#ccc",
                    highlight: "#555",
                    label: "Left"
                },

            ]

            var ctx = $("#progressChart").get(0).getContext("2d");
            var progressPyChart = new Chart(ctx).Pie(progressData, progressChartOptions);

            $scope.projId = $routeParams.projId;
            $scope.toTitleCase = toTitleCase;
            $rootScope.title = "Project " + $scope.projId + " - Fearless";
            $scope.timeConverter = timeConverter;
            //$scope.replan = true;
            $scope.newtask = {};
            $scope.resetNewtask = function(){
                $scope.newtask = {};
                $scope.newtask.start = timeConverter();
                $scope.newtask.end = timeConverter();
                $scope.newtask.priority = 500;
                $scope.newtask.effort = null;
            }
            $scope.resetNewSequnences = function(){
                $scope.newSequences = {};
            }
            $scope.resetNewtask();
            $scope.resetNewSequnences();
            $scope.getProjectDetails = function(){
            projectDetails = $http.get('/api/project/get/'+$scope.projId);
            projectDetails.success(function(resp){
                if (resp!='null')
                    {
                        resp.tasks = Object.keys(resp.tasks);
                        resp.start = timeConverter(resp.start);
                        resp.end = timeConverter(resp.end);
                        resp.updatedWatchers = [];
                        resp.watchers.forEach(function(e){resp.updatedWatchers.push(e)});
                        $scope.project = resp;
                    }
                else
                    $location.path('/pms')
                })
            
            _t = timeConverter(false, true).split('-').slice(0, 3).toString().split(' ').toString();
            getprefix = 'project_'+ $scope.projId+ '_' + _t + '_';
            $scope.generateReport = function(mode){
            if (!mode)
                {
                if ($scope.mode)
                    mode = $scope.mode;
                else
                    mode = 'guntt';
                }
            if (mode=='cal')
                return null;
            else
            {
                data = 'No data available yet!'
                if (!$scope.tasks)
                    data = ''
                $('#projectDetailDiv').html(data);

            }
            $scope.mode=mode;
            $('.tj_table_frame').fadeOut(2000);
            data = localStorage.getItem(getprefix +  mode);
            if ($scope.replan || !data){
            //if (1){
            //console.log('getting')
            projectReport = $http.get('/api/project/report/'+$scope.projId);
            projectReport.success(function(resp){
                localStorage.setItem(getprefix + 'plan', resp.plan);
                localStorage.setItem(getprefix + 'json', JSON.stringify(resp.json));
                localStorage.setItem(getprefix + 'guntt', resp.guntt);
                localStorage.setItem(getprefix + 'resource', resp.resource);
                localStorage.setItem(getprefix + 'profitAndLoss', resp.profitAndLoss);
                data = resp[mode];
                $scope.printable = data;
                //$scope.projectTjData = data;
                $('#projectDetailDiv').html(data);
                $('.tj_table_frame').fadeIn();
                $scope.getProjectDetails();
                $scope.generateProgressChart();
                $scope.getTasksList();
                })
                if ($scope.replan)
                    $scope.replan = false;
            }
            else{
                data = localStorage.getItem(getprefix + mode);
                if (data != 'undefined')
                {
                    $scope.printable = data;
                    $('#projectDetailDiv').html(data);
                    $('.tj_table_frame').fadeIn();
                    $scope.generateProgressChart();
                }
                $scope.getTasksList();
            }
            

         }


            $scope.generateReport();
            }


    $scope.print = function(){
        styles = '<html><head><link rel="stylesheet" href="css/tjmanual.css"> <link rel="stylesheet" href="css/tjreport.css"></head><body>';
        copyright = "<br/><div>Generated by Pooyamehr Fearless&trade;</div></body>"
        myWindow=window.open('','','width=800,height=600');
        myWindow.document.write(styles + $scope.printable + copyright);
        myWindow.document.close(); //missing code
        myWindow.focus();
        myWindow.print(); 
    }
    $scope.getResources = function(){
            $http.get('/api/users').success(function(resp){
                    $scope.resources = resp;
                    });
        }
    $scope.getResources();
    $scope.getTasksList = function(){
        $http.get('/api/task/list/'+$scope.projId).success(function(resp){
                $scope.tasks = resp;
                $scope.calTasks = [];
                for (x in $scope.tasks){
                        ev = $scope.tasks[x];
                        n = {
                                'id':ev.id,
                                'title':ev.title, 
                                'start':timeConverter(ev.start, true), 
                                'end':timeConverter(ev.end, true),

                            };
                        $scope.calTasks.push(n);
                    }
                //if ($scope.mode == 'cal')
                //    $scope.prepareCal();
            });
    }

    $scope.createNewSeq = function(){
        
        $http.put('/api/sequence/add/'+$scope.projId, $scope.newSequences).success(function(resp)
                {
                    if (resp.message == 'OK'){
                        $('#taskSeqModal').modal('hide');
                        $scope.getProjectDetails();

                    }
                });
    }

    $scope.createNewTask = function(){
       if ($scope.newtask.isMilestone)
       {
            $scope.newtask.effort = 0;
            $scope.newtask.resources = [];
            $scope.newtask.start = $scope.newtask.end;
        }


       data = $scope.newtask;
       $http.put('/api/task/add/'+$scope.projId, data).success(function(resp){
                $scope.resetNewtask();
               $('#taskAddModal').modal('hide');
                $scope.replan = true;
                $scope.getTasksList();
                //$scope.generateReport();
               
               });
    }



        $scope.isCurrenclyDependentOf = function(task){
            if (!$scope.editTaskInfo || !task || !$scope.editTaskInfo.depends)
                return false
            for (i=0;i<$scope.editTaskInfo.depends.length;i++)
            {
                t = $scope.editTaskInfo.depends[i];
                if (t.id == task)
                {
                    //$scope.editTaskInfo.updatedDepends.push(t.id);
                    return true
                }
            }
                
        };

        $scope.isCurrenclyResource = function(resource){
            if (!$scope.editTaskInfo || !resource || !$scope.editTaskInfo.resources)
                return false
            for (i=0;i<$scope.editTaskInfo.resources.length;i++)
            {
                t = $scope.editTaskInfo.resources[i];
                if (t.id == resource)
                {
                    //$scope.editTaskInfo.updatedResources.push(t.id);
                    return true
                }
            }
        }

        $scope.generateProgressChart = function(){
            _data = localStorage.getItem(getprefix + 'json');
            if (!_data || _data=='undefined')
                return null;
            data = JSON.parse(_data);
            complete = 0;
            for (i in data)
            {
                info = data[i]
               if (info.type == 'project'){
                    complete = parseInt(info.completion.split('%')[0]);
               }
            }
                progressPyChart.segments[0].value = complete;
                progressPyChart.segments[1].value = 100-complete;
                progressPyChart.update();


        }
        $scope.showCal = function(){
            $scope.mode = 'cal';
            $('.tj_table_frame').fadeOut(1000);
            data = '<div id="calendar" style="display:none"></div>';
            $('#projectDetailDiv').html(data);
            $('#calendar').fadeIn(1000);
        }
        $scope.prepareCal = function(){
            $('#calendar').fullCalendar('destroy');
            $('#calendar').fullCalendar({
                    weekends: true, // will hide Saturdays and Sundays,
                    dow : [0,1,2,3,6],
                    timezone:'Asia/Tehran',
                    hiddenDays: [5], // hide Tuesdays and Thursdays
                    firstDay:6,
                    businessHours:{
                        start: '9:00', // a start time (10am in this example)
                        end: '18:00', // an end time (6pm in this example)
                        dow: [ 1, 2, 3, 4 ]
                    },

                    eventClick: function(calEvent, jsEvent, view) {
                            //alert('Event: ' + calEvent.title);
                            $scope.taskDetail(calEvent.id);
                            

        },
			header: {
				left: 'prev,next today',
				center: 'title',
				right: 'month,agendaWeek,agendaDay'
			},
			editable: true,
			//eventLimit: true, // allow "more" link when too many events
			events: $scope.calTasks,
                // put your options and callbacks here
            })

        }

        $scope.taskDetail = function(taskId) {
            //console.log(taskId);
            $http.get('/api/task/'+taskId).success(function(resp){
                resp.start = timeConverter(Math.max(resp.start, resp.project_start));
                resp.end = timeConverter(Math.min(resp.end, resp.project_end));
                $scope.editTaskInfo = resp;
                $scope.editTaskInfo.updatedResources = [];
                $scope.editTaskInfo.updatedDepends = [];
                $scope.editTaskInfo.updatedResponsibles = [];
                $scope.editTaskInfo.updatedWatchers= [];
                $scope.editTaskInfo.updatedAlternativeResources= [];
                $scope.can_depend = JSON.parse(JSON.stringify($scope.tasks));
                //lets clean tasks that this task is dependent_of
                for (i in $scope.can_depend){
                    if ($scope.can_depend[i].id == resp.id)
                        $scope.can_depend.splice(i, 1);
                }

                for (i in $scope.can_depend){
                    task = $scope.can_depend[i];
                    for (depof in resp.dependent_of){
                        if (resp.dependent_of[depof].id == task.id)
                            $scope.can_depend.splice(i, 1);
                    }
                }

                $('#taskDetailModal').modal('show');

                    });
            }

    $scope.updateProject = function(){
        $scope.projectUpdateInfo = {};
        req = $http.post('/api/project/update/'+$scope.projId, $scope.project);
        req.success(function(resp){
                    if (resp.message == 'OK'){
                        $scope.getProjectDetails();
                        $('#projectEditModal').modal('hide');
                        
                    }
                })

        };
        
    $scope.updateTask = function(taskId){
        $http.post('/api/task/update/'+taskId, $scope.editTaskInfo).success(function(resp){
            $scope.getTasksList();
            $scope.replan = true;
            $scope.getTasksList();
            //$scope.generateReport();
            $scope.editTaskInfo = {};
            $('#taskDetailModal').modal('hide');

        });
    }
    
    $scope.deleteTask = function(taskId){
        if (confirm('Are you sure you want to delete the task?'))
            $http.delete('/api/task/delete/'+taskId).success(function(resp){
                $scope.replan = true;
                $scope.generateReport();
                $scope.getTasksList();
                $('#taskDetailModal').modal('hide');
                    });


    };

        });



fearlessApp.controller('sequenceDetailCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular){

        });


fearlessApp.controller('collectionCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){


        $scope.activateVideo = function(vid){
        var _v = "video_"+vid.toString();
        $timeout(function(){
        try {
            videojs(_v, {}, function(){
          // Player (this) is initialized and ready.
            })}

        catch(e){
            console.log(e)
            }
        }, 100);

        }


        $scope.$parent.page = 'ams';
        $scope.collection = {};
        $scope.collection.assets = [];
        $scope.newSubCollection = {};
        ci = $routeParams.collectionId;
        Dropzone.autoDiscover = false;
        $scope.dropzone = new Dropzone("#my-awesome-dropzone", {
            init: function() {
                this.on("addedfile", function(file) {
                    //console.log("Added file."); 
                    });
                this.on("complete", function(file) {
                    $timeout(function(){
                        $scope.dropzone.removeFile(file);
                        }, 1000);
                    });
                this.on("success", function(file, resp) {
                    $scope.collection.assets.push(resp);
                    $scope.$apply();

                    });
                this.on("queuecomplete", function(file, resp) {
                        console.log('all complete')
                        $scope.getCollectionDetails();
                        $scope.$apply();
                    });
                this.on("thumbnail", function(file, dataUrl) {
                        //$scope.dropzone.options.url = 'ok';
                        //$scope.$apply();

                    });
            },
            url: 'NULL',
            //autoDiscover: false,
            //autoProcessQueue: false,
            method:'PUT',
            parallelUploads: 4,
            maxFilesize: 8000,
            maxThumbnailFilesize: 10,
            uploadMultiple:false,
        });

        $scope.getCollectionDetails = function(){
            req = $http.get('/api/collection/'+ci);
            req.success(function(resp){
                    $scope.collection = resp;
                    $scope.attachurl = "/api/asset/save/"+resp.repository.name+"?collection_id="+resp.id+"&multipart=true";
                    $scope.dropzone.options.url = $scope.attachurl;

                })
        }
        $scope.createNewSubCollection = function(){
            $scope.newSubCollection.parent_id = $scope.collection.id;
            $scope.newSubCollection.repository_id = $scope.collection.repository.id;
            tarray = $scope.collection.path.split('/');
            $scope.newSubCollection.template = tarray[tarray.length-1];
            req = $http.put('/api/collection/add', $scope.newSubCollection);
            req.success(function(resp){
                if (resp.message == 'OK'){
                    $('#collectionAddModal').modal('hide');
                    $scope.getCollectionDetails();
                }
                else{
                    alert(resp.info);
                }
                
                })
        }







        });
//////////////////////////////////////////////////////

$(document).ready(function(){
    $('input').on('input', function() {
        alert('Text1 changed!');
    });




});


/////////////////////////////////////////////////

