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
  $scope.xhrLog = [];
  function logXhrProgress(prefix, target) {
    function log(type, message) {
      message = JSON.parse($filter('json')(message));
      setTimeout(function() {
        $scope.$apply(function(scope) {
          var logEntry = {type: type, message: message};
          scope.xhrLog.push(logEntry);
          console.log(logEntry);
        });
      }, 1);
    }
    var events = ['loadstart', 'progress', 'abort', 'error', 'load', 'timeout', 'loadend', 'readystatechange'];
    for (var i=0; i<events.length; i++) {
      target.addEventListener(events[i], log.bind(null, prefix + events[i]));
    }
  };
  $scope.fetchXhr = function(xhrMethod, xhrUrl, xhrAsync, xhrUsername, xhrPassword, xhrHeader, xhrTimeout, xhrWithCredentials, xhrData) {
    var xhr = new XMLHttpRequest;
    xhr.open(xhrMethod, xhrUrl, xhrAsync===true, xhrUsername?xhrUsername:undefined, xhrPassword?xhrPassword:undefined);
    for (header in xhrHeader) {
      xhr.setRequestHeader(header, xhrHeader[header]);
    }
    if (xhrAsync)
      xhr.timeout = xhrTimeout * 1;
    xhr.withCredentials = xhrWithCredentials === true;
    logXhrProgress('XHR.upload.', xhr.upload);
    logXhrProgress('XHR.', xhr);
    xhr.send(xhrData);
  };
});

sdcGithub.config(['$routeProvider', function($routeProvider, $sceDelegateProvider) {
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
  // allow all URLs as resource URLs
  $sceDelegateProvider.resourceUrlWhitelist(['**']);
}]);
