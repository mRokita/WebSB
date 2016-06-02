var app = angular.module("sb", []);
app.controller("serverList", function($scope, $http, $window){
    $http.get("/api/v1/scans/latest/?show_variables=1").success(function(response){
        $scope.scan = response;
        $scope.rowStyle = $window.rowStyle;
        console.log($scope.scan);
    })
});