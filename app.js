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
  $scope.registerServiceWorker = function() {
    navigator.serviceWorker.register(
      $scope.serviceWorkerUrl,
      JSON.parse($scope.serviceWorkerInit));
  };
  // XMLHttpRequest
  $scope.xhrHeader = {};
  $scope.logXhrProgress = function(prefix, target) {
    function log(type, message) {
      $scope.apply(function(scope) {
        var logEntry = {type: type, message: message};
        scope.xhrLog.push(logEntry);
        console.log(logEntry);
      });
    }
    var events = ['loadstart', 'progress', 'abort', 'error', 'load', 'timeout', 'loadend', 'readystatechange'];
    for (var i=0; i<events.length; i++) {
      target.addEventListener(events[i], log.bind(null, prefix + events[i]));
    }
  };
  $scope.fetchXhr = function() {
    var xhr = new XMLHttpRequest;
    xhr.open($scope.xhrMethod, $scope.xhrUrl, $scope.xhrAsync, $scope.xhrUsername, $scope.xhrPassword);
    for (header in $scope.xhrHeader) {
      xhr.setRequestHeader(header, $scope.xhrHeader[header]);
    }
    xhr.withCredentials = $scope.xhrWithCredentials;
    $scope.logXhrProgress('XHR.upload.', xhr.upload);
    $scope.logXhrProgress('XHR.', xhr);
    xhr.send($scope.xhrData);
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
    when('/service-worker', {
      templateUrl: 'partials/service-worker.html',
      controller: 'ServiceWorkerCtrl'
    }).
    otherwise({
      redirectTo: '/'
    });
}]);
