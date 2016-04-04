/**
 * Created by ansaev on 03.04.16.
 */
var ws = new WebSocket("ws://localhost:8888/download_progress/"+client_id);
ws.onopen = function() {
   ws.send("Hello, world");
};
ws.onmessage = function (evt) {
   alert(evt.data);
};
