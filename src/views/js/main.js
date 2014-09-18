var fateamApp = angular.module('fateamApp', ['ngRoute']);

	fateamApp.config(function($routeProvider, $locationProvider) {
		$routeProvider

			// route for the home page
			.when('/home', {
				templateUrl : 'pages/home.html',
				controller  : 'mainController'
			})

			// route for the about page
			.when('/about', {
				templateUrl : 'pages/about.html',
				controller  : 'aboutController'
			})

			// route for the contact page
			.when('/contact', {
				templateUrl : 'pages/contact.html',
				controller  : 'contactController'
			});
		$locationProvider.html5Mode(true);

	})

	// create the controller and inject Angular's $scope
	fateamApp.controller('mainController', function($scope) {
		// create a message to display in our view
		$scope.message = 'Everyone come and see how good I look!';
	});

	fateamApp.controller('aboutController', function($scope) {
		$scope.message = 'Look! I am an about page.';
	});

	fateamApp.controller('contactController', function($scope) {
		$scope.message = 'Contact us! JK. This is just a demo.';
	});









fateamApp.controller('homeCtrl', function ($scope, $http, $route) {
  $http({
    method: 'POST', 
    url:'/api'
}).then(function(response) {
    $scope.api_info = response.data;
}.bind(this));;



  $scope.message = 'Everyone come and see how good I look!';

});
