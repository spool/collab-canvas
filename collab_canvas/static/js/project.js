/* Project specific Javascript goes here. */

console.log(window.location)

const loc = window.location
const wsProtocol = 'ws://'
if (loc.protocol == 'https:'){
  wsProtocol = 'wss://'
}

const endpoint = wsProtocol + window.location.host + window.location.pathname

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
