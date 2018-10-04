"use strict";

const PROB_LINE_ON = 0.00;

class Edge {

    constructor (on) {
        this.on = on;
    }

    toggle() {
        this.on = !this.on;
    }
}


function getRandomInt(max) {
    //Stolen from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random
    //Using 0 as min
    var min = Math.ceil(0);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}



class Grid {

    constructor (size, divisions) {
        this.size = size;
        this.divisions = divisions;
        this.cells_per_division = this.size / this.divisions;
        this.edges_h = this.initializeEdges(size);
        this.edges_v = this.initializeEdges(size);
        this.edges_d_se = this.initializeEdges(size);
        this.edges_d_sw = this.initializeEdges(size);
        this.divisions_started = this.initializeEdges(size);

        // Sketchy attempt to iterate over generated 2d arrays
        for (let x = 0; x < size; x++) {
            for (let y = 0; y < size; y++) {
                this.edges_h[x][y] = new Edge(Math.random() < PROB_LINE_ON);
                this.edges_v[x][y] = new Edge(Math.random() < PROB_LINE_ON);
                this.edges_d_se[x][y] = new Edge(Math.random() < PROB_LINE_ON);
                this.edges_d_sw[x][y] = new Edge(Math.random() < PROB_LINE_ON);
            }
        }
        this.focus = new p5.Vector(getRandomInt(this.divisions), getRandomInt(this.divisions));
    }

    initializeEdges(size) {
        // Sketchy function to initialize an array in javascript...
        let edges = new Array(size);
        for (let x=0; x < size; x++) {
            edges[x] = new Array(size);
        }
        return edges;
    }

    lightLine(x0,  y0,  x1,  y1) {
        stroke(64);
        line(x0, y0, x1, y1);
    }

    darkLine(x0,  y0,  x1,  y1) {
        stroke(255);
        line(x0, y0, x1, y1);
    }

    toggleLine(x0,  y0,  x1,  y1) {
        // work out which array we need to modify
        if (x0 == x1) {
          this.edges_v[x0][min(y0, y1)].toggle();
        }
        else if (y0 == y1) {
          this.edges_h[min(x0, x1)][y0].toggle();
        }
        else if ((x1 - x0) == (y1 - y0)) {
          this.edges_d_se[min(x0, x1)][min(y0, y1)].toggle();
        }
        else {
          this.edges_d_sw[min(x0, x1)][min(y0, y1)].toggle();
        }

        // mark this division as started
        let current_division_x = Math.trunc(x0 / this.cells_per_division);
        let current_division_y = Math.trunc(y0 / this.cells_per_division);
        if (x0 % cells_per_division == 0 || y0 % cells_per_division == 0){
            return;

        }

        if (!this.divisions_started[current_division_x][current_division_y]) {
            this.divisions_started[current_division_x][current_division_y] = true;
        }
    }

    setFocus(x, y) {
        this.focus.x = Math.trunc(x);
        if (this.focus.x < 0){
            this.focus.x += this.divisions;
        }
        if (this.focus.x >= this.divisions){
            this.focus.x -= this.divisions;
        }

        this.focus.y = Math.trunc(y);
        if (this.focus.y < 0)
            this.focus.y += this.divisions;
        if (this.focus.y >= this.divisions)
            this.focus.y -= this.divisions;
    }

    setRandomFocus() {
        // select an unstarted cell, and set focus to this
        let unstarted_exists = false;
        for (x = 0; x < this.divisions; x++){
            for (y = 0; y < this.divisions; y++) {
                if (!this.divisions_started[x][y]) {
                    unstarted_exists = true;
                    break;
                }
            }
        }

        if (!unstarted_exists) {
          // all divisions have been started - pick one anyway
          this.focus.x = (random(this.divisions));
          this.focus.y = (random(this.divisions));
        }
        else {
          let division = this.pickNewDivision();
          this.focus.x = division[0];
          this.focus.y = division[1];
        }
    }

    drawSubgrid() {
        stroke(255, 0, 0);
        strokeWeight(0.05);
        rect(0.5 * this.cells_per_division, 0.5 * this.cells_per_division, this.cells_per_division, this.cells_per_division);
        stroke(0);
        strokeWeight(0.02);

        for (let x = 0; x < 2 * this.cells_per_division; x++) {
            for (let y = 0; y < 2 * this.cells_per_division; y++) {
                //Don't understand how it's not this.focus ....
                let ix = Math.trunc(this.focus.x * this.cells_per_division) - (this.cells_per_division / 2) + x;

                if (ix >= size) ix -= size;
                if (ix < 0) ix += size;

                let iy = Math.trunc(this.focus.y * this.cells_per_division) - (this.cells_per_division / 2) + y;
                if (iy >= size) iy -= size;
                if (iy < 0) iy += size;

                // draw horiz
                this.lightLine(x, y, x + 1, y);
                if (this.edges_h[ix][iy].on) this.darkLine(x, y, x + 1, y);

                // draw vert
                this.lightLine(x, y, x, y + 1);
                if (this.edges_v[ix][iy].on) this.darkLine(x, y, x, y + 1);

                // draw diag se
                this.lightLine(x, y, x + 1, y + 1);
                if (this.edges_d_se[ix][iy].on) this.darkLine(x, y, x + 1, y + 1);

                // draw diag sw
                this.lightLine(x, y + 1, x + 1, y);
                if (this.edges_d_sw[ix][iy].on) this.darkLine(x, y + 1, x + 1, y);
            }
        }

        fill(0, 0, 0, 128);
        noStroke();

        // draw horizontal bands
        rect(0, 0, width, 0.5 * this.cells_per_division);
        rect(0, 1.5 * this.cells_per_division, width, 0.5 * this.cells_per_division);

        rect(0, 0.5 * this.cells_per_division, 0.5 * this.cells_per_division, this.cells_per_division);
        rect(1.5 * this.cells_per_division, 0.5 * this.cells_per_division, 0.5 * this.cells_per_division, this.cells_per_division);
    }

