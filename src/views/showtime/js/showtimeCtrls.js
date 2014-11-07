var fearlessShowtimeApp = angular.module('fearlessShowtimeApp', ['ngResource', 'ngCookies', 'restangular', 'ngRoute']);





function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 8; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}



    fearlessShowtimeApp.controller('showtimeCtrl', function($scope, $rootScope, $cookies,$http,
                                                      $timeout, $location, $routeParams, Restangular) {


             $scope.asset = {};

             $scope.hey = function(){
                 console.log($scope.asset);
             }
             $scope.timeConverter = function(UNIX_timestamp){
             var a = new Date(UNIX_timestamp*1000);
             var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                 var year = a.getFullYear();
                 var month = months[a.getMonth() - 1];
                 var date = a.getDate();
                 var hour = a.getHours();
                 var min = a.getMinutes();
                 var sec = a.getSeconds();
                 var time = date + month + year + '-' + hour + ':' + min;
                 return time;
             }


        $http.post('/api/auth/getUserInfo').success(function(result){

            if (result.message == 'ERROR'){
                window.location = '/app/#/auth/login/' + btoa('showtime');
                return
            }
            else {
                $scope.user = result
                loc = $location.$$path
                name = loc.slice(1)
                //x = Restangular.one('api', 'asset').post(name+'.zip', {'name':true})
                //x.then(function(ass){
                //    console.log(ass);
                //})
                if (name.length==8){
                    $scope.loading = true;
                    $scope.name = name;
                    $http.post('/api/asset/'+$scope.name+'.zip?name=true').success(function(assetInfo){


                        if (assetInfo.url) {
                            JSZipUtils.getBinaryContent(assetInfo.url + '?rn=' + makeid(), function (err, data) {
                                if (err) {
                                    return false;
                                    //throw err; // or handle err
                                }
                                loadWithFile(data);


                                $scope.asset = assetInfo;
                                $scope.$apply()
                            });
                         }

                        $scope.loading = false;

                         //$scope.changed = new Date(assetInfo.modified_on * 1000)


                    })
                    // here I should try to load data from asset server
                }
                else {
                    $scope.name = makeid();
                }
                project.projectName = $scope.name;
                $location.path($scope.name);


            showtimeUserInfos = Restangular.one('api', 'showtime').getList($scope.user.id);
            showtimeUserInfos.then(function(result){

                $scope.userShows = result;
                $scope.goto = function(to){
                    $location.path(to);
                    location.reload();
                }
            })


        }
        })


///////////////////////////////////////end///////////////////
    });
