var fateamApp = angular.module('fateamApp', ['ngRoute', 'ngResource']);

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


		//$locationProvider.html5Mode(true);

	})

	// create the controller and inject Angular's $scope
	fateamApp.controller('mainController', function($scope, $rootScope) {
		// create a message to display in our view
        $rootScope.title = "Welcome to fa-team!";
		$scope.appName = 'APMS';
		$scope.message = $scope.appName + ', A Revolutionary Animation Production Management System!';
	});

	fateamApp.controller('aboutController', function($scope) {
		$scope.message = $scope.appName + '! I am an about page.';
	});




fateamApp.controller('titleCtrl', function ($scope, $http, $location) {
    console.log

});






fateamApp.controller('homeCtrl', function ($scope, $http, $route) {
  $http({
    method: 'POST', 
    url:'/api'
}).then(function(response) {
    $scope.api_info = response.data;
}.bind(this));;

});
