// Copyright (c) Microsoft. All rights reserved.
// Modifications  
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

'use strict';

// Setup basic express server
var express = require('express');
var app = express();
var server = require('http').createServer(app);
var port = process.env.PORT || 3000;

var url = require('url');
var WebSocketServer = require('ws').Server;
var wss = new WebSocketServer({ server: server });

var wordCount = {words:{}};

// Set up a broadcast function
wss.broadcast = function broadcast(data) {
  wss.clients.forEach(function each(client) {
    client.send(data);
  });
};

function handleEvent(ehEvent) {
  // extract the name of the target device from the command message
  var words = data.word;
  
  // update the counter for the received word
  wordCount.words[data.word] = data.count;

  // send the status to listening clients
  wss.broadcast(JSON.stringify(wordCount));
  //console.log('Event Received: ');
  //console.log(JSON.stringify(ehEvent.body));
};

// When a Websocket client connects, set up an event handler for received messages (command)
wss.on('connection', function connection(ws) {
   ws.on('message', function incoming(command) {
    var data = JSON.parse(command);

    handleEvent(data);
  });
});


// Routing for static content
app.use(express.static(__dirname + '/public'));

app.get('/log', function(req, res){
    res.send(JSON.stringify(recentEvents));  
});
// We use server.listen rather than app.listen becuase we need to use the server for both WebSockets and basic HTTP
server.listen(port, function () {
    console.log('Listening on ' + server.address().port) 
});
