var sdcGithub = angular.module('sdcGithub', ['ngRoute']);

sdcGithub.controller('IndexCtrl', function ($scope) {});
sdcGithub.controller('ServiceWorkerCtrl', function ($scope) {});

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
