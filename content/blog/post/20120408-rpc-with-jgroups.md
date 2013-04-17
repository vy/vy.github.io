---
kind: article
created_at: 2012-04-08 05:11 EET
title: RPC (Remote Procedure Call) with JGroup
tags:
  - java
  - jgroups
---

JGroups constitutes a perfect medium for RPC between nodes in a cluster. Here, I share a very basic JGroups RPC example.

    #!java
    import org.jgroups.Address;
    import org.jgroups.JChannel;
    import org.jgroups.blocks.*;
    import org.jgroups.util.RspList;
    
    import java.lang.reflect.Method;
    import java.util.HashMap;
    import java.util.Map;
    
    public final class RpcPeer {
        private final JChannel rpcChannel;
        private final RpcDispatcher rpcDispatcher;
        private final RequestOptions requestOptions;
    
        private static final Map<Short, Method> methods;
    
        private static final short CALLABLE = 0;
    
        static {
            methods = new HashMap<Short, Method>();
            try {
                methods.put(CALLABLE, RpcPeer.class.getMethod("callable", Long.class));
            } catch (NoSuchMethodException e) {
                throw new RuntimeException(e);
            }
        }
    
        RpcPeer() throws Exception {
            rpcChannel = ChannelFactory.getInstance().create();
            rpcDispatcher = new RpcDispatcher(rpcChannel, this);
            rpcDispatcher.setMethodLookup(new MethodLookup() {
                public Method findMethod(short id) {
                    return methods.get(id);
                }
            });
            requestOptions = new RequestOptions(ResponseMode.GET_ALL, 3000);
        }
    
        public void connect(String name) throws Exception {
            rpcChannel.connect(name);
        }
    
        public void disconnect() {
            rpcChannel.disconnect();
            rpcChannel.close();
        }
    
        @SuppressWarnings("unused")
        public String callable(Long n) {
            return String.format("%s received %s.", rpcChannel.getAddress(), n);
        }
    
        public Long call(Address address, Long n) throws Exception {
            MethodCall methodCall = new MethodCall(CALLABLE, (long) 10);
            return rpcDispatcher.callRemoteMethod(
                    address, methodCall, requestOptions);
        }
    
        public RspList<Object> call(Long n) throws Exception {
            MethodCall methodCall = new MethodCall(CALLABLE, n);
            return rpcDispatcher.callRemoteMethods(
                    null, methodCall, requestOptions);
        }
    }

I think (at least, hope) the code is self-explanatory. A minor important point here is the RPC channel. Per see, I use `ChannelFactory.getInstance().create()` method to create the channel. `ChannelFactory` is a shortcut class to create multiple channels sharing the same transport. (See my <%= link_to "Shared Transport in JGroups", @items["/blog/post/20120319-shared-transport-in-jgroups/"] %> post for details.) That is, you need to have a separate JGroups channel reserved for RPC communication. All other messages sent/received using this channel will be consumed and ignored by the `RpcDispatcher`.
