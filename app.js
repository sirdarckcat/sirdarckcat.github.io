var sdcGithub = angular.module('sdcGithub', ['ngRoute']);

sdcGithub.controller('IndexCtrl', function ($scope, $route) {
  debugger;
});

sdcGithub.controller('ServiceWorkerCtrl', function ($scope, $route) {
  debugger;
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
