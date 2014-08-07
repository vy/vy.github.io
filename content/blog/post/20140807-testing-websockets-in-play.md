---
kind: article
created_at: 2014-08-07 09:28 EET
title: Testing WebSockets in Play Framework
tags:
  - java
  - play framework
  - websocket
---

In a recent job interview, I was asked to implement a fully fledged (that is,
including unit and integration tests) [Lubang Menggali
(Mancala)](http://en.wikipedia.org/wiki/Mancala) game, where multiple users are
allowed to play in real-time. I went with [Play
Framework](http://www.playframework.com/) and used
[WebSocket](http://en.wikipedia.org/wiki/WebSocket)s to implement the real-time
server-client communication. (You can find the complete sources
[here](https://github.com/vy/lubang-menggali).) Play provides necessary leverage
for the integration tests -- start the server, connect two browsers to it, click
on the buttons to make a move and check the board updates. However, the tricky
bit was the implementation of unit tests for `WebSocket` handlers.

Preliminaries
=============

A typical `WebSocket` handler in Play has the following entry point for the
request dispatcher.

    #!java
    public static WebSocket<JsonNode> join() {
        return new WebSocket<JsonNode>() {
            @Override
            public void onReady(In<JsonNode> in, Out<JsonNode> out) {
                // ...
            }
        }
    }

When a request hits to `join()`, the function returns a new `WebSocket`
instance, where `onReady()` will be invoked upon connection establishment. After
that, the book keeping of the input and output sockets are delegated to the
programmer. Note that the client-server communication is performed in JSON
messages in the above code snippet.

Mocking
=======

In order to mock a client-server `WebSocket` communication, I need mock
`WebSocket.In` and `WebSocket.Out` class implementations. For that purpose, I
first tried googling alternatives and checked what other people have done
previously, but did not find much material. Hence, I came up with the following
`MockInputWebSocket`.

    #!java
    @ThreadSafe
    class MockInputWebSocket {

        protected final List<F.Callback<JsonNode>> messageListeners =
                Collections.synchronizedList(new ArrayList<F.Callback<JsonNode>>());

        protected final List<F.Callback0> closeListeners =
                Collections.synchronizedList(new ArrayList<F.Callback0>());

        protected final WebSocket.In<JsonNode> inputSocket = new WebSocket.In<JsonNode>() {

            @Override
            public void onMessage(F.Callback<JsonNode> callback) { messageListeners.add(callback); }

            @Override
            public void onClose(F.Callback0 callback) { closeListeners.add(callback); }

        };

        public void write(JsonNode data) throws Throwable {
            for (F.Callback<JsonNode> listener : messageListeners)
                listener.invoke(data);
        }

        public void close() throws Throwable {
            for (F.Callback0 listener : closeListeners)
                listener.invoke();
        }

        public WebSocket.In<JsonNode> getInputSocket() { return inputSocket; }

    }

Here, I first implement a `WebSocket.In` object, where message and close event
listeners can register themselves to `messageListeners` and `closeListeners`
list, respectively. Next, in order to pass data to the socket listeners, I wrote
my custom `write()` and `close()` methods.

I also implemented `MockOutputWebSocket` similarly:

    #!java
    @ThreadSafe
    class MockOutputWebSocket {

        private final static ObjectMapper objectMapper = new ObjectMapper();

        protected final BlockingQueue<JsonNode> messageQueue = new LinkedBlockingQueue<>();

        protected final WebSocket.Out<JsonNode> outputSocket = new WebSocket.Out<JsonNode>() {

            @Override
            public void write(JsonNode frame) { messageQueue.add(frame); }

            @Override
            public void close() {
                try { messageQueue.add(objectMapper.readTree("{\"closed\": true}")); }
                // This should not happen.
                catch (IOException e) { throw new RuntimeException(e); }
            }
        };

        public BlockingQueue<JsonNode> getMessageQueue() { return messageQueue; }

        public WebSocket.Out<JsonNode> getOutputSocket() { return outputSocket; }

    }

If we would forget about the custom close message hack (nasty!) in `close()`
method of the implemented `WebSocket.Out` class, things are self-explanative
here as well. That is, when we receive a new message, we push it to
`messageQueue`. The test user will be able to consume the messages written to
the mock output socket by polling `JsonData` from the `messageQueue`.

Since I come this far, I also implemented an entire `WebSocket` mock
(`MockWebSocket`) that employs the aforementioned `MockInputWebSocket` and
`MockOutputWebSocket` as follows.

    #!java
    @ThreadSafe
    class MockWebSocket {

        protected final MockInputWebSocket mockInput = new MockInputWebSocket();
        protected final MockOutputWebSocket mockOutput = new MockOutputWebSocket();
        protected final WebSocket<JsonNode> socket;

        MockWebSocket(WebSocket<JsonNode> socket) {
            this.socket = socket;
            socket.onReady(mockInput.getInputSocket(), mockOutput.getOutputSocket());
        }

        public JsonNode read() throws InterruptedException {
            return mockOutput.getMessageQueue().poll(1, TimeUnit.SECONDS);
        }

        public void write(JsonNode data) throws Throwable { mockInput.write(data); }

        public void close() throws Throwable { mockInput.close(); }

    }

`MockWebSocket` provides the caller an interface such that the two-way
`WebSocket` communication can be intercepted through provided `read()`,
`write()` and `close()` methods -- much like a regular network socket.

Conclusion
==========

Remember that I used JSON as the messaging medium. For that purpose, I created a
couple of event classes (e.g., `WaitingForOpponent`, `ReadyToStart`,
`IllegalMove`, etc.) and used [Jackson](http://jackson.codehaus.org/) for
POJO-JSON (de)serialization. Next, I integrated my brand new `MockWebSocket`
into the unit tests as follows.

    #!java
    private static <T> T readPojo(MockWebSocket socket, Class<T> clazz)
            throws InterruptedException, JsonProcessingException {
        JsonNode data = socket.read();
        assertThat(data).isNotNull();
        try { return objectMapper.convertValue(data, clazz); }
        catch (IllegalArgumentException iae) {
            throw new IllegalArgumentException(
                    "Invalid JSON: " + objectMapper.writeValueAsString(data), iae);
        }
    }

    private static void writeMove(MockWebSocket socket, Object pit) throws Throwable {
        socket.write(objectMapper.valueToTree(pit));
    }

    @Test
    public void testJoin() throws Throwable {
        // Introduce the first user and read the "WaitingForOpponent" message.
        MockWebSocket fstSocket = new MockWebSocket(Application.join());
        WaitingForOpponent fstWfo = readPojo(fstSocket, WaitingForOpponent.class);
        assertThat(Application.getPendingPlayers().size()).isEqualTo(1);
        assertThat(Application.getGames().size()).isEqualTo(0);

        // Introduce the second user and read the."WaitingForOpponent" message.
        MockWebSocket sndSocket = new MockWebSocket(Application.join());
        WaitingForOpponent sndWfo = readPojo(sndSocket, WaitingForOpponent.class);
        assertThat(fstWfo.playerId.equals(sndWfo.playerId)).isFalse();

        // Validate "ReadyToStart" messages.
        ReadyToStart fstRts = readPojo(fstSocket, ReadyToStart.class);
        ReadyToStart sndRts = readPojo(sndSocket, ReadyToStart.class);
        assertThat(Application.getGames().size()).isEqualTo(1);
        assertThat(Application.getPendingPlayers().size()).isEqualTo(0);
        assertThat(fstRts.nextPlayerId).isEqualTo(sndRts.nextPlayerId);
        assertThat(fstRts.opponentId).isEqualTo(sndWfo.playerId);
        assertThat(sndRts.opponentId).isEqualTo(fstWfo.playerId);

        // Let 2nd player make a move, while this is not his turn.
        writeMove(sndSocket, 0);
        IllegalMove im = readPojo(sndSocket, IllegalMove.class);
        assertThat(im.reason).isEqualTo("It is opponent's turn.");

        // Let 1st player make a move to an invalid pit index.
        writeMove(fstSocket, "n/a");
        im = readPojo(fstSocket, IllegalMove.class);
        assertThat(im.reason).matches("^Invalid pit index: .*");

        // Let 1st player make a move with a negative pit index.
        writeMove(fstSocket, -1);
        im = readPojo(fstSocket, IllegalMove.class);
        assertThat(im.reason).matches("^Invalid pit index: .*");

        // ...
    }

I suppose I have got a nearly 99% code coverage of the game engine by using the
mock `WebSocket`s. I hope this scheme would help others trying to do a similar
testing stuff.
