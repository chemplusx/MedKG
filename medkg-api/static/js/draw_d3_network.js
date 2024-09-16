// d3_graph.js

let simulation;
let svg, g, link, node;
let zoom;
let width, height;
let isInitialized = false;

function initD3Graph() {
    svg = d3.select("#network-1 svg");
    width = +svg.attr("width") || 800;
    height = +svg.attr("height") || 600;

    console.log(`SVG dimensions: ${width}x${height}`);
    // Create a group element to hold our graph elements
    g = svg.append("g");

    zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", zoomed);

    svg.call(zoom);

    simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(d => d.id).distance(50))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(30))
        .force("x", d3.forceX(width / 2).strength(0.1))
        .force("y", d3.forceY(height / 2).strength(0.1));

    // Initialize empty selections for links and nodes
    link = g.append("g").attr("class", "links").selectAll("line");
    node = g.append("g").attr("class", "nodes").selectAll("g");

    g.append("g").attr("class", "labels");

    isInitialized = true;
    svg.append("defs").selectAll("marker")
        .data(["end"])
        .enter().append("marker")
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#999");

    console.log("D3 Graph initialized with arrow definitions");
}

function LoadGraphValues(id, name, file, type = 'empty', neighbour='') {
    neighbour = neighbour ==='' ? $('#neighbour-type').val() !== 'Any' ? $('#neighbour-type').val() : null : neighbour;
    showLoading();

    $.ajax({
        url: "nodes/graph",
        data: {
            id: id,
            name: name,
            type: type,
            neighbour: neighbour
        },
        success: function(result) {
            hideLoading();
            createGraph(result);
            updateSearchParameters(name);
        },
        error: function(xhr, status, error) {
            hideLoading();
            console.error("Error loading graph:", error);
        }
    });
}

function transformGraphData(originalData) {
    const nodeMap = new Map();

    const transformedNodes = originalData.nodes.map(node => {
        const transformedNode = {
            id: node.data.id,
            x: Math.random() * width,  // Random initial x position
            y: Math.random() * height, // Random initial y position
            data: {
                Node_Type: node.data.Node_Type,
                properties: {
                    name: node.data.display_name || node.data.label,
                    ...node.data
                }
            }
        };
        nodeMap.set(transformedNode.id, transformedNode);
        return transformedNode;
    });

    const transformedEdges = originalData.edges.filter(edge => {
        return nodeMap.has(edge.data.source) && nodeMap.has(edge.data.target);
    }).map(edge => ({
        source: edge.data.source,
        target: edge.data.target,
        type: edge.data.Edge_Type,
        properties: edge.data.properties
    }));

    return {
        nodes: transformedNodes,
        edges: transformedEdges
    };
}

function createGraph(graphData) {

    if (!isInitialized) {
        console.error("Graph not initialized. Call initD3Graph first.");
        return;
    }

    console.log("Creating graph with data:", graphData);

    const transformedData = transformGraphData(graphData);

    console.log("Transformed data:", transformedData);

    if (transformedData.nodes.length === 0) {
        console.warn("No nodes in the graph data.");
        return;
    }

    // Clear existing graph
    g.selectAll("*").remove();

    // Create links
    link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(transformedData.edges)
        .enter().append("line")
        .attr("stroke-width", 1)
        .attr("stroke", d => getEdgeColor(d.type))
        .attr("marker-end", "url(#end)")
        .on("click", edgeClicked);

    // Create nodes
    node = g.append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(transformedData.nodes)
    .enter().append("g")
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
        .on("click", nodeClicked);

    // node.append("circle")
    //     .attr("r", 5)
    //     .attr("fill", d => getNodeColor(d.data.Node_Type));

    node.append("path")
    .attr("d", d => getNodeShape(d.data.Node_Type))
    .attr("fill", d => getNodeColor(d.data.Node_Type));

    node.append("title")
        .text(d => d.data.properties.name);

    node.append("text")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .text(d => d.data.properties.name);

    // link.append("text")
    //     .attr("dx", 12)
    //     .attr("dy", "0.35em")
    //     .text(d => d.type)

    // Update and restart the simulation
    simulation.nodes(transformedData.nodes)
        .force("link", d3.forceLink(transformedData.edges).id(d => d.id))
        .on("tick", ticked)
        .on("end", simulationEnded);

    simulation.alpha(1).restart();

    console.log("Graph creation process started");

    // Add context menu
    node.on("contextmenu", showContextMenu);
}

