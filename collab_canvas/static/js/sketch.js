"use strict";

const MODE_WHOLE = 0;
const MODE_SINGLE = 1;

const CELL_WIDTH = 8;
const CELL_DIVISIONS = 8;

const CELL_COUNT = 64;

var mode = MODE_SINGLE;  //let variables have local scope
var grid;    //var is a global variable
//var origin;  //var is a global variable

/*
function draw() {
    background(0);
    noFill();

    switch (mode) {
        case MODE_WHOLE:
              scale(CELL_WIDTH, CELL_WIDTH);
              grid.draw();
              break;
        case MODE_SINGLE:
              scale(CELL_WIDTH * CELL_DIVISIONS * 0.5, CELL_WIDTH * CELL_DIVISIONS * 0.5);
              grid.drawSubgrid();
              break;
    }
}*/

/*
function setCell(cell) {
    grid.setFocus(cell % 8, Math.floor(cell / 8));
}
*/

function mouseDragged() {
    let normalized = createVector(0, 0);   // normalized position of mouse, in global grid co-ordinates
    let distance = createVector(0, 0);     // normalized distance to nearest node (0..1)
    let nearest = createVector(0, 0);      // co-ordinates of nearest node
    let origin = createVector(-1, -1);     // initial vector to map beginning of drag to end
    let data = {
        x: mouseX,
        y: mouseY
    };

    if (mode == MODE_WHOLE) {
        normalized.x = mouseX / CELL_WIDTH;
        normalized.y = mouseY / CELL_WIDTH;
    }
    else {
        normalized.x = ((grid.focus.x - 0.5) * grid.cells_per_division) + (mouseX / (CELL_WIDTH * CELL_DIVISIONS * 0.5));
        normalized.y = ((grid.focus.y - 0.5) * grid.cells_per_division) + (mouseY / (CELL_WIDTH * CELL_DIVISIONS * 0.5));

    if (normalized.x < (grid.focus.x * grid.cells_per_division) || normalized.x > (grid.focus.x * grid.cells_per_division) + grid.cells_per_division ||
        normalized.y < (grid.focus.y * grid.cells_per_division) || normalized.y > (grid.focus.y * grid.cells_per_division) + grid.cells_per_division) {
          return;
        }
    }

    distance.x = abs(round(normalized.x) - normalized.x);
    distance.y = abs(round(normalized.y) - normalized.y);
    nearest.x = round(normalized.x);
    nearest.y = round(normalized.y);

    /*let logToggleLine = {
        originT: origin,
        nearest: nearest
    }
    socket.emit("toggleLine", logToggleLine);
    */
    /*socket.emit('mouse', data);*/

    if (dist(distance.x, distance.y, 0, 0) < 0.5) {
    // if we ar
        stroke(0);
        strokeWeight(1.5);
        if (origin.x == -1) {
            // don't have a current drag origin - set.
            origin.x = nearest.x;
            origin.y = nearest.y;
        }
        else if ((origin.x != -1) && ((origin.x != nearest.x) || (origin.y != nearest.y))) {
            // new line to add
            // grid.toggleLine((int) origin.x, (int) origin.y, (int) nearest.x,
            // (int) nearest.y);
            /*console.log("About to toggleLine. Variables:", origin.x, origin.y,
                nearest.x, nearest.y);*/

            grid.toggleLine(origin.x,  origin.y,  nearest.x,  nearest.y);
            // println("toggling " + origin.x + ", " + origin.y);
            origin.x = nearest.x;
            origin.y = nearest.y;
        }
    }
    /*socket.emit('mouse', data);*/
}

    /*
function mouseDragged() {
    let data = {
        x: mouseX,
        y: mouseY
    };
    //socket.emit("toggleLine", {a: 'dog', b:'cat'});
    socket.emit('mouse', data);
}
*/

    /*
function mouseEnded() {
    origin.x = -1;
    origin.y = -1;
}
*/


function getData() {
    return grid.serialize();
}

function getCell() {
    let cell = Math.floor(grid.focus.x + 8 * grid.focus.y);

    return cell;
}

// Keep track of our socket connection
//var socket;

function setup() {
    //createCanvas(600, 600);
    createCanvas(CELL_WIDTH * CELL_COUNT, CELL_WIDTH * CELL_COUNT);
    smooth();

    grid = new Grid(CELL_COUNT, CELL_DIVISIONS);
    //origin = new createVector(-1, -1);
    //origin = createVector(-1, -1);
    background(0);
    noFill();
  // Start a socket connection to the server
  // Some day we would run this server somewhere else
    //socket = io.connect('http://localhost:3000');
  // We make a named event called 'mouse' and write an
  // anonymous callback function
/*
  socket.on('mouse',
    // When we receive data
    function(data) {
        console.log("Getting data from mouse");
      console.log("Got: " + data.x + " " + data.y);
        socket.broadcast.emit('mouse', data);
        socket.broadcast.emit('finished a drag');
      // Draw a blue circle
        //fill(0,0,255);
        //noStroke();
        //ellipse(data.x, data.y, 20, 20);
    }
  );
  */
}

function draw() {
    switch (mode) {
        case MODE_WHOLE:
            scale(CELL_WIDTH, CELL_WIDTH);
            grid.draw();
            break;
        case MODE_SINGLE:
            scale(CELL_WIDTH * CELL_DIVISIONS * 0.5, CELL_WIDTH * CELL_DIVISIONS * 0.5);
            grid.drawSubgrid();
            break;
    }
}



/*
function load_empty()
{
	$.get("sfit-draw.pjs?" + (Math.random() * 5000),
		function(code) {
			canvas = $("#canvas")[0];
			processing = Processing(canvas, code);
		}
	);
}

function mouse() {
  // Draw some white circles
  fill(255);
  noStroke();
  ellipse(mouseX, touchY, 5, 5);
  // Send the mouse coordinates
  sendMouse(mouseX, touchY);
}

// Function for sending to the socket
function sendMouse(xpos, ypos) {
  // We are sending!
  console.log("sendmouse: " + xpos + " " + ypos);

  // Make a little object with  and y
  var data = {
    x: xpos,
    y: ypos
  };

  // Send that object to the socket
  socket.emit('mouse', data);
}*/
