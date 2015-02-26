var fearlessApp = angular.module('fearlessApp', ['ngRoute', 'ngResource', 'restangular',
        'ui.grid', 'ngSanitize', 'ui.bootstrap', 'checklist-model', 'blueimp.fileupload', 
        'siyfion.sfTypeahead', 'bootstrap-tagsinput', 'ngAnimate', 'flow']);

/*
fearlessApp.factory('$exceptionHandler', function () {
    return function (exception, cause) {
        console.log(exception.message, cause);
    };
});
*/

fearlessApp.config(function($sceDelegateProvider) {
  $sceDelegateProvider.resourceUrlWhitelist([
    'self',
  ]);
  // The blacklist overrides the whitelist so the open redirect here is blocked.
  $sceDelegateProvider.resourceUrlBlacklist([
  ]);
});




fearlessApp.factory('messageService', function() {
    itemsService = {};
    itemsService.messages = [];
    itemsService.getUnreadCount = function(){
        unread = 0;
        itemsService.messages.forEach(function(item){
                if (!item.read)
                    unread+=1;
                });
        return unread;
    };    
    return itemsService;
});

fearlessApp.factory('authFactory', function($resource) {
  return $resource('/api/auth/:what',
    { what:'@action' },
    { save: { method: 'POST' }}
  );
});

fearlessApp.filter('range', function() {
  return function(input, total) {
    total = parseInt(total);
    for (var i=0; i<total; i++)
      input.push(i);
    return input;
  };
});


var tags = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  prefetch: {
    url: '/api/db/tag',
  }
});
tags.initialize();


var resources = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('fullname'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  prefetch: {
    url: '/api/users',
  }
});
resources.initialize()


function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}



function pad(num, size) {
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}