function nodeClicked(event, d) {
    console.log("Node clicked:", d);
    
    // Reset all nodes and links
    node.attr("opacity", 1);
    link.attr("opacity", 0.3).attr("stroke", l => getEdgeColor(l.type));
    
    // Highlight connected links and nodes
    let connectedLinks = link.filter(l => l.source === d || l.target === d);
    connectedLinks.attr("opacity", 1).attr("stroke", "red");
    
    let connectedNodes = node.filter(n => 
        connectedLinks.data().some(l => l.source === n || l.target === n)
    );
    connectedNodes.attr("opacity", 1);

    // Show edge labels for connected links
    g.select(".labels").selectAll("text").remove();
    g.select(".labels")
        .selectAll("text")
        .data(connectedLinks.data())
        .join("text")
        .attr("x", l => (l.source.x + l.target.x) / 2)
        .attr("y", l => (l.source.y + l.target.y) / 2)
        .text(l => l.type)
        .attr("font-size", "10px")
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("background-color", "white");

    // Show node info
    showInfo(d.data, 'Node');
}

function edgeClicked(event, d) {
    console.log("Edge clicked:", d);
    
    // Reset all links
    link.attr("opacity", 0.3).attr("stroke", l => getEdgeColor(l.type));
    
    // Highlight clicked link
    d3.select(this).attr("opacity", 1).attr("stroke", "red");

    // Show edge info
    showInfo(d, 'Edge');
}

function beautifyObject(obj) {
	let output = '<ul>';

	for (const subKey in obj) {
		if (subKey === "embedding" || subKey === "synonyms_str") {
			continue;
		}
		if (obj.hasOwnProperty(subKey)) {
			output += '<li style="margin-top: 1rem;">';
			if (typeof obj[subKey] === 'object' && obj[subKey] !== null) {
				// Recursive call for nested objects
				output += `<strong style="display: inline-block; width: 10rem;">${subKey}:</strong> ${beautifyObject(obj[subKey])}`;
			} else {
				output += `<strong style="display: inline-block; width: 10rem;">${subKey}:</strong> ${obj[subKey]}`;
			}
			output += '</li>';
		}
	}

	output += '</ul>';
	return output;
}

function createDetailsCard(title, data) {
	let cardHtml = `
		<div class="card details-card">
			<div class="card-content">
				<span class="card-title">${title}</span>`;
	cardHtml += beautifyObject(data);
	cardHtml +=
			`</div>
		</div>
	`;

	return cardHtml;
}

function showInfo(data, type="Node") {
    // Remove existing info panel
    // d3.select("#info-panel").remove();

    // // Create and position the info panel
    // let infoPanel = svg.append("g")
    //     .attr("id", "info-panel")
    //     .attr("transform", `translate(10, ${height - 60})`);

    // infoPanel.append("rect")
    //     .attr("width", 300)
    //     .attr("height", 50)
    //     .attr("fill", "white")
    //     .attr("stroke", "black");

    // infoPanel.append("foreignObject")
    //     .attr("width", 290)
    //     .attr("height", 40)
    //     .attr("x", 5)
    //     .attr("y", 5)
    //     .append("xhtml:div")
    //     .style("font", "12px 'Helvetica Neue'")
    //     .html(html);


    var detailsContent = document.getElementById('details-content');
                        
    // Clear previous content
    detailsContent.innerHTML = '';

    // Add general info card
    var generalInfo = {
        'ID': data.properties.id,
        'Type': data.Node_Type
    };
    detailsContent.innerHTML += createDetailsCard('General Information', generalInfo);

    // Add data card
    detailsContent.innerHTML += createDetailsCard('Element Data', data.properties);

    // Scroll to details section
    document.getElementById('details-section').scrollIntoView({behavior: 'smooth'});
}

function ticked() {
    link
        .attr("x1", d => isNaN(d.source.x) ? 0 : d.source.x)
        .attr("y1", d => isNaN(d.source.y) ? 0 : d.source.y)
        .attr("x2", d => isNaN(d.target.x) ? 0 : d.target.x)
        .attr("y2", d => isNaN(d.target.y) ? 0 : d.target.y);

    node
        .attr("transform", d => `translate(${isNaN(d.x) ? 0 : d.x},${isNaN(d.y) ? 0 : d.y})`);

    g.select(".labels").selectAll("text")
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);
    // link
    //     .attr("x1", d => d.source.x)
    //     .attr("y1", d => d.source.y)
    //     .attr("x2", d => d.target.x)
    //     .attr("y2", d => d.target.y);

    // node
    //     .attr("transform", d => `translate(${d.x},${d.y})`);

    // // Keep nodes within SVG boundaries
    // node.attr("transform", function(d) {
    //     d.x = Math.max(10, Math.min(width - 10, d.x));
    //     d.y = Math.max(10, Math.min(height - 10, d.y));
    //     return `translate(${d.x},${d.y})`;
    // });
}

