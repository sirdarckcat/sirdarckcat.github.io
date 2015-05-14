var sdcGithub = angular.module('sdcGithub', ['ngRoute']);

sdcGithub.controller('IndexCtrl', function ($scope) {
  debugger;
});

sdcGithub.controller('FetchCtrl', function ($scope, $location, $filter) {
  $scope.fetchUrl = $location.search().fetchUrl;
  $scope.fetchInfo = $location.search().fetchInfo;
  $scope.doFetch = function() {
    $scope.fetchInfo = $filter('json')(JSON.parse($scope.fetchInfo));
    $location.search({fetchUrl: $scope.fetchUrl, fetchInfo: $scope.fetchInfo});
    var responsePromise = fetch($scope.fetchUrl, JSON.parse($scope.fetchInfo));
  };
});

sdcGithub.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/', {
      templateUrl: 'partials/index.html',
      controller: 'IndexCtrl'
    }).
    when('/fetch', {
      templateUrl: 'partials/fetch.html',
      controller: 'FetchCtrl'
    }).
    otherwise({
      redirectTo: '/'
    });
}]);
