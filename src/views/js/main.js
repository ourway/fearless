var fearlessApp = angular.module('fearlessApp', ['ngRoute', 'ngResource', 'ngCookies']);

fearlessApp.factory('authFactory', function($resource) {
  return $resource('/api/auth/:what',
    { what:'@action' },
    { save: { method: 'POST' }}
  );
});



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
                controller: 'pmsCtrl'
            })
		 })


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
                        $cookies.userid = resp.id;
                        $cookies.username = resp.firstname;
                        $scope.userInfo.username = resp.firstname;
                        $scope.userInfo.userid = resp.id;
                        $('#loginSubmitButton').text('Done!')
                        $scope.loginInfo.email = null;
                        $scope.loginInfo.password = null;
                        $scope.userInfo.logged_in = true;
                        try {
                            next_page = atob($routeParams.next);
                            if (next_page.split('/')[1] === 'api')
                                window.location = next_page;
                            else
                                $location.path(next_page);
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
            $cookies.userid = '';
            $cookies.username = '';
            $scope.userInfo.logged_in = false;
            $scope.userInfo.username = null;
            $scope.userInfo.userid = null;
            $http.post('/api/auth/logout');
            //$scope.userInfo.logged_in = true;

        }
    //Check if user is logged in
    $scope.is_logged_in = function(){
        var userid = $cookies.userid;
        var username = $cookies.username;
       if (userid && username)
            {
                $scope.userInfo.username = username;
                $scope.userInfo.userid = userid;
                $scope.userInfo.logged_in = true;
                return true
            }
        else {
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

            console.log(result);
        })




    }

});