/* Project specific Javascript goes here. */

/* Consider trying ES6  */

console.log(window.location)

const channelsWebSocketPath = ''
const loc = window.location
const wsStart = 'ws://'
if (loc.protocol == 'https:'){
  wsStart = 'wss://'
}

/*const endpoint = wsStart + loc.host + loc.pathname + 'channels'*/
const endpoint = wsStart + loc.host + loc.pathname + 'channels'

const socket = new WebSocket(endpoint)

socket.onmessage = function(e){
  console.log("message", e)
}

socket.onopen = function(e){
  console.log("open", e)
}

socket.onerror = function(e){
  console.log("error", e)
}

socket.onclose = function(e){
  console.log("close", e)
}