    draw() {
        stroke(255, 0, 0);
        strokeWeight(0.05);
        rect(this.focus.x * this.cells_per_division, this.focus.y * this.cells_per_division, this.cells_per_division, this.cells_per_division);

        stroke(0);
        strokeWeight(0.02);

        for (let x = 0; x < size; x++) {
            for (let y = 0; y < size; y++) {
                // draw horiz
                this.lightLine(x, y, x + 1, y);
                if (this.edges_h[x][y].on) this.darkLine(x, y, x + 1, y);

                // draw vert
                this.lightLine(x, y, x, y + 1);
                if (this.edges_v[x][y].on) this.darkLine(x, y, x, y + 1);

                // draw diag se
                this.lightLine(x, y, x + 1, y + 1);
                if (this.edges_d_se[x][y].on) this.darkLine(x, y, x + 1, y + 1);

                // draw diag sw
                this.lightLine(x, y + 1, x + 1, y);
                if (this.edges_d_sw[x][y].on) this.darkLine(x, y + 1, x + 1, y);
            }
        }
    }

    serialize() {
        let data = new str[4];
        data[0] = "";
        data[1] = "";
        data[2] = "";
        data[3] = "";

        for (let x = 0; x < this.size; x++) {
            for (let y = 0; y < this.size; y++) {
                data[0] = data[0] + (this.edges_h[x][y].on ? "1" : "0");
                data[1] = data[1] + (this.edges_v[x][y].on ? "1" : "0");
                data[2] = data[2] + (this.edges_d_se[x][y].on ? "1" : "0");
                data[3] = data[3] + (this.edges_d_sw[x][y].on ? "1" : "0");
            }
        }
        return data;
    }

    /// XXX processing.js: can't have space between Type and []
    load(data) {
        for (let x=0; x < this.size; x++){
            for (let y=0; y < this.size; y++) {
                this.edges_h[x][y].on = (data[0].charAt((x * (size)) + y) == "1");
                this.edges_v[x][y].on = (data[1].charAt((x * size) + y) == "1");
                this.edges_d_se[x][y].on = (data[2].charAt((x * size) + y) == "1");
                this.edges_d_sw[x][y].on = (data[3].charAt((x * size) + y) == "1");

                let current_division_x = Math.trunc(x / this.cells_per_division);
                let current_division_y = Math.trunc(y / this.cells_per_division);

                if (!this.divisions_started[current_division_x][current_division_y] && (this.edges_h[x][y].on || this.edges_v[x][y].on || this.edges_d_se[x][y].on || this.edges_d_sw[x][y].on)) {
                    this.divisions_started[current_division_x][current_division_y] = true;
                }
            }
        }
    }

    clear() {
        for (let x = 0; x < this.size; x++) {
            for (let y = 0; y < this.size; y++) {
                this.edges_h[x][y].on = false;
                this.edges_v[x][y].on = false;
                this.edges_d_se[x][y].on = false;
                this.edges_d_sw[x][y].on = false;
            }
        }
    }

    pickNewDivision() {
        // Think it's defined below
        // int[][] possibilities;
        let possibility_count = 0;

        // XXX processing.js doesn't seem to like declaration + init on same line...
        // let possibilities = new int[this.divisions * this.size][2];
        let possibilities = [this.divisions * this.size][2];

        for (let x = 0; x < this.divisions; x++){
            for (let y = 0; y < this.divisions; y++) {
                if (this.divisions_started[x][y]) {
                    // possibilities[possibility_count] = new int[] { x, y };
                    possibilities[possibility_count] = [x, y];
                    possibility_count++;
                }
            }
        }

        if (possibility_count == 0){
            return new Array(0, 0);
        }

        let found = false;
        let attempts_left = 500;
        while (!found && (attempts_left > 0)) {
            let source = possibilities[Math.trunc(random(possibility_count))];
            // relations = new int[][] { { -1, 0 }, { 1, 0 }, { 0, -1 }, { 0, 1 } };
            let relations = [ [-1, 0], [1, 0], [0, -1], [0, 1] ];
            // dir[] = relations[int(random(relations.length))];
            let dir = relations[Math.trunc(random(relations.length))];

            let nx = source[0] + dir[0];
            if (nx < 0) nx += this.divisions;
            if (nx >= this.divisions) nx -= this.divisions;

            let ny = source[1] + dir[1];
            if (ny < 0) ny += this.divisions;
            if (ny >= this.divisions) ny -= this.divisions;

            if (!this.divisions_started[nx][ny]) {
                return [ nx, ny ];
            }
        } // while

        // oh dear, we've made many attempts but not found a free neighbour.
        // return the first cell in desparation.
        return [ 0, 0 ]
    }
}
