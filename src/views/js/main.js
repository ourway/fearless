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
        console.log(toTitleCase(task));
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
            .when('/pms', {

                templateUrl: 'pages/pms/index.html',
                controller: 'projectCtrl'
            })
            .when('/pms/:projId', {

                templateUrl: 'pages/pms/detail.html',
                controller: 'projectDetailCtrl'
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
        
        if (validateEmail($scope.loginInfo.email) == false)
                return null;
                $scope.AuthRespInfo = null;

        prom = $http.post('/api/auth/login', $scope.loginInfo);
        prom.success(function(resp){
                $scope.login_wait = resp.wait;
                $scope.AuthRespMessage = resp.message;
                $scope.AuthRespInfo = resp.info;
                if (resp.message == 'error') {
                    $scope.loginInfo.password = null;
                    $scope.enable_signup = true;
                }
                setTimeout(function(){$scope.login_wait=null}, resp.wait);


               if (resp.message=='success') //green light
                    {

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
            resp = resp[0]
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
                localStorage.setItem('username', $scope.user.firstname);
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






fearlessApp.controller('reportCtrl', function($scope, $rootScope, $http, $location){


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
                    cellTemplate: '<div>  <a class="btn" href="#pms/{{row.entity.id}}"><span class="glyphicon glyphicon-folder-close"></span> {{row.entity.name}}</a></div>'
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
           sd = $scope.newProjectStartDate;
           ed = $scope.newProjectEndDate;
           pn = $scope.newProjectName;
           pl = $scope.newProjectLeader;
           data = {start:sd, end:ed, name:pn, lead_id:pl}
           $http.put('/api/db/project', data).success(function(resp){
                   $scope.getProjData();
                    $scope.newProjectStartDate = null;
                    $scope.newProjectEndDate = null;
                    $scope.newProjectName=null;
                    $scope.newProjectLeader=null;
                   $('#projectAddModal').modal('hide');
                   
                   });
        }

        $scope.getResources = function(){
            $http.get('/api/db/user').success(function(resp){
                    $scope.resources = resp;
                    }).error(function(resp, status){
                        if (status == 401)
                            $location.path('auth/login');
                        });
        }


        });



fearlessApp.controller('userAccessCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular){
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
                    label: "Complete"

                },
                 {
                    value: 100,
                    color:"#ccc",
                    highlight: "#555",
                    label: "Remaining"
                },

            ]

            var ctx = $("#progressChart").get(0).getContext("2d");
            var progressPyChart = new Chart(ctx).Pie(progressData, progressChartOptions);

            $scope.projId = $routeParams.projId;
            $scope.toTitleCase = toTitleCase;
            $rootScope.title = "Project " + $scope.projId + " - Fearless";
            $scope.timeConverter = timeConverter;
            $scope.newtask = {};
            $scope.resetNewtask = function(){
                $scope.newtask = {};
                $scope.newtask.start = timeConverter();
                $scope.newtask.end = timeConverter();
                $scope.newtask.priority = 500;
                $scope.newtask.effort = null;
            }
            $scope.resetNewtask();
            $scope.getProjectDetails = function(){
            projectDetails = $http.get('/api/project/get/'+$scope.projId);
            projectDetails.success(function(resp){
                if (resp!='null')
                    {
                        resp.tasks = Object.keys(resp.tasks)
                        $scope.project = resp;
                    }
                else
                    $location.path('/pms')
                })

            getprefix = 'project_'+ $scope.projId+ '_' + timeConverter() + '_';
            $scope.generateReport = function(mode){
            if (!mode)
                {
                if ($scope.mode)
                    mode = $scope.mode;
                else
                    mode = 'guntt';
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
                $('#projectDetailDiv').html(data);
                $('.tj_table_frame').fadeIn();
                $scope.generateProgressChart();
                $scope.getTasksList();
                })
                if ($scope.replan)
                    $scope.replan = false;
            }
            else{
                data = localStorage.getItem(getprefix + mode);
                $scope.printable = data;
                $('#projectDetailDiv').html(data);
                $('.tj_table_frame').fadeIn();
                $scope.generateProgressChart();
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
            $http.get('/api/db/user').success(function(resp){
                    $scope.resources = resp;
                    });
        }
    $scope.getTasksList = function(){
        $http.get('/api/task/list/'+$scope.projId).success(function(resp){
                $scope.tasks = resp;
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
                $scope.generateReport();
               
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
                resp.resources.forEach(function(e){$scope.editTaskInfo.updatedResources.push(e.id)});
                resp.depends.forEach(function(e){$scope.editTaskInfo.updatedDepends.push(e.id)});
                resp.responsibles.forEach(function(e){$scope.editTaskInfo.updatedResponsibles.push(e.id)});
                resp.watchers.forEach(function(e){$scope.editTaskInfo.updatedWatchers.push(e.id)});
                resp.alternative_resources.forEach(function(e){$scope.editTaskInfo.updatedAlternativeResources.push(e.id)});
                $('#taskDetailModal').modal('show');

                    });
            }
    $scope.updateTask = function(taskId){
        $http.post('/api/task/update/'+taskId, $scope.editTaskInfo).success(function(resp){
            $scope.getTasksList();
            $scope.replan = true;
            $scope.getTasksList();
            $scope.generateReport();
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