var substringMatcher = function(strs) {
  return function findMatches(q, cb) {
    var matches, substrRegex;
 
    // an array that will be populated with substring matches
    matches = [];
 
    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');
 
    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        // the typeahead jQuery plugin expects suggestions to a
        // JavaScript object, refer to typeahead docs for more info
        matches.push({ value: str });
      }
    });
 
    cb(matches);
  };
};




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
            console.log(target)
        if (target.length)
            target[0].click();
        //console.log(angular.element('#projectDetailContainer').scope.taskInfo);
    }



	fearlessApp.config(function($routeProvider, $locationProvider) {
		$routeProvider
			// route for the home page
			.when('/', {
				templateUrl : 'pages/home.html',
				controller  : 'homeCtrl'
			})
			.when('/welcome', {
				templateUrl : 'pages/welcome.html',
				controller  : 'welcomeCtrl'
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
                controller: 'sequenceDetailCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
            .when('/profile', {

                templateUrl: 'pages/auth/profile.html',
                controller: 'profileCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search

            })
            .when('/user/:userId', {

                templateUrl: 'pages/auth/profile.html',
                controller: 'profileCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search

            })
            .when('/report', {

                templateUrl: 'pages/crew/report.html',
                controller: 'reportCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
             .when('/ua', {

                templateUrl: 'pages/auth/access.html',
                controller: 'userAccessCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
             .when('/ams/c/:collectionId', {
                templateUrl: 'pages/ams/collection.html',
                controller: 'collectionCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
             .when('/ams/a/:assetId', {
                templateUrl: 'pages/ams/asset.html',
                controller: 'assetCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
             .when('/ams', {
                templateUrl: 'pages/ams/index.html',
                controller: 'assetsIndexCtrl',
                 reloadOnSearch: true // dont reload the page on $location.search
            })
             .when('/pms/t/:taskId', {
                templateUrl: 'pages/pms/task.html',
                controller: 'taskDetailCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
             .when('/tasks', {
                templateUrl: 'pages/pms/tasks.html',
                controller: 'tasksCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
             .when('/404', {
                templateUrl: 'pages/errors/404.html',
                controller: 'errorsCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })
             .when('/messages', {
                templateUrl: 'pages/messages/index.html',
                controller: 'messagesCtrl',
                 reloadOnSearch: true // dont reload the page on $location.search

            })
             .when('/ur', {

                templateUrl: 'pages/crew/user_reports.html',
                controller: 'userReportsCtrl',
                 reloadOnSearch: false // dont reload the page on $location.search
            })

    })

function choose(choices) {
  var index = Math.floor(Math.random() * choices.length);
  return choices[index];
}

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
        $scope.comments = {};
        $scope.newComment = {};
        $scope.login_init = function() {
            //
        }

        $scope.setResourceTags = function(obj){
            $('.resourceSelect').tagsinput({
            itemValue: 'id',
            itemText: 'lastname',
              typeaheadjs: {
                name: 'resources',
                displayKey: 'fullname',
                source: resources.ttAdapter()
              }
            });
            $('#newproj_watchers').on('itemAdded', function(event) {
                    
              // event.item: contains the item
            });
        }


        $scope.prettyDate = function(time){
            var _d = moment.unix(time); 
            return moment.duration(_d-moment()).humanize();

        }
        $scope.isASCII = function(str, extended) {
            data = (extended ? /^[\x00-\xFF]*$/ : /^[\x00-\x7F]*$/).test(str);
            return data;
        }

        $scope.getReadableFileSizeString = function(fileSizeInBytes) {
            var i = -1;
            var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB', 'EB', 'ZB', 'YB'];
            do {
                fileSizeInBytes = fileSizeInBytes / 1024;
                i++;
            } while (fileSizeInBytes > 1024);
            return Math.max(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
        };


        $scope.getComments = function(){
            req = $http.get('/api/db/comment/'+$scope.comment_id+'?key=item&list=true');
            req.success(function(resp){
                    $scope.comments[$scope.comment_id] = resp;
                })
        }
        $scope.addComment = function(){
            $scope.newComment.user_id = $scope.userInfo.userid;
            $scope.newComment.item = $scope.comment_id;
            if ($scope.userInfo.userid && $scope.newComment.content){
                req = $http.put('/api/db/comment', $scope.newComment);
                req.success(function(resp){
                        if (!$scope.comments[$scope.comment_id])
                            $scope.comments[$scope.comment_id] = [];
                        $scope.comments[$scope.comment_id].splice(0, 0, $scope.newComment);
                        $scope.newComment = {};
                    })

            }

        }
        $scope.getGroups = function(){
            req = $http.get('/api/db/group').success(function(resp){
                    $scope.groups = resp;
                });
        }
        $scope.getDeps = function(){
            req = $http.get('/api/db/departement').success(function(resp){
                    $scope.departements = resp;
                });
         
        }

        $scope.getExps = function(){
            req = $http.get('/api/db/expert').success(function(resp){
                    $scope.experts = resp;
                });
         
        }
        $scope.sendmail = function(mail){
            m = $http.post('/api/sendmail', mail);
        }

        $scope.persianDate = function(d, mode){
        // d is like 2015-1-1
        list = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 
                'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
        if (d)
            a = new Date(d)  // 1000 is for unix time date;
        else
            a = new Date();

        j = new JDate(a);
        result = [j.jdate[2], list[j.jdate[1]-1], j.jdate[0]]
        if (mode!=null)
            return result[mode];
        else
            return result[0] + ' ' + result[1] + ' ' + result[2];
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
                        
                    //console.log(resp);

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
                            //console.log(next_page)
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
                $scope.user = $scope.userInfo;

                userInfoReq = $http.get('/api/users');

                userInfoReq.error(function(resp, code){
                        if (code==401)
                        {
                            $location.path('/auth/login')
                            return
                        }
                        });
                userInfoReq.success(function(resp, code){
                        $scope.resources = resp;
                        _members = {};
                        for (i in resp){
                            _members[resp[i].id] = resp[i];
                        }
                        $scope.members = _members;
                    });

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


      $scope.go = function (path) {
          $location.path( path );
        };




	});


	fearlessApp.controller('aboutController', function($scope) {
		$scope.message = $scope.appName + '! I am an about page.';
	});


	fearlessApp.controller('welcomeCtrl', function($scope) {
		$scope.message = 'A heroestic project management solution';
	});



fearlessApp.controller('homeCtrl', function ($scope, $http, $location, $interval, $rootScope) {

        $rootScope.title = 'Home';
		messages = [
                    "Life is what happens to you while you're busy making other plans.",
                    'A goal without a plan is just a wish!',
                    'By failing to prepare, you are preparing to fail.',
                    "You can't plow a field simply by turning it over in your mind.",
                    "If you don't know where you are going, you'll end up someplace else.",
                    "Plans are useless, but planning is indispensable.",
                    "Someone's sitting in the shade today because someone planted a tree a long time ago.",
                    "Always, Always have a plan",
                    "You need to stop getting into situations where all your options are potentially bad.",
                    "The time to repair the roof is when the sun is shining.",
                    "Do not let the universe surprise you!",
                    "Fearless is worrying, only in a productive, proactive form"
                 ];

        $scope.message = choose(messages);
        $interval(function(){
            // every 30 secs
		    $scope.message = choose(messages);
            }, 30000);

    if (!localStorage.getItem('WelcomePageVisited')){

        $http.get('/api/db/project?count=true').success(function(resp){
                if (resp.count==0){
                    localStorage.setItem('WelcomePageVisited', 1);
                    $location.path('/welcome');
                }
            });
    }


    $scope.getUserTasks = function(){
        if (!$scope.$parent.user.logged_in)
            return null;
        uid = $scope.$parent.user.userid;
        $http.get('/api/taskcard/today').success(function(resp){
                $scope.user.tasksForToday = resp;
                })
    }

    $scope.getUnfinishedTasks = function(){
        if (!$scope.$parent.user.logged_in)
            return null;
        uid = $scope.$parent.user.userid;
        $http.get('/api/taskcard/before').success(function(resp){
                $scope.user.unfinishedTasks = resp;
                })
    }

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
    $scope.accounting = accounting; 
    $scope.$parent.getGroups();
    $scope.$parent.getDeps();
    $scope.$parent.getExps();
    $scope.print = function(){
        $scope.printable = $('#invoice_print_area').html();
        styles = '<html><head><title>Fearless Monthly Invoice</title><link rel="stylesheet" href="css/bootstrap.min.css"> <link rel="stylesheet" href="css/main.css"> </head><body>';
        copyright = "<br/><div>Generated by Pooyamehr Fearless&trade;</div></body>"
        myWindow=window.open('','','width=1024,height=1024');
        _final = styles + $scope.printable;
        myWindow.document.write(_final);
        myWindow.document.close(); //missing code
        myWindow.focus();
        myWindow.print(); 
    }


        $scope.roundG = function(num){
            return Math.round(num);
        }
        $scope.ceilG = function(a){
            if (a > 0)
                return a;
            else
                return 0;
        }

        userInfoReq = $http.get('/api/db/user/'+userId);
        userInfoReq.success(function(resp){
            //resp = resp[0];
            resp.agreement_start = new Date(resp.agreement_start*1000);
            resp.agreement_end = new Date(resp.agreement_end*1000);
            delete resp.created_on;
            delete resp.modified_on;
            $scope.user = resp; 
            $http.get('/api/db/user/'+userId+'?field=grps&list=true').success(function(grps){
                $scope.user.grps = grps; 
                })
            $http.get('/api/db/user/'+userId+'?field=dps&list=true').success(function(dps){
                $scope.user.dps = dps;
                })
            $http.get('/api/db/user/'+userId+'?field=exps&list=true').success(function(exps){
                $scope.user.exps = exps;
                })
            //console.log(resp);
            });
        userInfoReq.error(function(a, b, c, d){
                console.log(a, b, c, d);
            });

        userTasksReq = $http.get('/api/db/user/'+userId+'?field=tasks&list=true');
            userTasksReq.success(function(tasks){
                $scope.userTasks = tasks; 
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

    $scope.mailInvoice = function(){
                mail = {};
                invoice = '<div style="margin:5px;font-size:10px;border:1px solid #333;padding:5px;background:#f8f8f8">' + $('#invoice_print_area').html() + '</div>';
                mail['message'] = 'Hello <b>'+ $scope.user.firstname +'</b>!<br/>'
                mail['message']+= 'Here is your monthly salary document.<br/>';
                mail['message']+= invoice;
                mail['to'] = $scope.user.email;
                //mail['cc'] = ['rodmena@me.com', 'sara_kayvan@hotmail.com', 'hamid2117@gmail.com'];
                mail['subject'] = 'Pooyamehr Financial Departement - Salary Document';
                if (confirm('Are you sure you want to send invoice to ' + $scope.user.email + ' ?'))
                    $scope.$parent.sendmail(mail);
    }

    $scope.updateUserInformation = function(){
        $scope.user.rate = ($scope.user.monthly_salary / $scope.user.monthly_working_hours) * 8;
        $scope.$parent.members[$scope.user.id] = $scope.user;
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
                //$scope.$parent.sendmail(mail);
                }
            });
        // lets update groups or other list type data:
         y = $http.post('/api/user/'+userId+'/groups', {'groups':$scope.user.grps});
         z = $http.post('/api/user/'+userId+'/departements', {'departements':$scope.user.dps});
         x = $http.post('/api/user/'+userId+'/expertise', {'expertise':$scope.user.exps});
    }

});






fearlessApp.controller('reportCtrl', function($scope, $rootScope, $http, $timeout, $location){
        $rootScope.title = "User Reports - Fearless";
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
    $scope.newProject = {};
    $scope.newProject.start = new Date();
    $rootScope.title = "Projects - Fearless";
    $scope.timeConverter = timeConverter;

    $scope.getProjsData = function(){
        $http.get('/api/project').success(function(resp){
            $scope.involving_projects = resp;
            });
    }


        $scope.createNewProject = function(){
        $scope.newProject.lead_id = $scope.newProject.leader.id;
           $http.put('/api/project/add', $scope.newProject).success(function(resp){
                   $scope.getProjsData();
                    $scope.newProject = {};
                   $('#projectAddModal').modal('hide');
                   });
        }




        });



fearlessApp.controller('userAccessCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular){
        $rootScope.title = "Members - Fearless";
        $scope.$parent.page = 'auth';
        $scope.getUsers = function(){
            $http.get('/api/db/user').success(function(resp){
                    $scope.users = resp;
                    $scope.paylist = [];
                    for (i in resp){
                        _user = resp[i];
                        if (_user.monthly_present_hours)
                            $scope.paylist.push(_user);
                    }

                    }).error(function(resp, status){
                        if (status == 401)
                            $location.path('auth/login');
                        });
        }

        $scope.roundG = function(num){
            return Math.round(num);
        }
        $scope.ceilG = function(a){
            if (a > 0)
                return a;
            else
                return 0;
        }
        $scope.accounting = accounting;

        $scope.calculate_salery = function(user, rawMode){
                result = $scope.ceilG(user.monthly_salary - 
                ((user.monthly_salary/user.monthly_working_hours)*user.monthly_present_hours*(user.retention+user.payroll_tax+user.insurance_deductions)/100 + 
                ($scope.roundG((user.monthly_salary/user.monthly_working_hours)*($scope.ceilG(user.monthly_working_hours-user.monthly_present_hours))))));
                //$scope.final_payment+=result;
                if (rawMode)
                    return result;
                else
                    return accounting.formatNumber(result);

        }

        $scope.final_payment = function(){
            result = 0;
            for (i in $scope.users){
                result += $scope.calculate_salery($scope.users[i], true);
            }
            return accounting.formatNumber(result);
        
        };


        $scope.print = function(){
            $scope.printable = $('#salary_sumup').html();
            styles = '<html><head><title>Fearless Salary Brief</title><link rel="stylesheet" href="css/bootstrap.min.css"> <link rel="stylesheet" href="css/main.css"> </head><body>';
            copyright = "<br/><div>Generated by Pooyamehr Fearless&trade;</div></body>"
            myWindow=window.open('','','width=1024,height=1024');
            _final = styles + $scope.printable;
            myWindow.document.write(_final);
            myWindow.document.close(); //missing code
            myWindow.focus();
            myWindow.print(); 
        }

    $scope.mailSumpup = function(){
                mail = {};
                invoice = '<div style="margin:5px;font-size:10px;border:1px solid #333;padding:5px;background:#f8f8f8">' + $('#salary_sumup').html() + '</div>';
                mail['message'] = 'Hello <b> Dear Pooyamehr financial officer</b>!<br/>'
                mail['message']+= 'Here is a sum up of crew salaries, Please review:<br/>';
                mail['message']+= invoice;
                //mail['to'] = 'farsheed.ashouri@gmail.com';
                mail['to'] = ['hamid2177@gmail.com'];
                mail['subject'] = 'گزارش کارکرد ماه ' + $scope.$parent.persianDate(null, 1) + ' پروژه پادشاه آب';
                if (confirm('Are you sure you want to send sumpup?'))
                    $scope.$parent.sendmail(mail);
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

        $scope.replan = true;
        $scope.timeConverter = timeConverter;

        $scope.burndownChart = new Morris.Line({
          element: 'burndown_chart_div',
          xkey: 'date',
          events:[timeConverter()],
          data:[{'date':new Date().toDateString(), 'value':0, 'expected':0, 'Offset':0}],
          ykeys: ['value', 'expected', 'Offset'],
          lineColors: ['#5bc0de', 'green', '#c2aeae'],
          lineWidth: ['5', '1', '1'],
          labels: ['Completed', 'Expected', 'Offset'],
          fillOpacity:1,
          goals: [0, 100],
          parseTime:true,
          hideHover:'auto',
          resize:true,
        });

        $scope.progressPyChart = Morris.Donut({
          element: 'progress_chart_div',
          data: [
            {label: "Completed", value: 0},
            {label: "Remaining", value: 100},
          ],
          colors:['#5bc0de','lightgrey'],
          postUnits:'%',
          hideHover:'auto',
          resize:true
        });


            $scope.projId = $routeParams.projId;
            newTask = {};
            $scope.$watch($scope.projId, function(){
                    $scope.getProjectDetails();
                    $scope.getTasksList();
                    $scope.generateReport();

                    })
            $scope.toTitleCase = toTitleCase;
            $rootScope.title = "Project " + $scope.projId + " - Fearless";
            $scope.timeConverter = timeConverter;
            //$scope.replan = true;
            $scope.newtask = {};
            $scope.resetNewtask = function(){
                $scope.newtask = {};
                $scope.newtask.start = new Date();
                $scope.newtask.end = new Date();
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
                            //resp.tasks = Object.keys(resp.tasks);
                            resp.start = new Date(resp.start*1000);
                            resp.end = new Date(resp.end*1000);
                            $rootScope.title = resp.name + ' - ' + 'Fearless'
                            resp.updatedWatchers = [];
                            getTags = $http.get('/api/db/project/'+$scope.projId+'?field=tgs');
                            getTags.success(function(tgs){
                                resp.tgs = tgs;
                                })
                            resp.watchers.forEach(function(e){resp.updatedWatchers.push(e)});
                            $scope.project = resp;
                            $scope.projectBackup = resp;
                            if ($scope.$parent){
                                $scope.$parent.comment_id = resp.uuid;
                                $scope.$parent.getComments();
                                }




                            //$scope.generateReport('guntt');
                        }
                    else
                        $location.path('/pms')
                })
            projectDetails.error(function(resp){
                    $location.path('/404')
                    });
            };

            
            _t = timeConverter(false, true).split('-').slice(0, 3).toString().split(' ').toString();
            getprefix = 'project_'+ $scope.projId+ '_' + _t + '_';
            $scope.generateReport = function(mode){


                el = document.getElementById('canvasloader-container');
                if (el){
                    var cl = new CanvasLoader('canvasloader-container');
                    cl.setColor('#2aabd2'); // default is '#000000'
                    cl.setShape('spiral'); // default is 'oval'
                    cl.setDiameter($('#projectDetailDiv').width()*0.4); // default is 40
                    cl.setDensity(20); // default is 40
                    cl.setRange(2); // default is 1.3
                    cl.setFPS(24); // default is 24
                    cl.show(); // Hidden by default
                }

            $('#canvasloader-container').fadeIn();
            projectReport = $http.get('/api/project/report/'+$scope.projId+'/plan');
            projectReport.success(function(resp){
                $scope.prepareCal();
                $scope.showCal();

                })
         }


    $scope.print = function(){
        styles = '<html><head><link rel="stylesheet" href="css/tjmanual.css"> <link rel="stylesheet" href="css/tjreport.css"></head><body>';
        copyright = "<br/><div>Generated by Pooyamehr Fearless&trade;</div></body>"
        myWindow=window.open('','','width=1280,height=960');
        myWindow.document.write(styles + $scope.printable + copyright);
        myWindow.document.close(); //missing code
        myWindow.focus();
        myWindow.print(); 
    }

    $scope.getTasksList = function(){
        gettask = $http.get('/api/task/list/'+$scope.projId);
        gettask.success(function(resp){
                if (!resp)
                    return null;
                $scope.tasks = resp;
                //$scope.tasksBackup = [];
                if($scope.$parent)
                    $scope.resources = $scope.$parent.resources;
                //$scope.project.tasks = resp;
                $scope.calTasks = [];
                for (x in $scope.tasks){
                        ev = $scope.tasks[x];
                        if (ev.effort>0){
                        n = {
                                'id':ev.id,
                                'title':ev.title, 
                                'start':new Date(ev.start*1000), 
                                'end':new Date(ev.end*1000),

                            };
                        $scope.calTasks.push(n);
                        }
                    }

                $scope.generateBurndownChart();
                $scope.generateProgressChart();
                //if ($scope.mode == 'cal')
                //    $scope.prepareCal();
            });
        gettask.error(function(resp){
                location.reload();
                })
    }

    $scope.createNewSeq = function(){
        
        $http.put('/api/sequence/add/'+$scope.projId, $scope.newSequences).success(function(resp)
                {
                    if (resp.message == 'OK'){
                        $('#taskSeqModal').modal('hide');
                        $scope.generateReport();

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
                //$scope.getProjectDetails();
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
                  data =  [
                    {label: "Completed", value: complete},
                    {label: "Remaining", value: 100-complete},
                  ]
                $scope.progressPyChart.setData(data);
            
        }

        $scope.generateBurndownChart = function(){
            _tasks = $scope.tasks;

            _data = localStorage.getItem(getprefix + 'trace');
            if (!_data || _data=='undefined')
                return null;
            data = JSON.parse(_data);
            complete = 0;
            lables = data.Date;
            keys = Object.keys(data);
            chartData = [];
            for (i in lables){
                label = lables[i];
                key = keys[2];
                if (key != 'Date'){
                    value = data[key][i];
                    ldate = moment(label).toDate().getTime();
                    complete = parseInt(value);

                    }
                pointDate =  moment(label).toDate();
                _behind_list = [];
                _task_efforts = [];
                for (_t in _tasks){
                    taskEndDate = moment.unix(_tasks[_t].end).toDate();
                    _task_efforts.push(_tasks[_t].effort);
                    if (taskEndDate<pointDate)
                        _behind_list.push(_tasks[_t].effort);
                    else
                        {
                            duration = (moment.unix(_tasks[_t].end)-moment.unix(_tasks[_t].start))/3600000;
                            tillnow = (moment(pointDate)-moment.unix(_tasks[_t].start))/3600000;
                            if (tillnow>0){
                                expected_progress = (tillnow/duration);
                                _behind_list.push(_tasks[_t].effort*expected_progress);
                                }
                        }
                    }
                expected = value;
                if (_tasks){
                    var total_efforts = _task_efforts.reduce(function(pv, cv) { return pv + cv; }, 0);
                    var expected_efforts = _behind_list.reduce(function(pv, cv) { return pv + cv; }, 0);
                    expected = (expected_efforts/total_efforts) * 100;
                }
                chartData.push({
                        date:ldate, value:complete, 
                        expected:parseInt(expected),
                        Offset:complete - parseInt(expected)
                        })

            }
            if (chartData.length>0)
            {
                $scope.burndownChart.setData(chartData);
            }

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
            gettask = $http.get('/api/task/'+taskId);
            gettask.success(function(resp){
                newBackup = [];
                $scope.tasks.forEach(function(e){
                        if (e.id==taskId){
                            _bk = JSON.parse(JSON.stringify(resp))
                            newBackup.push(_bk);
                        }
                    })
                $scope.tasksBackup = newBackup;
                resp.start = new Date(resp.start*1000);
                resp.end = new Date(resp.end*1000);
                //resp.start = timeConverter(Math.max(resp.start, resp.project_start));
                //resp.end = new Date(Math.min(resp.end, resp.project_end)*1000);
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
            gettask.error(function(resp){
                location.reload();
                });
            }

    $scope.updateProject = function(data){
        $scope.projectUpdateInfo = {};
        if (!data)
            data = $scope.project;
        req = $http.post('/api/project/update/'+$scope.projId, data);
        req.success(function(resp){
                    if (resp.message == 'OK'){
                        $scope.generateReport();
                        $('#projectEditModal').modal('hide');
                        
                    }
                })

        };
        
    $scope.updateTask = function(taskId, data){
        if (!data)
            data = $scope.editTaskInfo;
        $http.post('/api/task/update/'+taskId, data).success(function(resp){
            $scope.replan = true;
            $scope.getTasksList();
            for (i in $scope.tasks){
                _t = $scope.tasks[i];
                if (_t.id == data.id)
                    $scope.tasks[i] = data;
            }
            $scope.editTaskInfo = {};
            $('#taskDetailModal').modal('hide');

        });
    }
    
    $scope.deleteTask = function(taskId){
        if (confirm('Are you sure you want to delete the task?'))
        {
            $http.delete('/api/task/delete/'+taskId).success(function(resp){
                $scope.replan = true;
                $scope.getTasksList();
                //$scope.generateReport();
                $('#taskDetailModal').modal('hide');
                    });

        }


    };

    $scope.isMyTask = function(task){
        result = false;
        task.resources.forEach(function(e){
                if (e.id==$scope.$parent.userInfo.userid) 
                    result = true;
            })
        return result;
    };

    $scope.isTaskLate = function(task){
        if (task.complete != 100)
            result = new Date() > new Date(task.end*1000);
        return result;
    };

        });



fearlessApp.controller('sequenceDetailCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular){

        });


fearlessApp.controller('assetCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){
        assetId = $routeParams.assetId;
        $scope.marked = marked;



        $scope.activateVideo = function(vid){
        if (vid)
        {
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

        }
        
        $scope.setTags = function(){
            $('#assetTags').tagsinput({
              typeaheadjs: {
                name: 'tags',
                displayKey: 'name',
                valueKey: 'name',
                source: tags.ttAdapter()
              }
            });
            $('#assetTags').on('itemAdded', function(event) {

                    
              // event.item: contains the item
            });
        }

        $scope.isImage = function(asset){
            ct = asset.content_type;
            ctM = ct.split('/')[0];
            ctT = ct.split('/')[1];
            if (ctM=='image'){
                if (['png', 'jpeg', 'gif', 'webp', 'svg'].indexOf(ctT)>=0)
                    return true;
            }
        }

        $scope.isVideo = function(asset){
            ct = asset.content_type;
            ctM = ct.split('/')[0];
            ctT = ct.split('/')[1];
            if (ctM=='video'){
                if (['mp4', 'ogg', 'webm', 'x-flv'].indexOf(ctT)>=0)
                    return true;
            }
        }


        $scope.range = function(from, to){
            result = [];
            for(var x = Math.ceil(1); x <= to; x++)
                result.push(x);
            return result;

        }

        $scope.deleteAsset = function(){
            if (confirm('Are you sure you want to rmove this asset?'))
                req= $http.delete('/api/db/asset/'+$scope.asset.id).success(function(resp){
                            cid = $scope.asset.collection_id;
                            url = '/ams/c/' + cid;
                            $location.path(url);
                        });

        }

        $scope.updateAssetDescription = function(){
            $http.post('/api/db/asset/'+$scope.asset.id, {'description':$scope.asset.description});
        }

        $scope.highlightCode = function(){
              $('pre code').each(function(i, block) {
                hljs.highlightBlock(block);
              });
        }

        $scope.loadAssetData = function(){
            $http.get('/static/' + $scope.asset.url).success(function(resp){

                        $scope.asset.data = resp;
                        $timeout($scope.highlightCode, 10);

                    });
        }

        $scope.editAssetContents = function(){
            if ($scope.editMode)
                $scope.editMode = false;
            else
                $scope.editMode = true;
        }
        $scope.updateAssetContents = function(){
                _data = $scope.asset.data;
                send = $http.put('/api/asset/save/'+$scope.asset.repository_id
                        +'?collection_id='+$scope.asset.collection_id+'&name='+$scope.asset.fullname
                        , $scope.asset.data, {transformRequest: []});
                send.success(function(resp){
                    $scope.editMode = false;
                    $scope.getAssetInfo(true); //only asset versions;
                        });
                send.error(function(resp){
                    $scope.getAssetInfo();
                        });

            }



        $scope.checkout = function(v, download){
                    $scope.checkout_load = v;
            req = $http.post('/api/asset/checkout/'+$scope.asset.id+'?version='+v).success(function(resp){
                    //$scope.getAssetInfo();
                    if (resp.poster)
                        $scope.asset.poster = resp.poster;
                    if (resp.preview)
                        $scope.asset.preview = resp.preview;
                    $scope.checkout_load = null;
                    $scope.checkouted = v;
                    if (download)
                        window.location = '/static/ASSETS/'+ $scope.asset.uuid + '/' + $scope.asset.fullname;
                    //document.location='/static/ASSETS/'+$scope.asset.uuid+'/'+$scope.asset.fullname;
                    
                    }) 
        }
        $scope.getAssetInfo = function(versionsOnly){
            req = $http.get('/api/db/asset/'+assetId).success(function(Resp, code){
                    if (!Resp.id)
                        {
                        $location.path('404');
                        return null;
                        }
                    //$location.search('version', Resp.version)
                    if (!versionsOnly)
                        $scope.asset = Resp;

                    getTags = $http.get('/api/db/asset/'+assetId+'?field=tgs');
                    getTags.success(function(tgs){
                        $scope.asset.tgs = tgs;
                        })

                    $scope.checkout('v_'+Resp.version);
                    $scope.assetVersions = Resp.git_tags.split(',');
                    $rootScope.title = 'Asset: ' + Resp.name + ' - ' + 'Fearless';
                    $scope.$parent.comment_id = Resp.uuid;
                    $scope.$parent.getComments();
                    if (Resp.owner_id){

                        ureq = $http.get('/api/db/user/'+Resp.owner_id).success(function(resp){
                                $scope.asset.owner = resp;
                                if (Resp.content_type.split('/')[0]=='video')
                                    videojs('video_'+$scope.asset.id);
                            })

                        creq = $http.get('/api/db/collection/'+Resp.collection_id).success(function(resp){
                            $scope.asset.collection = resp;
                            });
                        rreq = $http.get('/api/db/repository/'+Resp.repository_id).success(function(resp){
                            $scope.asset.repository = resp;
                            });


                    }
                })


        }
        $scope.$watch(assetId, function(){
                $scope.getAssetInfo();
            })
        

        });


fearlessApp.controller('collectionCtrl', function($scope, $rootScope, $routeParams, 
            $http, $location, Restangular, $timeout, $filter, $window){


        $scope.activateVideo = function(vid){
        if (vid)
        {
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

        }

        $scope.isImage = function(asset){
            if (!asset)
                return null;
            ct = asset.content_type;
            ctM = ct.split('/')[0];
            ctT = ct.split('/')[1];
            if (ctM=='image'){
                if (['png', 'jpeg', 'gif', 'webp', 'svg'].indexOf(ctT)>=0)
                    return true;
            }
        }

        $scope.makeGallery = function(asset){
            blueimp.Gallery([
                {
                    title: asset.name,
                    href: '/static/' + asset.url,
                    type: asset.content_type,
                }
            ]);

        }

        $scope.isVideo = function(asset){
            if (!asset)
                return null;
            ct = asset.content_type;
            ctM = ct.split('/')[0];
            ctT = ct.split('/')[1];
            if (ctM=='video'){
                //if (['mp4', 'ogg', 'webm', 'x-flv'].indexOf(ctT)>=0)
                    return true;
            }
        }


        $scope.$parent.page = 'ams';
        $scope.collection = {};
        $scope.collection.assets = [];
        $scope.newSubCollection = {};
        ci = $routeParams.collectionId;

        $scope.getCollectionDetails = function(page, fromDropzone){
            if (page==undefined)
            {
                if ($routeParams.page>0)
                    page = $routeParams.page-1;
                else
                    page = 0;
            }
            start = 0;
            end = 10;
            if (page){
                c = 10;
                start = c*page;
                end = start + c;
            }
            req = $http.get('/api/collection/'+ci+'?s='+start+'&e='+end);
            req.success(function(resp){
                    $scope.collection = resp;
                    if (!resp)
                        $location.path('404')
                    else {
                    for (i in $scope.collection.assets){
                        _asset = $scope.collection.assets[i];


                    }
                    getTags = $http.get('/api/db/collection/'+ci+'?field=tgs');
                    getTags.success(function(tgs){
                        $scope.collection.tgs = tgs;
                        })
                    $rootScope.title = 'Collection: ' + resp.name + ' - ' + 'Fearless'
                    $scope.collection.page = (page||0)+1;
                    $location.search('page', (page||0)+1);
                    $scope.attachurl = "/api/asset/save/"+resp.repository.name+"?collection_id="+resp.id+'&multipart=true';
                    $scope.uploadOptions = {
                        url:$scope.attachurl,
                        type:'PUT',
                        singleFileUploads:true,
                        sequentialUploads:true,
                        done: function(e, data) {
                            console.log(data.files, e);
                            $scope.getCollectionDetails();
        //hide completed upload element in queue
                        //$(data.context['0']).fadeOut(700);
                        //limitMultiFileUploads:1,
                        
                    }
                    }
                    //$('#fileupload').bind('fileuploaddone', function (e, data) {
                   //         $scope.getCollectionDetails();
                   //         })





                    if ($scope.$parent){
                        $scope.$parent.comment_id = resp.uuid;
                        $scope.$parent.getComments();
                        }

                    //$scope.activateVideo();

                }
            })
            req.error(function(er){
                        $location.path('404')
                    })
        }


        $scope.deleteCollection = function(){
            if (confirm('Are you sure you want to rmove this collection?'))
                req= $http.delete('/api/db/collection/'+ci).success(function(resp){
                            pid = $scope.collection.project.id;
                            url = '/pms/' + pid;
                            $location.path(url);
                        });

        }



        $scope.$watch(ci, function(){
                $scope.getCollectionDetails();
                })

    

        $scope.toggleThumbnail = function(){
            if ($scope.thumbnails)
                $scope.thumbnails=false;
            else
                $scope.thumbnails=true;
        }
        $scope.initToggle = function(){
            $('#toggle-thmb').bootstrapToggle();
            $scope.thumbnails=false;
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

fearlessApp.controller('errorsCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){
        
        })
fearlessApp.controller('tasksCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){
        
        })

fearlessApp.controller('taskDetailCtrl', function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){
        taskId = $routeParams.taskId;
        $scope.getTaskDetails = function(){
            req = $http.get('/api/task/'+taskId).success(function(resp){
                    $scope.task = resp;
                
                })
        }
        })


    
fearlessApp.controller('inboxCtrl', function ($scope, $filter, $location, $interval, $rootScope, messageService, $http, $routeParams) {
    $scope.messages = {};
    if($scope.$parent)
        $scope.messages.resources = $scope.$parent.resources;
    messageService.messages = [];
    $scope.getUnreadCount  = messageService.getUnreadCount;
    $scope.messages.folder = $routeParams.folder || 'inbox';

    
    $scope.init = function(process){
        req = $http.get('/api/messages/list');
        req.success(function(resp){
        messageService.messages = resp;
        $scope.messages.items = resp;
        if (process){
            $scope.messages.items = [];
            $rootScope.title = 'Messages';
            all = $http.get('/api/messages/all?folder='+($routeParams.folder || 'inbox'));
            all.success(function(results){
            for (i in results){
                m = results[i];
                newm = m;
                newm.prettyDate = $scope.$parent.prettyDate(m.datetime);
                $scope.messages.items.push(newm);
                $scope.search($scope.messages.folder);
            }
            });
        }
            $scope.newMessage = {};            
       })
    }
   	
 	$scope.date = new Date;
    $scope.sortingOrder = 'id';
    $scope.pageSizes = [10,20,50,100];
    $scope.reverse = false;
    $scope.filteredItems = [];
    $scope.groupedItems = [];
    $scope.itemsPerPage = 10;
    $scope.pagedItems = [];
    $scope.currentPage = 0;
    
    /* inbox functions -------------------------------------- */
    



    $scope.sendMessage = function(draft){
        $('#modalCompose').modal('hide');
        if (draft)
            $scope.newMessage.draft = true;
        if ($scope.forwardMode){
            $scope.newMessage.subject = 'FWD: ' + $scope.selected.subject_s;
            $scope.newMessage.body = 'Forwarded message:'
        }

        if ($scope.replyMode || $scope.forwardMode)
            $scope.newMessage.body += ('\n _____ \n\n <sup> Authored on '
                    + new Date($scope.selected.datetime * 1000).toString()
                    + ' by '+$scope.selected.from_s.firstname_s 
                    + ' ' + $scope.selected.from_s.lastname_s +'</sub> \n >'
                    + $scope.selected.body_s);
        req = $http.post('/api/messages/set', $scope.newMessage);
        req.success(function(resp){
                if ($scope.newMessage.to)
                    $location.search('folder', 'sent');
                else
                    $location.search('folder', 'draft');
                $scope.newMessage = {};
                replyMode=false;
                forwardMode=false;
                })
    }

    var searchMatch = function (haystack, needle) {
        if (!needle) {
          return true;
        }
        return haystack.toLowerCase().indexOf(needle.toLowerCase()) !== -1;
    };
    
    $scope.$watch($routeParams.folder, function(){
            })
    // filter the items
    $scope.search = function (folder) {
        //$scope.messages.items.sort(function(a, b){return a.datetime<b.datetime});
        $scope.filteredItems = $filter('filter')($scope.messages.items, function (item) {
          for(var attr in item) {
            if (searchMatch(item[attr], $scope.query))
              return true;
          }
          return false;
        });
        $scope.currentPage = 0;
        // now group by pages
        $scope.groupToPages();
    };
    
    // calculate page in place
    $scope.groupToPages = function () {
        $scope.selected = null;
        $scope.pagedItems = [];
        
        for (var i = 0; i < $scope.filteredItems.length; i++) {
          if (i % $scope.itemsPerPage === 0) {
            $scope.pagedItems[Math.floor(i / $scope.itemsPerPage)] = [ $scope.filteredItems[i] ];
          } else {
            $scope.pagedItems[Math.floor(i / $scope.itemsPerPage)].push($scope.filteredItems[i]);
          }
        }
    };
    
    $scope.range = function (start, end) {
        var ret = [];
        if (!end) {
          end = start;
          start = 0;
        }
        for (var i = start; i < end; i++) {
          ret.push(i);
        }
        return ret;
    };
    
    $scope.prevPage = function () {
        if ($scope.currentPage > 0) {
            $scope.currentPage--;
        }
        return false;
    };
    
    $scope.nextPage = function () {
        if ($scope.currentPage < $scope.pagedItems.length - 1) {
            $scope.currentPage++;
        }
        return false;
    };
    
    $scope.setPage = function () {
        $scope.currentPage = this.n;
    };
    
    $scope.moveItem = function (item, target) {
            if (!target){
                if ($scope.messages.folder != 'trash')
                    target = 'trash';
                else
                    target = 'inbox';
            }
                var idxInItems = $scope.messages.items.indexOf(item);
                data = {to_folder:target, from_folder:$scope.messages.folder};
                req = $http.post('/api/messages/move/'+item.key, data);
                $scope.messages.items.splice(idxInItems,1);
                req.success(function(resp){
                   // if (target!='trash' && target!='archive')
                   //     $location.search('folder', target);
                        //deleted
                })
        $scope.search();
        return false;
    };


    
    $scope.isMessageSelected = function () {
        if (typeof $scope.selected!=="undefined" && $scope.selected!==null) {

            return true;

        }
        else {
            return false;
        }
    };

    function replaceAll(find, replace, str) {
      return str.replace(new RegExp(find, 'g'), replace);
    }

    var re = /(^|\s)((https?:\/\/)?[\w-]+(\.[\w-]+)+\.?(:\d+)?(\/\S*)?)/gi;
    function uniq_fast(a) {
        if (!a)
            return []

        var seen = {};
        var out = [];
        var len = a.length;
        var j = 0;
        for(var i = 0; i < len; i++) {
             var item = a[i];
             if(seen[item] !== 1) {
                   seen[item] = 1;
                   out[j++] = item;
             }
        }
        return out;
    }

    $scope.readMessage = function (item) {
        item.read = true;
        $scope.selected = item;
        $scope.updateMessage(item);
    };

    $scope.updateMessage = function(message){
        data = {message:message, folder:$scope.messages.folder}
        $http.post('/api/messages/update/'+message.key, data);
    }

    
    $scope.readAll = function () {
        for (var i in $scope.messages.items) {
            $scope.messages.items[i].read = true;
            $scope.updateMessage($scope.messages.items[i]);
        }
    };
    
    $scope.closeMessage = function () {
        $scope.selected = null;
    };
    
    $scope.renderMessageBody = function(body)
    {
        if (body)
            return marked(body);
        };
    
    /* end inbox functions ---------------------------------- */
    


    // initialize
    //$scope.init();


    
})// end inboxCtrl
fearlessApp.controller('messagesCtrl',  function ($scope) {
    
    $scope.message = function(idx) {
        return messages(idx);
    };
    
});// end messageCtrl


fearlessApp.controller('taggerCtrl',  function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){
        
    $scope.tags = {};
    $scope.tags.data = [];
    var tags = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 5,
      prefetch: {
        // url points to a json file that contains an array of country names, see
        // https://github.com/twitter/typeahead.js/blob/gh-pages/data/countries.json
        url: '/api/db/tag',
        // the json file contains an array of strings, but the Bloodhound
        // suggestion engine expects JavaScript objects so this converts all of
        // those strings

                
      }
    });
    tags.initialize();

    $scope.completeData = {
      name: 'tags',
      displayKey: 'name',
      source: tags.ttAdapter(),
    };
    
    $scope.addTag = function(type, target){
        target.tgs.forEach(function(e){
                    $scope.tags.data.push(e.name)
                }
            )
        if ($scope.tags.userTagFilter && $scope.tags.userTagFilter.name)
        {
            $scope.tags.data.push($scope.tags.userTagFilter.name);
            target.tgs.push({'name':$scope.tags.userTagFilter.name})
        }
        else if ($scope.tags.userTagFilter)
        {
            $scope.tags.data.push($scope.tags.userTagFilter);
            target.tgs.push({'name':$scope.tags.userTagFilter})
        }
        $scope.tags.userTagFilter = null;
        console.log($scope.tags.data)
        $http.post('/api/setTags/'+type+'/'+target.uuid, {'tags':$scope.tags.data});
        $scope.tags.data = [];
    }

        });

fearlessApp.controller('assetsIndexCtrl',  function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){

        $rootScope.title = 'User Assets - Fearless';

        $scope.assetOptions = {};
                // main assets index page
        var assets = new Bloodhound({
          datumTokenizer: Bloodhound.tokenizers.obj.whitespace('fullname'),
          queryTokenizer: Bloodhound.tokenizers.whitespace,
          limit: 5,
          prefetch: {
            // url points to a json file that contains an array of country names, see
            // https://github.com/twitter/typeahead.js/blob/gh-pages/data/countries.json
            url: '/api/db/asset?field=fullname&filters=owner_id='+$scope.$parent.userInfo.userid,
            // the json file contains an array of strings, but the Bloodhound
            // suggestion engine expects JavaScript objects so this converts all of
            // those strings
            filter: function(list) {
              return $.map(list, function(asset) { return { fullname: asset }; });
            }
                    
          }
        });
        // kicks off the loading/processing of `local` and `prefetch`
        assets.initialize();

        $scope.assetOptions =  {
            highlight: true
          };
        // passing in `null` for the `options` arguments will result in the default
        // options being used
        $scope.completeData = {
          name: 'assets',
          displayKey: 'fullname',
          // `ttAdapter` wraps the suggestion engine in an adapter that
          // is compatible with the typeahead jQuery plugin
          source: assets.ttAdapter(),
        //templates: {
        //    empty: [
        //      '<div style="padding:10px">',
        //      'unable to find any assets.',
        //      '</div>'
        //    ].join('\n'),
        //    suggestion: Handlebars.compile('<p><strong>{{fullname}}</strong> – {{content_type}}</p>')
        //  }
        };

        $scope.search = function(){
            old = false;
            q = $scope.assetOptions.userAssetsFilter.fullname;
            if (q && old!=q)
            {
                $scope.page = 1;
                $location.search('page', 1);
                $scope.getUserAssets(false, false, q);
                $location.search('q', q);
                old = q;
            }
            else if (!q && !$scope.assetOptions.userAssetsFilter)
            {
                $scope.getUserAssets();
                $location.search('q', null);
            }
        }





        $scope.gotoPage = function(page){
            if (page<1)
                return null;

            $scope.page = page;
            $location.search('page', page);
            $scope.getUserAssets();
            //here
        }


        $scope.tagSelection = function(tag){
            if (tag.selected)
                tag.selected=false;
            else
                tag.selected=true;
            
            tags = [];
            for (i in $scope.assetTags){
                _t = $scope.assetTags[i];
                if (_t.selected)
                    tags.push(_t.name)
                $location.search('tags', tags.join(','));
            }
        }

        $scope.getUserAssets = function(order_by, sort, search_for){
            if (!$scope.page)
                $scope.page = 1;
            if (!order_by)
                order_by = $scope.orderMode || 'created_on';
            if (!sort || sort==0)
                sort = 'desc';
            else
                sort = 'asc';
            s = ($scope.page-1)*50;
            e = s+50;
            query = '/api/db/asset?sort='+sort+'&s='+s+'&e='+e+'&order_by='+ order_by + '&filters=owner_id='+
                    $scope.$parent.userInfo.userid;
            if ($routeParams.tags)
                query += '&tags='+$routeParams.tags;

            tag_query = '/api/asset/get_user_tags';
            tagReq = $http.get(tag_query); 
            tagReq.success(function(resp){
                $scope.assetTags = resp;
                if ($routeParams.tags)
                    {
                        _tags = $routeParams.tags.split(',');
                        for (j in _tags){
                            tag = _tags[j];
                            for (i in resp){
                                each = $scope.assetTags[i];
                                if (each.name == tag)
                                    each.selected=true;


                            }
                        }
                    }
                })



            if (search_for)
                query += ',fullname=' + search_for;

            req = $http.get(query);
            req.success(function(resp){
                    $scope.userAssets = resp;
                    
                    })
            query = '/api/db/asset?filters=owner_id='+$scope.$parent.userInfo.userid+'&count=true';
            if (search_for)
                query += '&filters=fullname=' + search_for;
            if ($routeParams.tags)
                query += '&tags='+$routeParams.tags;
            creq = $http.get(query);
            creq.success(function(cresp){
                    $scope.assetsCount = cresp.count;
                    
                    })
        }


         $scope.$watch($routeParams.page, function(){
                    $scope.page = parseInt($routeParams.page);
                    $scope.assetOptions.userAssetsFilter = {};
                    $scope.assetOptions.userAssetsFilter.fullname = $routeParams.q;
                    if ($routeParams.q)
                        {
                        $scope.search();
                        }
                    else
                        {
                        $scope.getUserAssets();
                        }
                });

    
});// end messageCtrl



fearlessApp.controller('userReportsCtrl',  function($scope, $rootScope, $routeParams, $http, $location, Restangular, $timeout){


        getReports = $http.get('/api/userReports').success(function(resp){
                $scope.reports = resp;

            });

        });


fearlessApp.controller('FileDestroyController',  function($scope, $http){
    var file = $scope.file,
        state;
    if (file.url) {
        file.$state = function () {
            return state;
        };
        file.$destroy = function () {
            state = 'pending';
            return $http({
                url: file.deleteUrl,
                method: file.deleteType
            }).then(
                function () {
                    state = 'resolved';
                    $scope.clear(file);
                },
                function () {
                    state = 'rejected';
                }
            );
        };
    } else if (!file.$cancel && !file._index) {
        file.$cancel = function () {
            $scope.clear(file);
        };
    }

        });



//////////////////////////////////////////////////////


/////////////////////////////////////////////////

