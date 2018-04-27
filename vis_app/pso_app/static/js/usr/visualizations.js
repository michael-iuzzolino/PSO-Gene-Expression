
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

function createPlot() {
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

function initializePlot(msg) {
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

function updatePlot(msg) {
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

    resetRunButton();

    THREAD_RUNNING = false;
}
