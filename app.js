var sdcGithub = angular.module('sdcGithub', ['ngRoute']);

sdcGithub.controller('IndexCtrl', function ($scope) {
  debugger;
});

sdcGithub.controller('ServiceWorkerCtrl', function ($scope, $location, $filter) {
  $scope.fetchUrl = $location.search().fetchUrl;
  $scope.fetchInfo = $filter('json')(JSON.parse($location.search().fetchInfo));
  $scope.styleFetchInfo = function() {
    var fetchInfo = $filter('json')(JSON.parse($scope.fetchInfo));
    if ($scope.fetchInfo != fetchInfo) {
      $scope.fetchInfo = fetchInfo;
    }
  };
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
