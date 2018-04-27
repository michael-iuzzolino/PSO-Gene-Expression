"use strict";
var socket;

var histogram;
var xScale, yScale;
var xHistScale, yHistScale;
var svg_width = 300;
var svg_height = 300;
var height, width;
var histogramHeight, histogramWidth;
var objective_function, bounds;
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
    createPlot_1D();
}

function createPlot_1D() {
    d3.select("#pso_svg").remove();

    var margin = {top: 50, right: 50, bottom: 50, left: 50};
    width = svg_width - margin.left - margin.right;
    height = svg_height - margin.top - margin.bottom;

    xScale = d3.scaleLinear()
        .range([0, width]);

    yScale = d3.scaleLinear()
        .range([height, 0]);

    var xAxis = d3.axisBottom(xScale);
    var yAxis = d3.axisLeft(yScale);

    var pso_svg = d3.select("#vis_div").append("svg")
        .attr("id", "pso_svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)

    var pso_g = pso_svg.append("g")
        .attr("id", "pso_g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var objective_g = pso_g.append("g").attr("id", "objective_g");

    xScale.domain(d3.extent(objective_function, function(d) { return d.x; })).nice();
    yScale.domain([0, d3.max(objective_function, function(d) { return d.y; })]).nice();

    // define the line
    var valueline = d3.line()
        .x(function(d) { return xScale(d.x); })
        .y(function(d) { return yScale(d.y); });

    // Add the valueline path.
    objective_g.append("path")
        .data([objective_function])
        .attr("class", "line")
        .attr("id", "objective_path")
        .attr("d", valueline);

    // X axis Label
    // --------------------------------------------------------
    objective_g.append("g")
        .attr("class", "x_axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
            .attr("class", "axis_label")
            .attr("x", width)
            .attr("y", -6)
            .style("text-anchor", "end")
            .text("X position");
    // --------------------------------------------------------

    // Y axis label
    // --------------------------------------------------------
    objective_g.append("g")
        .attr("class", "y_axis")
        .call(yAxis)
        .append("text")
            .attr("class", "axis_label")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Y Value")
    // --------------------------------------------------------
}


function initializeHistogram(msg) {

    d3.select("#histogram_svg").remove();

    var data = msg.history;
    var timestep = msg.time_i;

    // set the dimensions and margins of the graph
    var margin = {top: 50, right: 50, bottom: 50, left: 50};
    histogramWidth = svg_width - margin.left - margin.right;
    histogramHeight = 200 - margin.top - margin.bottom;

    xHistScale = d3.scaleLinear()
        .range([0, histogramWidth]);

    yHistScale = d3.scaleLinear()
        .range([histogramHeight, 0]);

    xHistScale.domain(d3.extent(objective_function, function(d) { return d.x; })).nice();

    // set the parameters for the histogram
    histogram = d3.histogram()
        .value(function(d) { return d.position[0]; })
        .domain(xHistScale.domain())
        .thresholds(xHistScale.ticks(num_histogram_bins));

    // append the svg object to the body of the page
    // append a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select("#histo_div").append("svg")
        .attr("id", "histogram_svg")
        .attr("width", histogramWidth + margin.left + margin.right)
        .attr("height", histogramHeight + margin.top + margin.bottom)
      .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");


    // group the data for the bars
    var bins = histogram(data);

    // Scale the range of the data in the y domain
    yHistScale.domain([0, d3.max(bins, function(d) { return d.length; })]);

    // append the bar rectangles to the svg element
    svg.selectAll("rect.histo_bar")
        .data(bins)
        .enter().append("rect")
        .attr("class", "histo_bar")
        .attr("x", 1)
        .attr("transform", function(d) {
            return "translate(" + xHistScale(d.x0) + "," + yHistScale(d.length) + ")";
        })
        .attr("width", function(d) { return xHistScale(d.x1) - xHistScale(d.x0) - 1 ; })
        .attr("height", function(d) { return histogramHeight - yHistScale(d.length); });

    // add the x Axis
    svg.append("g")
        .attr("transform", "translate(0," + histogramHeight + ")")
        .call(d3.axisBottom(xHistScale));

    // add the y Axis
    svg.append("g")
        .call(d3.axisLeft(yHistScale).ticks(5));
}

function updateHistogram(msg) {
    var data = msg.history;
    var timestep = msg.time_i;

    // group the data for the bars
    var bins = histogram(data);

    // Scale the range of the data in the y domain
    yHistScale.domain([0, d3.max(bins, function(d) { return d.length; })]);

    d3.selectAll(".histo_bar")
        .data(bins).transition().duration(500)
        .attr("transform", function(d) {
            return "translate(" + xHistScale(d.x0) + "," + yHistScale(d.length) + ")";
        })
        .attr("width", function(d) { return xHistScale(d.x1) - xHistScale(d.x0) - 1 ; })
        .attr("height", function(d) { return histogramHeight - yHistScale(d.length); });

}

function initializePlot_1D(msg) {
    var data = msg.history;
    var timestep = msg.time_i;

    d3.selectAll("#vis_g").remove();

    var vis_g = d3.select("#pso_g").append("g").attr("id", "vis_g");

    // Timestep Label
    // --------------------------------------------------------
    vis_g.append("g")
        .attr("id", "text_g")
        .attr("transform", "translate(0," + (height*1.2) + ")")
        .append("text")
        .attr("id", "timestep_label")
        .attr("class", "label")
        .attr("x", width/2.)
        .attr("y", -6)
        .style("text-anchor", "end")
        .text("Timestep: " + timestep);
    // --------------------------------------------------------

    // Agent dots
    // --------------------------------------------------------
    vis_g.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "agent")
        .attr("id", function(d) {
            return "agent_" + d.agent;
        })
        .attr("r", 3.5)
        .attr("cx", function(d) {
            return xScale(d.position[0]);
        })
        .attr("cy", function(d) {
            return yScale(d.position[1]);
        })
        .style("fill", "blue");
    // --------------------------------------------------------
}

function updatePlot_1D(msg) {
    var data = msg.history;
    var timestep = msg.time_i;

    data.forEach(function(d) {
        d3.select("#agent_"+d.agent)
            .transition().duration(1000).delay(200)
            .attr("cx", function() { return xScale(d.position[0]); })
            .attr("cy", function() { return yScale(d.position[1]); })

    });

    d3.select("#timestep_label")
        .text("Timestep: " + timestep);
}


function endPlot_1D(msg) {
    var data = msg.history;
    var timestep = msg.time_i;

    var pso_svg = d3.select("#pso_svg");

    xScale.domain(d3.extent(data, function(d) { return d.position[0]; })).nice();
    yScale.domain(d3.extent(data, function(d) { return d.position[1]; })).nice();

    updateAxis(pso_svg);

    pso_svg.selectAll(".dot")
        .data(data).transition(transition)
        .attr("cx", function(d) { return xScale(d.position[0]); })
        .attr("cy", function(d) { return yScale(d.position[1]); })
        .style("fill", "red");

    d3.select("#timestep_label")
        .text("Timestep: " + timestep);

    resetRunButton();

    THREAD_RUNNING = false;
}


function resetRunButton() {
    d3.select("#run_button").attr("value", "Finished");
    setTimeout(function() {
        d3.select("#run_button").attr("value", "Run PSO");
    }, 2000);
}


function initializePlot_2D(msg) {

    var data = msg.history;
    var timestep = msg.time_i;
    d3.select("#pso_svg").remove();

    var margin = {top: 50, right: 50, bottom: 50, left: 50};
    var width = svg_width - margin.left - margin.right;
    var height = svg_height - margin.top - margin.bottom;

    xScale = d3.scaleLinear()
        .range([0, width]);

    yScale = d3.scaleLinear()
        .range([height, 0]);

    var xAxis = d3.axisBottom(xScale);
    var yAxis = d3.axisLeft(yScale);

    var pso_g = d3.select("#vis_div").append("svg")
        .attr("id", "pso_svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    xScale.domain(d3.extent(data, function(d) { return d.position[0]; })).nice();
    yScale.domain(d3.extent(data, function(d) { return d.position[1]; })).nice();

    // Timestep Label
    // --------------------------------------------------------
    pso_g.append("g")
        .attr("id", "text_g")
        .attr("transform", "translate(0," + (height*1.2) + ")")
        .append("text")
        .attr("id", "timestep_label")
        .attr("class", "label")
        .attr("x", width/2.)
        .attr("y", -6)
        .style("text-anchor", "end")
        .text("Timestep: " + timestep);
    // --------------------------------------------------------

    // X axis Label
    // --------------------------------------------------------
    pso_g.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("class", "label")
        .attr("x", width)
        .attr("y", -6)
        .style("text-anchor", "end")
        .text("X position");
    // --------------------------------------------------------

    // Y axis label
    // --------------------------------------------------------
    pso_g.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Y position")
    // --------------------------------------------------------

    // Agent dots
    // --------------------------------------------------------
    pso_g.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr("cx", function(d) {
            return xScale(d.position[0]);
        })
        .attr("cy", function(d) { return yScale(d.position[1]); })
        .style("fill", "blue");
    // --------------------------------------------------------
}

function updateAxis(svg) {
    var xAxis = d3.axisBottom(xScale);
    var yAxis = d3.axisLeft(yScale);

    svg.select(".x")
        .transition(transition)
        .call(xAxis)

    svg.select(".y")
        .transition(transition)
        .call(yAxis)
}

function updatePlot(msg) {
    var data = msg.history;
    var timestep = msg.time_i;

    var pso_svg = d3.select("#pso_svg");

    xScale.domain(d3.extent(data, function(d) { return d.position[0]; })).nice();
    yScale.domain(d3.extent(data, function(d) { return d.position[1]; })).nice();

    updateAxis(pso_svg);

    pso_svg.selectAll(".dot")
        .data(data).transition(transition)
        .attr("cx", function(d) { return xScale(d.position[0]); })
        .attr("cy", function(d) { return yScale(d.position[1]); });

    d3.select("#timestep_label")
        .text("Timestep: " + timestep);
}

function endPlot(msg) {
    var data = msg.history;
    var timestep = msg.time_i;

    var pso_svg = d3.select("#pso_svg");

    xScale.domain(d3.extent(data, function(d) { return d.position[0]; })).nice();
    yScale.domain(d3.extent(data, function(d) { return d.position[1]; })).nice();

    updateAxis(pso_svg);

    pso_svg.selectAll(".dot")
        .data(data).transition(transition)
        .attr("cx", function(d) { return xScale(d.position[0]); })
        .attr("cy", function(d) { return yScale(d.position[1]); })
        .style("fill", "red");

    d3.select("#timestep_label")
        .text("Timestep: " + timestep);


    d3.select("#run_button").attr("value", "Finished");
    setTimeout(function() {
        d3.select("#run_button").attr("value", "Run PSO");
    }, 2000);
}


function initializeControls() {
    var controlsDiv = d3.select("#controls_div");
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
    param_div.append("input")
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
    param_div.append("input")
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
}

function initializeSocket() {
    var namespace = '/pso';
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        socket.emit('get_objective_function', {data: 'I\'m connected!'});
    });

    socket.on('receive_objective_function', function(msg) {
        objective_function = msg.objective_function;
        bounds = msg.bounds;
        createPlot_1D();
    });

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    // socket.on('pso_init'), function(msg) {}
    socket.on('pso_init', function(msg) {
        initializePlot_1D(msg);
        initializeHistogram(msg);
    });

    socket.on('pso_update', function(msg) {
        updatePlot_1D(msg);
        updateHistogram(msg);
    });

    socket.on('pso_end', function(msg) {
        endPlot_1D(msg);
    });
}

$(function() {
    initializeControls();
    initializeSocket();
});
