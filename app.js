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
    fetch($scope.fetchUrl, JSON.parse($scope.fetchInfo)).then(function(response) {
      $scope.$apply(function(scope) {
        scope.fetchResponse = response;
      });
    }).catch(function(error) {
      $scope.$apply(function(scope) {
        scope.fetchError = error;
      });
    });
  };
});

sdcGithub.controller('ServiceWorkerCtrl', function ($scope, $location, $filter) {
  $scope.serviceWorkerController = navigator.serviceWorker.controller;
  $scope.serviceWorkerUrl = '/sw.js';
  $scope.serviceWorkerInit = $filter('json')({'scope': '/'});
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
    when('/service-worker', {
      templateUrl: 'partials/service-worker.html',
      controller: 'ServiceWorkerCtrl'
    }).
    otherwise({
      redirectTo: '/'
    });
}]);