function addSimulationControls() {
    const controlPanel = d3.select("body").append("div")
        .attr("id", "simulation-controls")
        .style("position", "absolute")
        .style("top", "10px")
        .style("left", "10px");

    controlPanel.append("button")
        .text("Freeze")
        .on("click", freezeSimulation);

    controlPanel.append("button")
        .text("Unfreeze")
        .on("click", unfreezeSimulation);

    controlPanel.append("button")
        .text("Restart")
        .on("click", restartSimulation);
}

function freezeSimulation() {
    simulation.stop();
    node.each(d => {
        d.fx = d.x;
        d.fy = d.y;
    });
}

function unfreezeSimulation() {
    node.each(d => {
        d.fx = null;
        d.fy = null;
    });
    simulation.alpha(0.3).restart();
}

function restartSimulation() {
    node.each(d => {
        d.fx = null;
        d.fy = null;
    });
    simulation.alpha(1).restart();
}

function simulationEnded() {
    console.log("Force simulation ended");
    fitGraphToSvg();
}

function zoomed(event) {
    g.attr("transform", event.transform);
}

function zoomIn() {
    if (!isInitialized) {
        console.error("Graph not initialized. Call initD3Graph first.");
        return;
    }
    svg.transition().duration(750).call(zoom.scaleBy, 1.2);
}

function zoomOut() {
    if (!isInitialized) {
        console.error("Graph not initialized. Call initD3Graph first.");
        return;
    }
    svg.transition().duration(750).call(zoom.scaleBy, 0.8);
}

function resetZoom() {
    if (!isInitialized) {
        console.error("Graph not initialized. Call initD3Graph first.");
        return;
    }
    svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
}

function fitGraphToSvg() {
    if (!isInitialized) {
        console.error("Graph not initialized. Call initD3Graph first.");
        return;
    }

    const bounds = g.node().getBBox();
    console.log("Graph bounds:", bounds);

    if (bounds.width === 0 || bounds.height === 0) {
        console.warn("Graph still has no dimensions. Nodes may not have valid positions.");
        return;
    }

    const scale = 0.8 / Math.max(bounds.width / width, bounds.height / height);
    const translate = [
        width / 2 - scale * (bounds.x + bounds.width / 2),
        height / 2 - scale * (bounds.y + bounds.height / 2)
    ];

    svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity
            .translate(translate[0], translate[1])
            .scale(scale));

    console.log("Graph fitted to SVG");
}

function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    // d.fx = null;
    // d.fy = null;
}

function getEdgeColor(edgeType) {
    // Define colors for different edge types
    const edgeColors = {
        // Existing colors
        "IS_AN_INDICATION_FOR": "#ff0000", // Red
        "HAS_ENZYME": "#00ff00", // Green
        "INTERACTS_WITH": "#0000ff", // Blue
        "PART_OF": "#ffa500", // Orange
        "REGULATES": "#800080", // Purple

        // Additional colors
        "BINDS_TO": "#00ffff", // Cyan
        "INHIBITS": "#ff00ff", // Magenta
        "ACTIVATES": "#ffff00", // Yellow
        "EXPRESSES": "#008080", // Teal
        "METABOLIZES": "#800000", // Maroon
        "CAUSES": "#808000", // Olive
        "TREATS": "#008000", // Dark Green
        "ASSOCIATED_WITH": "#000080", // Navy
        "LOCATED_IN": "#c0c0c0", // Silver
        "BELONGS_TO": "#808080", // Gray
        "DERIVED_FROM": "#a52a2a", // Brown
        "CONVERTS_TO": "#daa520", // Goldenrod
        "REGULATES_EXPRESSION_OF": "#9932cc", // Dark Orchid
        "COEXPRESSED_WITH": "#8fbc8f", // Dark Sea Green
        "PHOSPHORYLATES": "#483d8b", // Dark Slate Blue
        "DEPHOSPHORYLATES": "#2f4f4f", // Dark Slate Gray
        "METHYLATES": "#dc143c", // Crimson
        "DEMETHYLATES": "#00ced1", // Dark Turquoise
        "ACETYLATES": "#ff1493", // Deep Pink
        "DEACETYLATES": "#1e90ff", // Dodger Blue
        "UBIQUITINATES": "#b8860b", // Dark Goldenrod
        "DEUBIQUITINATES": "#32cd32", // Lime Green
        "TRANSPORTS": "#ff8c00", // Dark Orange
        "SECRETES": "#8b008b", // Dark Magenta
        "RELEASES": "#556b2f", // Dark Olive Green
    };
    return edgeColors[edgeType] || "#999"; // Default color is gray
}

