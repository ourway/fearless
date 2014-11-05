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
                    $http.get('/api/db/asset/'+name+'.zip?key=name&field=url').success(function(assetInfo){

                         asset_url = '/static/'+ assetInfo.split('"')[1]
                        JSZipUtils.getBinaryContent(asset_url, function(err, data) {
                              if(err) {
                                throw err; // or handle err
                              }
                              loadWithFile(data)
                            });

                         //$scope.changed = new Date(assetInfo.modified_on * 1000)


                    })
                    // here I should try to load data from asset server
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
