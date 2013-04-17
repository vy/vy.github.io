---
kind: article
created_at: 2012-09-16 15:31 EET
title: An Authentication Service for AngularJS
tags:
  - angularjs
  - coffeescript
  - javascript
---

I am so tired to form up explanatory, coherent sentences, but at the same time I really like to share a user authentication service that I wrote for [AngularJS](http://www.angularjs.org/). Hence, pardon my brevity.

In this example I use RailwayJS with CoffeeScript both at the client- and server-side. (See my previous <%= link_to "post", @items["/blog/post/20120916-auto-compiling-assets-with-connect-assets/"] %> on auto-compiling assets with connect-assets.) Here is the scenario: You have `assignments.html` such that only authenticated users are allowed.

First things first, here is our `/config/routes.coffee`:

    #!coffeescript
    exports.routes = (map)->
      map.post  '/login',                   'home#login'
      map.post  '/logout',                  'home#logout'
      map.get   '/',                        'home#index'

Then we implement our controller `/app/controllers/home_controller.coffee` as follows.

    #!coffeescript
    moment = require('moment')
    
    action 'index', ->
        render(user: request.session.user)
    
    action 'login', ->
        authenticate request.body.username, request.body.password, (ret) ->
            if (ret)
                request.session.user =
                    name: request.body.username,
                    time: moment().unix()
            send(result: ret)
    
    action 'logout', ->
        request.session.destroy()
        redirect('/')

Note that the `authenticate` used in `login` action handler is meant to be provided by you.

Later, we write `/app/views/home/index.ejs` to fire up AngularJS:

    #!html
    <div ng-app="project">
        <%%- javascript_include_tag('angular', 'angular-resource') %>
        <%%- js('app') %>
        <%%- js('controllers') %>
        <%%- js('services') %>
        <div ng-view></div>
    </div>

We first start by implementing `app.js` of AngularJS in `/assets/js/app.coffee`:

    #!coffeescript
    angular.module('project', ['projectServices'])
        .config ($routeProvider) ->
            $routeProvider
                .when('/login',
                    templateUrl: 'partials/login.html',
                    controller: LoginCtrl)
                .when('/assignments',
                    templateUrl: 'partials/assignments.html',
                    controller: AssignmentListCtrl)
                .otherwise(redirectTo: '/login')
        .run ($rootScope, $location, User) ->
            $rootScope.$watch \
                () -> $location.path(),
                (next, prev) ->
                    if not User.isAuthenticated() and next isnt '/login'
                        $location.path("/login"),
                true

The extra bit for watching on `$rootScope` is to check access to authentication required pages.

After `app.js`, we implement `/assets/js/controllers.coffee`:

    #!coffeescript
    window.LoginCtrl = ($scope, $location, User) ->
        $scope.login = ->
            User.login $scope.username, $scope.password, (result) ->
                if !result
                    window.alert('Authentication failed!')
                else
                    $scope.$apply -> $location.path('/assignments')
    
    window.AssignmentListCtrl = ($scope, User) ->
        $scope.User = User

For each controller, we implement a view, that is, `/public/partials/login.html`

    #!html
    <div>
        <form>
            <label>Username: <input type="text" ng-model="username"></label>
            <label>Password: <input type="password" ng-model="password"></label>
            <button ng-click="login()">Login</button>
        </form>
    </div>

and `/public/partials/assignments.html`:

    #!html
    <p>Welcome, {{User.getName()}}!</p>
    <button ng-click="User.logout()">Logout</button>

And here goes the magic, `/assets/js/services.coffee`:

    #!coffeescript
    angular.module('projectServices', [])
        .factory 'User', ->
            @authenticated = false
            @name = null
            isAuthenticated: => @authenticated
            getName: => @name
            login: (username, password, callback) =>
                $.post '/login',
                    {username: username, password: password},
                    ((data) =>
                        if data.result
                            @name = username
                            @authenticated = true
                        callback(data.result)),
                    'json'
            logout: (callback) =>
                if @authenticated
                    $.post '/logout', {},
                        ((data) =>
                            if data.result
                                @authenticated = false;
                            callback(data.result)),
                        'json'
                else callback(false)

Hope it works for you as well.

**Edit:** Thanks [Krisztián Kerék](https://plus.google.com/100882799970411374993) for spotting the routing problem related with listening on `$rootScope` for `$routeChangeStart`. Replaced it with `$rootScope.$watch` as suggested in [this](http://stackoverflow.com/a/15029387/1278899) StackOverflow post.