function getNodeShape(nodeType) {
    const size = 10; // Adjust this value to change the overall size of the shapes
    switch (nodeType) {
        case "Protein":
            return d3.symbol().type(d3.symbolCircle).size(size * 5)();
        case "Disease":
            return d3.symbol().type(d3.symbolSquare).size(size * 5)();
        case "Drug":
            return d3.symbol().type(d3.symbolTriangle).size(size * 5)();
        case "Gene":
            return d3.symbol().type(d3.symbolDiamond).size(size * 5)();
        case "Phenotype":
            return d3.symbol().type(d3.symbolPentagon).size(size * 5)();
        case "Pathway":
            return d3.symbol().type(d3.symbolHexagon).size(size * 5)();
        default:
            return d3.symbol().type(d3.symbolCircle).size(size * 5)();
    }
}

function getNodeColor(nodeType) {
    // Implement color logic based on node type
    const colors = {
        "Protein": "#ff7f0e",
        "Disease": "#2ca02c",
        "Phenotype": "#d62728",
        "Drug": "#9467bd",
        "Compound": "#8c564b",
        "Gene": "#e377c2",
        "Metabolite": "#7f7f7f",
        "Pathway": "#bcbd22",
        "Chromosome": "#17becf"
    };
    return colors[nodeType] || "#aaa";
}

function showContextMenu(event, d) {
    event.preventDefault();
    
    const contextMenu = d3.select("body").selectAll(".context-menu").data([1])
        .enter().append("div")
        .attr("class", "context-menu")
        .style("left", (event.pageX + 5) + "px")
        .style("top", (event.pageY - 5) + "px");

    contextMenu.selectAll("div")
        .data(["Remove Node", "Expand", "Show Details"])
        .enter().append("div")
        .attr("class", "context-menu-item")
        .text(d => d)
        .on("click", (event, action) => {
            switch(action) {
                case "Remove Node":
                    removeNode(d);
                    break;
                case "Expand":
                    expandForNodeId(d.id, d.data.properties.name, d.data.Node_Type);
                    break;
                case "Show Details":
                    showDetails(d);
                    break;
            }
            contextMenu.remove();
        });

    d3.select("body").on("click.context-menu", () => {
        contextMenu.remove();
    });
}

function removeNode(d) {
    // Implement node removal logic
}

function expandForNodeId(id, name, nodeType) {
    // Implement node expansion logic
}

function beautifyObject(obj) {
	let output = '<ul>';

	for (const subKey in obj) {
		if (subKey === "embedding" || subKey === "synonyms_str") {
			continue;
		}
		if (obj.hasOwnProperty(subKey)) {
			output += '<li style="margin-top: 1rem;">';
			if (typeof obj[subKey] === 'object' && obj[subKey] !== null) {
				// Recursive call for nested objects
				output += `<strong style="display: inline-block; width: 10rem;">${subKey}:</strong> ${beautifyObject(obj[subKey])}`;
			} else {
				output += `<strong style="display: inline-block; width: 10rem;">${subKey}:</strong> ${obj[subKey]}`;
			}
			output += '</li>';
		}
	}

	output += '</ul>';
	return output;
}

function updateSearchParameters(name) {
    $('#search_parameters').append(`<li class="list-group-item"><b>Query Terms:</b><br>${name}</li>`);
}

function showLoading() {
    // Implement loading indicator
}

function hideLoading() {
    // Hide loading indicator
}

// Export functions for use in other scripts
window.initD3Graph = initD3Graph;
window.createGraph = createGraph;
window.LoadGraphValues = LoadGraphValues;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.resetZoom = resetZoom;
window.fitGraphToSvg = fitGraphToSvg;