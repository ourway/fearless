var fearlessApp = angular.module('fearlessApp', ['ngRoute', 'ngResource', 'ngCookies', 'restangular', 'ui.grid']);

fearlessApp.factory('authFactory', function($resource) {
  return $resource('/api/auth/:what',
    { what:'@action' },
    { save: { method: 'POST' }}
  );
});

function timeConverter(UNIX_timestamp){
 var a = new Date(UNIX_timestamp*1000);
 var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
     var year = a.getFullYear();
     var month = months[a.getMonth()];
     var date = a.getDate();
     var hour = a.getHours();
     var min = a.getMinutes();
     var sec = a.getSeconds();
     var time = date +  month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
     return time;
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
             .when('/report', {

                templateUrl: 'pages/crew/report.html',
                controller: 'reportCtrl'
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
	fearlessApp.controller('mainController', function($scope, $rootScope, $cookies,$http,
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

        prom = authFactory.save({}, $scope.loginInfo, function(resp){
                // Here we need an anomality prevention method:
                $scope.login_wait = resp.wait;
                $scope.AuthRespMessage = resp.message;
                $scope.AuthRespInfo = resp.info;
                if (resp.message == 'error') {
                    $scope.loginInfo.password = null;
                    $scope.enable_signup = true;

                }
                setTimeout(function(){$scope.login_wait=null}, resp.wait);
               if (resp.message=='success' && $scope.loginInfo.action=='login') //green light
                    {
                        localStorage.setItem('userid', resp.id);
                        localStorage.setItem('username', resp.firstname);
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

            if (resp.message=='success' && $scope.loginInfo.action=='signup') //green light
            {
                window.location =  '#auth/login/?m=' + btoa(resp.info)  ;
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
            localStorage.setItem('userid', '');
            localStorage.setItem('username', '');
            localStorage.setItem('avatar', '');
            $scope.userInfo.logged_in = false;
            $scope.userInfo.username = null;
            $scope.userInfo.userid = null;
            $http.post('/api/auth/logout');
            //$scope.userInfo.logged_in = true;

        }
    //Check if user is logged in
    $scope.is_logged_in = function(){
        var userid = localStorage.getItem('userid');
        var username = localStorage.getItem('username');
       if (userid && username)
            {
                $scope.userInfo.username = username;
                $scope.userInfo.userid = userid;
                $scope.userInfo.logged_in = true;
                return true
            }
        else {
        console.log(userid, username)
           // This is where I redirect user to login page if she/he is unauthenticated
              $scope.userInfo.username = null;
              $scope.userInfo.userid = null;
              $scope.userInfo.logged_in = false;
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

fearlessApp.controller('profileCtrl', function($scope, $rootScope, $http, $location){
        
        userInfoReq = $http.get('/api/db/user/'+$scope.$parent.userInfo.userid);
        userInfoReq.success(function(resp){
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
        x = $http.post('/api/db/user/'+$scope.$parent.userInfo.userid, $scope.user); //send it
        x.success(function(resp){
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
                });
    }

});






fearlessApp.controller('reportCtrl', function($scope, $rootScope, $http, $location){

        });

fearlessApp.controller('projectCtrl', function($scope, $rootScope, $http, $location){
    
    //$scope.newProjectStartDate = new Date();
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
                    });
        }


        });




fearlessApp.controller('projectDetailCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular){
            $scope.projId = $routeParams.projId;
            $scope.getProjectDetails = function(){
            projectDetails = $http.get('/api/project/get/'+$scope.projId);
            projectDetails.success(function(resp){
                resp.tasks = Object.keys(resp.tasks)
                $scope.project = resp;
                })

            projectReport = $http.get('/api/project/report/'+$scope.projId);
            projectReport.success(function(resp){
                $('#projectDetailDiv').html(resp.report);
                $('.tj_table_frame').fadeIn();
                })
            }

        $scope.getResources = function(){
            $http.get('/api/db/user').success(function(resp){
                    $scope.resources = resp;
                    });
        }

        $scope.createNewTask = function(){
           te = $scope.newTaskEffort;
           tt = $scope.newTaskTitle;
           tm = $scope.newTaskManager;
           data = {'effort':te, 'title':tt, 'responsible':tm}
           $http.put('/api/task/add/'+$scope.projId, data).success(function(resp){
                    $scope.getProjectDetails();
                    $scope.newTaskEffort = null;
                    $scope.newTaskTitle=null;
                    $scope.newTaskManager=null;
                   $('#taskAddModal').modal('hide');
                   
                   });
        }
        

        });
