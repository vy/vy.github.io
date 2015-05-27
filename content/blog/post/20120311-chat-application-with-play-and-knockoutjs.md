---
kind: article
created_at: 2012-03-11 10:00 EET
title: Chat Application with Play Framework and KnockoutJS
tags:
  - facebook
  - java
  - javascript
  - knockoutjs
  - play framework
---

For a geography based social web application, I chose to work on a [Single Page Application](http://en.wikipedia.org/wiki/Single-page_application) template. For this purpose, I needed a Javascript framework to do the necessary plumbing for synchronizing server side and client side model objects. It took my nearly 3-4 weeks to finish the implementation. I was very happy with its final state and was excited to use it in the rest of the project. Next morning, I met with [BackboneJS](http://documentcloud.github.com/backbone/) with a suggestion from a friend of mine. Damn! My implementation was so close to BackboneJS that almost every function name was identical. Anyway, I couldn't know if I should cry or laugh. Following that path, it didn't take long for me to discover [KnockoutJS](http://knockoutjs.com/). I found it astonishingly beautiful and directly dived into the depths of the tutorial and spent that half day to read-and-evaluate  the exercises. Since the best way to learn something is to use it, in this blog post I will try to walk you through a chat application using [Play Framework](http://playframework.org/) and KnockoutJS.

In order to save some effort, I'll use the Facebook Login mechanics described in my <%= link_to "Facebook Login and Secure Module Integration in Play", @items["/blog/post/20120220-facebook-login-and-secure-module/"] %> post. Since I put together the necessary pieces into a GitHub project ([play-facebook](http://github.com/vy/play-facebook)), I will bootstrap directly from there.

    #!bash
    git clone git://github.com/vy/play-facebook.git play-chat
    cd play-chat
    play deps
    emacs conf/application.conf            # Edit application.name
    emacs app/controllers/Security.java    # Edit FBOAuth
    play run

So far, so good. Now, we need a `Room` model to store the posted messages.

    #!java
    public class Room {
        private static Room instance = null;
        public static final int EVENT_STREAM_SIZE = 100;
        private final ArchivedEventStream<Event> eventStream =
                new ArchivedEventStream<Event>(EVENT_STREAM_SIZE);
     
        public void publish(Event event) {
            eventStream.publish(event);
        }
     
        public Promise<List<IndexedEvent<Event>>> nextMessages(long lastReceived) {
            return eventStream.nextEvents(lastReceived);
        }
     
        public static abstract class Event {
            public final String date;
            public final String user;
            public final Type type;
     
            public final static DateFormat dateFormat =
                    new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
     
            public enum Type {
                JOIN,
                LEAVE,
                MESSAGE
            }
     
            public Event(User user, Type type) {
                this.date = dateFormat.format(new Date());
                this.user = user.name;
                this.type = type;
            }
        }
     
        public static class JoinEvent extends Event {
            public JoinEvent(User user) {
                super(user, Type.JOIN);
            }
        }
     
        public static class LeaveEvent extends Event {
            public LeaveEvent(User user) {
                super(user, Type.LEAVE);
            }
        }
     
        public static class MessageEvent extends Event {
            public final String text;
     
            public MessageEvent(User user, String text) {
                super(user, Type.MESSAGE);
                this.text = text;
            }
        }
     
        public static Room getInstance() {
            if (instance == null)
                instance = new Room();
            return instance;
        }
    }

Below is the list of major components provided by the `Room` model.

- `eventStream`, which is of type `ArchivedEventStream<Event>`, is the stream of messages that are published in the room. We bound the size of the stream window with `EVENT_STREAM_SIZE`.
- `nextMessages`, returns the list of messages that are published since the time pointed by passed index number, `lastReceived`. The main crux here is that, we return a `Promise`, which is actually a tiny magic provided by `ArchivedEventStream`. Hence, web server can process these requests asynchronously without blocking the whole thread. And this results in a huge increase in the number of simultaneous requests that we can handle.
- `Event` is the base type that is fed to `eventStream`. We represent each user action (join, leave, message) by corresponding subclasses of `Event`, that is, `JoinEvent`, `LeaveEvent`, and `MessageEvent`. As a side note, these classes will be serialized to their JSON counterparts while getting transferred to the client side. Hence, try to keep them as compact as possible.

Since we have a `Room`, now we will implement our `Chat` controller.

    #!java
    @With(Secure.class)
    public class Chat extends Controller {
        public static void index() {
            renderArgs.put("username", Security.getSessionUser().name);
            render();
        }
     
        public static void join() {
            Room.getInstance().publish(
                    new Room.JoinEvent(Security.getSessionUser()));
        }
     
        public static void leave() {
            Room.getInstance().publish(
                    new Room.LeaveEvent(Security.getSessionUser()));
        }
     
        public static void say(String text) {
            Room.getInstance().publish(
                    new Room.MessageEvent(Security.getSessionUser(), text));
        }
     
        public static void waitMessages(long lastReceived) {
            renderJSON(
                    // Here we use continuation to suspend the execution until a
                    // new message arrives.
                    await(Room.getInstance().nextMessages(lastReceived)),
                    new TypeToken<List<IndexedEvent<Room.Event>>>() {}.getType());
        }
    }

See the `@With(Secure.class)` annotation? Yes, only signed in Facebook users are allowed. Per see, `index()`, `join()`, `leave()`, `say()` methods are clear. The significant bit here is the `waitMessages` method. Each client will make long [XHR](http://en.wikipedia.org/wiki/XMLHttpRequest) polls to the server and wait for incoming messages. And `waitMessages` will render necessary number of messages from `Room` event stream in JSON. Since `Room.nextMessages()` returns a `Promise`, `waitMessages` will work in an asynchronous (non-blocking) manner.

![Facebook Login Entrance](1.jpg)
![Facebook Login Success](2.jpg)

Let's modify `app/views/Application/index.html` as follows to provide a link to the chat room for the signed in users.

    #!html
    #{extends 'main.html' /}
    #{set title:'Home' /}
     
    #{if user}
    <h1>Welcome, ${user.name}! #{if user.isAdmin}(admin)#{/if}</h1>
    <a href="@{Secure.logout()}">Logout</a>
    <a href="@{Chat.index()}">Chat Room</a>
    #{/if}
     
    #{else}
    #{fbLogin text:'Log In', perms:'publish_stream' /}
    #{/else}

It is time for the client side implementation of the chat room. I'll first present you the `app/views/Chat/index.html` as is, and then explain the bits in it. Here we go.

    #!html
    #{extends 'main.html' /}
    #{set title:'Chat Room' /}
    #{set 'moreScripts'}
        #{script 'jquery.scrollTo.js' /}
        #{script 'knockout.js' /}
    #{/set}
    #{set 'moreStyles'}
        #{stylesheet 'chat.css' /}
    #{/set}
     
    <div>
        <button data-bind="enable: !isJoined(), click: join">Join</button>
        <button data-bind="enable: isJoined, click: leave">Leave</button>
    </div>
     
    <div id="messages" data-bind="foreach: messages">
        <div>
            <span class="date" data-bind="text: date"></span>
            <span class="message" data-bind="if: type == 'MESSAGE'">
                <span class="user"
                      data-bind="text: user,
                                 css: { you: user == '${username}' }"></span>&gt;
                <span class="text" data-bind="text: text"></span>
            </span>
            <span class="join" data-bind="if: type == 'JOIN'">
                <span class="user" data-bind="text: user"></span> joins the room.
            </span>
            <span class="leave" data-bind="if: type == 'LEAVE'">
                <span class="user" data-bind="text: user"></span> leaves the room.
            </span>
        </div>
    </div>
     
    <form data-bind="submit: say">
        <label for="inputText">Type your text here:</label>
        <input id="inputText" type="input"
               data-bind="enable: isJoined, value: messageText" />
        <input type="submit" value="Send" data-bind="enable: isJoined" />
    </form>
     
    <script type="text/javascript">
        $(document).ready(function() {
            var XHR = {
                join: #{jsAction @join() /},
                leave: #{jsAction @leave() /},
                say: #{jsAction @say() /},
                waitMessages: #{jsAction @waitMessages(':lastReceived') /}
            };
     
            var RoomModel = function() {
                var self = this;
                var lastReceived = 0;
     
                self.isJoined = ko.observable(false);
                self.messages = ko.observableArray([]);
                self.messageText = ko.observable("");
     
                self.join = function() {
                    $.post(XHR.join(), {}, function() {
                        self.isJoined(true);
                        getMessages();
                    });
                };
     
                self.leave = function() {
                    $.post(XHR.leave(), {}, function() {
                        self.isJoined(false);
                    });
                };
     
                self.say = function() {
                    $.post(XHR.say(), {text: self.messageText()});
                    self.messageText("");
                };
     
                var getMessages = function() {
                    if (self.isJoined())
                        $.getJSON(XHR.waitMessages({lastReceived: lastReceived}), {},
                                function(events) {
                                    $(events).each(function() {
                                        self.messages.push(this.data);
                                        lastReceived = this.id;
                                    });
                                    $("#messages").scrollTo("max");
                                    getMessages();
                                });
                };
     
                $(window).unload(function() {
                    if (self.isJoined())
                        $.post(XHR.leave());
                });
            };
     
            var roomModel = new RoomModel();
            ko.applyBindings(roomModel);
        });
    </script>

Before diving into the sources, you will need to get `jquery.scrollTo.js` and `knockout.js` files. 

    #!bash
    cd public/javascripts
    wget http://flesler-plugins.googlecode.com/files/jquery.scrollTo-1.4.2-min.js -O jquery.scrollTo.js
    wget http://github.com/downloads/SteveSanderson/knockout/knockout-2.0.0.js -O knockout.js

And a simple CSS (`public/stylesheets/chat.css`) for the chat room.

    #!css
    #messages {
        height: 200px;
        overflow: auto;
        font-family: Arial, Verdana, sans-serif;
        font-size: 10pt;
        padding-bottom: 8px;
        padding-top: 8px;
    }
     
    #messages .user { font-style: oblique; }
    #messages .message .user { font-style: normal; }
    #messages .you { font-weight: bold; }
    #messages .join { color: green; }
    #messages .leave { color: red; }
    #messages .date { font-family: monospace; padding-right: 6px; }

Let me introduce you to KnockoutJS with a very simple snippet from the above mess.

1. There is a javascript object, called `RoomModel`, and it has a boolean field called `isJoined`.
2. There is a submit button to send messages to the room and we want the button to be enabled and disabled appropriately according to the `RoomModel.isJoined` flag.
3. We instantiate `RoomModel` as an observable using KnockoutJS.

       #!javascript
       var roomModel = new RoomModel();
       ko.applyBindings(roomModel);

4. We set `isJoined` to an observable as well.

       #!javascript
       self.isJoined = ko.observable(false);

5. Add `data-bind="enable: isJoined"` attribute to the button.

After three easy settings, we have the send button auto-magically binded to the `isJoined` flag. When there occurs a change on the `isJoined` variable, change will be propagated to the all dependent objects.

Another good thing about KnockoutJS observables is that the change propagation channel is bidrectional. That is, when an observable variable changes, this change gets propagated to the rest of the binded elements. Moreover, a change on the binded elements are also gets reflected to the variables as well. Let's see this in action.

1. There is an observable text field called `messageText`.
2. Message input box is binded to this observable through `data-bind="enable: isJoined, value: messageText"` attribute.

Here, `messageText` variable and the value of the input box are bidirectionally synchronized by KnockoutJS observables.
Another cool KnockoutJS feature is its `foreach` looping functionality over observable arrays. We see on in action while printing out the incoming messages. That is,

1. Messages are stored in an observable array via

       #!javascript
       self.messages = ko.observableArray([]);

2. We loop over the `messages` observable via

       #!html
       <div ... data-bind="foreach: messages">
       ...
       </div>

3. Inside the loop body, current array element is accessed as is. (Remember the list of JSON-inified `Room.Event` subclasses?)

There are other cool KnockoutJS tricks that are available in the above chat room sources (e.g., `if: type == 'MESSAGE'`, `css: { you: user == '${username}'`, etc.), but explaining all of them is out of the scope of my agenda, at least not in this blog post. I strongly advise you to take a look at the KnockoutJS [tutorials](http://learn.knockoutjs.com/) and [documentation](documentation).
