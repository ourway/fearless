var fearlessShowtimeApp = angular.module('fearlessShowtimeApp', ['ngResource', 'ngCookies', 'ngRoute']);

function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 8; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}



    fearlessShowtimeApp.controller('showtimeCtrl', function($scope, $rootScope, $cookies,$http,
                                                      $timeout, $location, $routeParams) {


        $http.post('/api/auth/getUserInfo').success(function(result){

            if (result.message == 'ERROR'){
                window.location = '/app/#/auth/login/' + btoa('showtime');
                return
            }
            else {
                $scope.user = result.alias
                loc = $location.$$path
                name = loc.slice(1)
                if (name.length==8){
                    $scope.name = name;
                }
                else {
                    $scope.name = makeid();
                }
                project.projectName = $scope.name;
                $location.path($scope.name);

        }
        })


///////////////////////////////////////end///////////////////
    });
