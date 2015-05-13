var sdcGithub = angular.module('sdcGithub', ['ngRoute']);

sdcGithub.controller('IndexCtrl', function ($scope) {
  debugger;
});

sdcGithub.controller('ServiceWorkerCtrl', function ($scope, $location) {
  $scope.fetchUrl = $location.search().fetchUrl;
  $scope.$watch('fetchUrl', function() {
    $location.search({'fetchUrl': $scope.fetchUrl});
  });
  $scope.fetchInfo = $location.search().fetchInfo;
  $scope.$watch('fetchInfo', function() {
    $location.search({'fetchInfo': $scope.fetchInfo});
    var fetchInfo = $filter('json')($scope.fetchInfo);
    if ($scope.fetchInfo != fetchInfo) {
      $scope.fetchInfo = fetchInfo;
    }
  });
});

sdcGithub.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/', {
      templateUrl: 'partials/index.html',
      controller: 'IndexCtrl'
    }).
    when('/service-worker', {
      templateUrl: 'partials/service-worker.html',
      controller: 'ServiceWorkerCtrl'
    }).
    otherwise({
      redirectTo: '/'
    });
}]);
