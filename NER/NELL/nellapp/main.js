/**
 * Created by zal on 9/21/16.
 */
(function () {

  'use strict';

  angular.module('NellAnnoApp', [])

  .controller('NellAnnoController', ['$scope', '$log',
    function($scope, $log) {
    $scope.getResults = function() {
      $log.log("test");
    };
  }

  ]);

}());