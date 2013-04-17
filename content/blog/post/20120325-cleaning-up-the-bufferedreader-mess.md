---
kind: article
created_at: 2012-03-25 14:36 EET
title: Cleaning up the BufferedReader Mess in a Proxy Server 
tags:
  - java
---

A couple of weeks ago, friends from the university knocked my door. They were given an assignment to implement a HTTP [Proxy Server](http://en.wikipedia.org/wiki/Proxy_server). I tried to do my best and told them the basics. That is, they should first simply read the HTTP headers line by line, and then read the rest of the stream in bytes. After that, the mechanics are easy:

1. Pass the request headers from browser to the server, which is, provided by `Host` header in the browser request,
2. Pass back the response sent by server to the browser.

Easy, right? Just before the homework due, my door knocked again. Suprise! Suprise! They couldn't properly read the server data after reading the headers. It sounded like a trivial problem at first, as hours pass by while I'm trying to fix the code, it appeared to be not like so. Since you are here for the code, let me first show you the working draft.

    #!java
    import java.io.*;
    import java.net.InetAddress;
    import java.net.ServerSocket;
    import java.net.Socket;
    import java.util.ArrayList;
    import java.util.List;
    import java.util.regex.Pattern;
    
    public class Main {
        static final int PROXY_PORT = 8080;
        static final String PROXY_HOST = "localhost";
        static final String NEWLINE = "\r\n";
     
        public static void main(String[] args) throws Exception {
            ServerSocket proxySocket = new ServerSocket(
                    PROXY_PORT, 32, InetAddress.getByName(PROXY_HOST));
     
            while (true) {
                // Accept the incoming connection.
                Socket clientSocket = proxySocket.accept();
                BufferedInputStream clientInputStream = new BufferedInputStream(
                        new DataInputStream(clientSocket.getInputStream()));
                OutputStream clientOutputStream = new DataOutputStream(
                        clientSocket.getOutputStream());
     
                // Read client headers.
                List<String> clientHeaders = readHeaders(clientInputStream);
                display("Client Headers", clientHeaders);
     
                // Locate the web server.
                String hostHeader = getHeader(clientHeaders, "Host");
                display("HostHeader", hostHeader);
                String[] hostHeaders = hostHeader.split(":");
                String hostName = hostHeaders[0];
                display("HostName", hostName);
                int hostPort = hostHeaders.length > 1
                        ? Integer.parseInt(hostHeaders[1]) : 80;
                display("HostPort", hostPort);
     
                // Connect to the web server.
                Socket serverSocket = new Socket(hostName, hostPort);
                BufferedInputStream serverInputStream = new BufferedInputStream(
                        new DataInputStream(serverSocket.getInputStream()));
                OutputStream serverOutputStream = new DataOutputStream(
                        serverSocket.getOutputStream());
     
                // Pass the client request to the web server.
                writeHeaders(serverOutputStream, clientHeaders);
                serverSocket.shutdownOutput();
                display("Sent server headers.");
     
                // Read web server response headers.
                List<String> serverHeaders = readHeaders(serverInputStream);
                display("ServerHeaders", serverHeaders);
     
                // Read web server response data.
                byte[] serverData = readData(serverInputStream);
                display("ServerDataLength", serverData.length);
     
                // Try to sign the response data.
                byte[] signedData = sign(serverHeaders, serverData);
     
                // Pass the web server response to the client.
                writeHeaders(clientOutputStream, serverHeaders);
                clientOutputStream.write(signedData);
     
                display("---------------------");
                display("");
     
                serverSocket.close();
                clientSocket.close();
            }
        }
     
        static byte[] readData(InputStream stream) throws Exception {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            BufferedInputStream bufferedStream = new BufferedInputStream(stream);
            byte[] buf = new byte[8192];
            int len;
            while ((len = bufferedStream.read(buf)) > 0)
                baos.write(buf, 0, len);
            return baos.toByteArray();
        }
     
        static void writeHeaders(OutputStream stream, List<String> headers)
                throws IOException {
            StringBuilder builder = new StringBuilder();
            for (String header : headers) {
                builder.append(header);
                builder.append(NEWLINE);
            }
            builder.append(NEWLINE);
            stream.write(builder.toString().getBytes());
        }
     
        static List<String> readHeaders(BufferedInputStream stream)
                throws Exception {
            List<String> lines = new ArrayList<String>();
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(stream));
            String line;
            long nRead = NEWLINE.length();  // For the last empty line.
            stream.mark(Integer.MAX_VALUE);
            while ((line = reader.readLine()) != null && !(line.isEmpty())) {
                nRead += line.getBytes().length + NEWLINE.length();
                if (!line.startsWith("Accept-Encoding"))    // Avoid compressed pages.
                    lines.add(line);
            }
            stream.reset();
            long nSkipped = stream.skip(nRead);
            assert (nSkipped == nRead);
            return lines;
        }
     
        static String getHeader(List<String> headers, String name) {
            for (String line : headers)
                if (line.startsWith(name))
                    return line.split(": ")[1];
            return null;
        }
     
        static byte[] sign(List<String> headers, byte[] data) {
            String header = getHeader(headers, "Content-Type");
            if (header == null || !header.startsWith("text/html"))
                return data;
            String content = new String(data);
            Pattern pattern = Pattern.compile("^(.*<title>)(.*</title>.*)$",
                    Pattern.CASE_INSENSITIVE | Pattern.MULTILINE);
            return pattern.matcher(content).replaceFirst("$1[VY] $2").getBytes();
        }
     
        static void display(String title, List<String> lines) {
            System.out.println("### <" + title + "> ###");
            for (String line : lines)
                System.out.println("'" + line + "'");
            System.out.println("### </" + title + "> ###");
        }
     
        static void display(String title, Object obj) {
            System.out.println("### " + title + ": '" + obj + "'");
        }
     
        static void display(Object obj) {
            System.out.println("### " + obj);
        }
     
        static void display() {
            System.out.println();
        }
    }

The truth is, it took my almost four hours to find and squash the bug. `serverSocket.shutdownOutput()` was a low hanging one, it solved the problem of web server waiting to start sending data. But take a closer look at the `readHeaders()` method. You see the mess? Particularly, the ones with stream arithmetic using `mark()`, `reset()` and `skip()` calls. The problem was, in order to make `readLine()` requests on an `InputStream`, you first need to wrap it with a `BufferedReader`. But once you wrap it up and make a call to `readLine()`, `BufferedReader` buffers the input stream to a position that is much more advanced than you generally expect it to be. Hence, after you finish reading headers and continue with reading the response data in bytes, `read()` tells you that there is nothing left to read. To avoid such nasty bugs, after reading from an `InputStream` using some sort of buffered reader, do not forget to reset the stream to a position where you expect it to be.
