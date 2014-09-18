var fateamApp = angular.module('fateamApp', ['ngRoute']);

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


		$locationProvider.html5Mode(true);

	})

	// create the controller and inject Angular's $scope
	fateamApp.controller('mainController', function($scope) {
		// create a message to display in our view
		$scope.message = 'fa-team, A Revolutionary Animation Production Management System!';
	});

	fateamApp.controller('aboutController', function($scope) {
		$scope.message = 'Look! I am an about page.';
	});











fateamApp.controller('homeCtrl', function ($scope, $http, $route) {
  $http({
    method: 'POST', 
    url:'/api'
}).then(function(response) {
    $scope.api_info = response.data;
}.bind(this));;

});
