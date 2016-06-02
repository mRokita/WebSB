var app = angular.module("sb", []);
app.controller("serverList", function($scope, $http){
    $http.get("/api/v1/scans/latest/").success(function(response){
        $scope.scan = response;
        console.log($scope.scan);
    })
});