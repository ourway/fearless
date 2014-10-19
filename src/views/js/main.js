var fateamApp = angular.module('fateamApp', ['ngRoute', 'ngResource', 'ngCookies']);

fateamApp.factory('authFactory', function($resource) {
  return $resource('/api/users/:what',
    { what:'@action' },
    { save: { method: 'POST' }}
  );
});

	fateamApp.config(function($routeProvider, $locationProvider) {
		$routeProvider

			// route for the home page
			.when('/', {
				templateUrl : 'pages/home.html',
				controller  : 'mainController'
			})

			// route for the about page
			.when('/about/', {
				templateUrl : 'pages/about.html',
				controller  : 'aboutController'
			})
			.when('/auth/login', {
				templateUrl : 'pages/auth/login.html',
				controller  : 'authController'
			})

		//$locationProvider.html5Mode(true);

	})

	// create the controller and inject Angular's $scope
	fateamApp.controller('mainController', function($scope, $rootScope, $cookies, authFactory) {
		// create a message to display in our view
        $rootScope.title = "Welcome to fa-team!";
		$scope.appName = 'APMS';
        $scope.showLogin = true;
		$scope.message = $scope.appName + ', A Revolutionary Animation Production Management System!';
        $scope.userInfo = {'logged_in':false};

    //Here is login format. I will send email and passwork and see if it is OK to continue
    //if the result.message===true then we are ok to continue authentication
    $scope.doLogin = function() {
        if (validateEmail($scope.loginInfo.email)==false)
            return null
        prom = authFactory.save({}, $scope.loginInfo, function(resp){
               if (resp.message==true && $scope.loginInfo.action=='login') //green light
                    {
                        $cookies.user_id = resp.id;
                        $cookies.user_name = resp.first_name;
                        $scope.userInfo.user_name = resp.first_name;
                        $scope.userInfo.user_id = resp.id;
                        $scope.loginInfo.email = null;
                        $scope.loginInfo.password = null;
                        $scope.userInfo.logged_in = true;
                    }
            
               if (resp.message==false && $scope.loginInfo.action=='login') //green light
                {
                        $scope.login_mode = 'Register';
                        $scope.loginInfo.action = 'register';
                }
                
               if (resp.message==true && $scope.loginInfo.action=='register') //green light
  // red light
                    {
                        $scope.login_mode = 'Sign in';
                        $scope.loginInfo.action = 'login';
                    }
        });
        console.log('ok')
        $scope.loginInfo.action = 'login';
        $scope.login_mode = 'Sign in';
    }


    // logout actions
    $scope.doLogout = function(){
            $cookies.user_id = '';
            $cookies.user_name = '';
            $scope.userInfo.logged_in = false;
            $scope.userInfo.user_name = null;
            $scope.userInfo.user_id = null;
            //$scope.userInfo.logged_in = true;

        }
    //Check if user is logged in
    $scope.is_logged_in = function(){
        var user_id = $cookies.user_id; 
        var user_name = $cookies.user_name;
       if (user_id && user_name)
            {
                $scope.userInfo.user_name = user_name;
                $scope.userInfo.user_id = user_id;
                $scope.userInfo.logged_in = true;
                return true
            } 
    }


	});

	fateamApp.controller('aboutController', function($scope) {
		$scope.message = $scope.appName + '! I am an about page.';
	});




fateamApp.controller('titleCtrl', function ($scope, $http, $location) {
    console.log

});


fateamApp.controller('authController', function ($scope, $http, $location) {
    $scope.$parent.showLogin = null;


});
//  NON Angular scripts
//  ========================


function validateEmail(email) { 
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
