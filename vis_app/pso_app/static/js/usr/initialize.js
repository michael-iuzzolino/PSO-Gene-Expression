"use strict";
var socket;

var histogram;
var xScale, yScale;
var xHistScale, yHistScale;
var svg_width = 300;
var svg_height = 300;
var height, width;
var histogramHeight, histogramWidth;
var objective_function, objective_string, bounds;
var THREAD_RUNNING = false;
var num_histogram_bins = 12;

var transition = d3.transition().duration(250);

var PSO_param_keys = {
    "C1"            : "C1 (cognative constant)",
    "C2"            : "C2 (social constant)",
    "W"             : "W (inertial weight)",
    "maxiter"       : "Max Iterations",
    "num_agents"    : "Number of Agents",
}
// Init params
var PSO_params = {
    "C1"            : 1.496180,          // cognative constant
    "C2"            : 2.496180,          // social constant
    "W"             : 0.5,               // constant inertia weight (how much to weigh the previous velocity)
    "maxiter"       : 20,
    "num_agents"    : 50,
}

function resetPlots() {
    createPlot();
}


function resetRunButton() {
    d3.select("#run_button").attr("value", "Finished");
    setTimeout(function() {
        d3.select("#run_button").attr("value", "Run PSO");
    }, 2000);
}

function initializeControls() {

    d3.select("#controls_div").remove();

    var controlsDiv = d3.select("#controls_div_container").append("div").attr("id", "controls_div");

    var params = Object.keys(PSO_params);

    var param_div;
    for (var i=0; i < params.length; i++) {
        var param = params[i];
        param_div = controlsDiv.append("div")
            .attr("id", param + "_div")
            .attr("class", "param_container");
        param_div.append("label").attr("class", "param_label").html(PSO_param_keys[param]);
        param_div.append("input")
            .attr("class", "param_input_text")
            .attr("type", "text")
            .attr("name", param)
            .attr("value", PSO_params[param])
            .on("change", function() {
                PSO_params[this.name] = parseFloat(this.value);
            });
    }

    // Run Button
    // -------------------------------------------------------
    controlsDiv.append("input")
        .attr("id", "run_button")
        .attr("type", "button")
        .attr("value", "Run PSO")
        .on('click', function() {
            if (THREAD_RUNNING) {
                console.log("Thread already running.");
                return;
            }

            resetPlots();
            this.value = "Running...";
            THREAD_RUNNING = true;
            socket.emit('runPSO', PSO_params);
        });
    // -------------------------------------------------------

    // Stop button
    // -------------------------------------------------------
    controlsDiv.append("input")
        .attr("id", "stop_button")
        .attr("type", "button")
        .attr("value", "Stop PSO")
        .on('click', function() {
            if (!THREAD_RUNNING) {
                console.log("No threads running.");
                return;
            }
            resetRunButton();
            socket.emit('stopPSO', {"stop" : true});
            THREAD_RUNNING = false;
        });

    // -------------------------------------------------------

    // Objective Function Input
    // -------------------------------------------------------
    var objective_div = controlsDiv.append("div").attr("id", "objective_div");

    objective_div.append("label").attr("class", "param_label").html("Objective Function");
    objective_div.append("input")
        .attr("class", "param_input_text")
        .attr("type", "text")
        .attr("name", "objective_function")
        .attr("value", objective_string)
        .style("width", "300px")
        .on("change", function() {
            socket.emit('updateObjective', {
                "new_objective"     : this.value,
                "lower_bound"       : bounds[0],
                "upper_bound"       : bounds[1]
            });
        });
    // -------------------------------------------------------

    // Lower bound
    // -------------------------------------------------------
    var lower_bound_div = controlsDiv.append("div").attr("id", "lower_bound_div");

    lower_bound_div.append("label").attr("class", "param_label").html("Lower Bound");
    lower_bound_div.append("input")
        .attr("class", "param_input_text")
        .attr("type", "text")
        .attr("name", "lower_bound")
        .attr("value", bounds[0])
        .style("width", "300px")
        .on("change", function() {
            socket.emit('updateObjective', {
                "new_objective"     : objective_string,
                "lower_bound"       : this.value,
                "upper_bound"       : bounds[1]
            });
        });
    // -------------------------------------------------------

    // Upper bound
    // -------------------------------------------------------
    var upper_bound_div = controlsDiv.append("div").attr("id", "upper_bound_div");

    upper_bound_div.append("label").attr("class", "param_label").html("Upper Bound");
    upper_bound_div.append("input")
        .attr("class", "param_input_text")
        .attr("type", "text")
        .attr("name", "upper_bound")
        .attr("value", bounds[1])
        .style("width", "300px")
        .on("change", function() {
            socket.emit('updateObjective', {
                "new_objective"     : objective_string,
                "lower_bound"       : bounds[0],
                "upper_bound"       : this.value
            });
        });
    // -------------------------------------------------------
}

function initializeSocket() {
    var namespace = '/pso';
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        socket.emit('get_objective_function', {data: 'I\'m connected!'});
    });

    socket.on('receive_objective_function', function(msg) {
        objective_function = msg.objective_function;
        objective_string = msg.objective_string;
        bounds = msg.bounds;
        console.log("Bounds: " + bounds);

        console.log("objective_function: " + objective_string)
        initializeControls();
        createPlot();
    });

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    // socket.on('pso_init'), function(msg) {}
    socket.on('pso_init', function(msg) {
        initializePlot(msg);
        initializeHistogram(msg);
    });

    socket.on('pso_update', function(msg) {
        updatePlot(msg);
        updateHistogram(msg);
    });

    socket.on('pso_end', function(msg) {
        endPlot(msg);
    });
}

$(function() {
    initializeSocket();
});
