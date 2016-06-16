var app = angular.module("sb", []).filter('mapshotname', function() {
        return function(input) {
            // do some bounds checking here to ensure it has that index
            var a = input.split("/");
            return a.length>1 ? a[1] : a[0];
        }
    });
app.controller("serverList", function($scope, $http){
    $http.get("/api/v1/scans/latest/?show_variables=1&show_players=1").success(function(response){
        var rowWidth;
        $scope.rowStyle = {"margin": "0px", 'padding': '0px'};
        function getWidths(){
            var rowWidth = $(".collapsible").width();
            $scope.rowStyle['max-width'] = rowWidth/3-1+"px";
            $scope.rowStyle['min-width'] = rowWidth/3-1+"px";
        }
        $(window).resize(getWidths);
        $(document).ready(getWidths);
        $scope.scan = response;
        console.log($scope.scan);
    })
});