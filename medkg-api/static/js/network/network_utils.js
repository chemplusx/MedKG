// Constants for styling
// Context menu options
const CONTEXT_MENU_ITEMS = [
    { text: "Expand Node", icon: "add_circle_outline", action: "expand" },
    { text: "Hide Node", icon: "visibility_off", action: "hide" },
    { text: "Focus on this Node", icon: "center_focus_strong", action: "focus" },
    { text: "Find Path", icon: "timeline", action: "path" },
    { text: "View in New Graph", icon: "open_in_new", action: "newGraph" }
];

const STYLES = {
    colors: {
        primary: '#2c3e50',
        secondary: '#3498db',
        accent: '#e74c3c',
        background: '#f8f9fa',
        nodeTypes: {
            Drug: '#ff7675',
            Protein: '#4834d4',
            Disease: '#6c5ce7',
            Gene: '#00b894',
            Metabolite: '#e17055',
            Pathway: '#fdcb6e',
            Default: '#95a5a6'
        }
    },
    nodes: {
        minRadius: 8,
        maxRadius: 20,
        labelOffset: 8,
        highlightStrokeWidth: 3
    }
};


function initD3Graph() {
    // SVG Setup
    const svg = d3.select("#network-container svg");
    const width = svg.node().getBoundingClientRect().width;
    const height = svg.node().getBoundingClientRect().height;

    // Define arrow markers for different relationship types
    const defs = svg.append("defs");

    const markers = [
        { id: "arrow-inhibits", color: STYLES.colors.accent },
        { id: "arrow-activates", color: STYLES.colors.secondary },
        { id: "arrow-interacts", color: STYLES.colors.primary }
    ];

    markers.forEach(marker => {
        defs.append("marker")
            .attr("id", marker.id)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("fill", marker.color)
            .attr("d", "M0,-5L10,0L0,5");
    });

    // Create container with zoom behavior
    const container = svg.append("g");
    const zoom = d3.zoom()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => {
            container.attr("transform", event.transform);
            // Update label visibility based on zoom level
            updateLabels(event.transform.k);
        });

    svg.call(zoom);

    // Force simulation setup with improved parameters
    const simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(d => d.id)
            .distance(100)
            .strength(0.5))
        .force("charge", d3.forceManyBody()
            .strength(-500)
            .distanceMax(300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(50))
        .alphaDecay(0.01); // Slower decay for better layout

    function updateGraph(data) {
        // Clear existing elements
        container.selectAll("*").remove();

        // Create link group with multiple line types
        const links = container.append("g")
            .attr("class", "links")
            .selectAll("g")
            .data(data.links)
            .join("g");

        // Main link line
        links.append("line")
            .attr("class", "link-line")
            .attr("stroke", "#999")
            .attr("stroke-width", 1.5)
            .attr("stroke-opacity", 0.6)
            .attr("marker-end", d => `url(#arrow-${d.type || 'interacts'})`);

        // Link labels
        const linkLabels = links.append("text")
            .attr("class", "link-label")
            .attr("dy", -2)
            .text(d => {
                // Shorten long relationship names
                const type = d.type || "";
                // if (type.includes("IS_A_CONTRAINDICATION_FOR")) {
                //     return "contraindication";
                // }
                // Add more mappings as needed
                return type;
            })
            .attr("fill", "#666")
            .attr("font-size", "6px") // Even smaller font
            .style("pointer-events", "none")
            .style("opacity", 0.7); // Make labels slightly transparent

        // Add textPath for edge labels
        linkLabels.append("textPath")
            .attr("xlink:href", (d, i) => `#linkPath${i}`)
            .attr("startOffset", "50%")
            .style("text-anchor", "middle");

        // Create paths for edge labels
        links.append("path")
            .attr("id", (d, i) => `linkPath${i}`)
            .attr("class", "link-path")
            .style("fill", "none")
            .style("stroke", "none");

        // Create nodes with custom shapes
        const nodes = container.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .attr("class", "node")
            .call(drag(simulation));

        // Node shapes
        nodes.append("path")
            .attr("d", d => getNodeShape(d.type))
            .attr("fill", d => STYLES.colors.nodeTypes[d.type] || STYLES.colors.nodeTypes.Default)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);

        // Node labels
        const labels = nodes.append("text")
            .attr("class", "node-label")
            .attr("dy", d => getNodeLabelOffset(d.type))
            .attr("text-anchor", "middle")
            .text(d => d.name)
            .attr("fill", "#333")
            .attr("font-size", "10px")
            .style("pointer-events", "none");

        // Hover interactions
        nodes
            .on("mouseover", handleNodeHover)
            .on("mouseout", handleNodeUnhover)
            .on("click", handleNodeClick);

        // Then update the event bindings like this:
        nodes.on("contextmenu", (event, d) => {
            event.preventDefault();
            handleContextMenu(event, d);
        });

        nodes.on("click", (event, d) => {
            event.preventDefault();
            showNodeModal(d);  // This was previously updateDetails(d)
        });

        // Update simulation
        simulation
            .nodes(data.nodes)
            .on("tick", () => {
                // Update link lines
                links.selectAll("line")
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                // Update link paths for labels
                links.selectAll(".link-path")
                    .attr("d", d => {
                        const dx = d.target.x - d.source.x;
                        const dy = d.target.y - d.source.y;
                        const dr = Math.sqrt(dx * dx + dy * dy);
                        return `M ${d.source.x} ${d.source.y} A ${dr} ${dr} 0 0 1 ${d.target.x} ${d.target.y}`;
                    });

                links.selectAll("text")
                    .attr("x", d => (d.source.x + d.target.x) / 2)
                    .attr("y", d => (d.source.y + d.target.y) / 2);

                nodes.attr("transform", d => `translate(${d.x},${d.y})`);
            });

        simulation.force("link").links(data.links);
        simulation.alpha(1).restart();

        updateNetworkDetails(data);
    }

    // Helper functions
    function getNodeShape(type) {
        const size = 150;
        switch (type) {
            case 'Drug':
                return d3.symbol().type(d3.symbolCircle).size(size)();
            case 'Protein':
                return d3.symbol().type(d3.symbolDiamond).size(size)();
            case 'Disease':
                return d3.symbol().type(d3.symbolTriangle).size(size)();
            case 'Gene':
                return d3.symbol().type(d3.symbolSquare).size(size)();
            default:
                return d3.symbol().type(d3.symbolCircle).size(size)();
        }
    }

    function getNodeLabelOffset(type) {
        return type === 'Disease' ? 25 : 20;
    }

    function handleNodeHover(event, d) {
        const node = d3.select(this);
        node.select("path")
            .transition()
            .duration(200)
            .attr("stroke", "#000")
            .attr("stroke-width", STYLES.nodes.highlightStrokeWidth);

        // Highlight connected nodes and links
        const linkedNodes = new Set();
        container.selectAll(".link-line")
            .filter(link => {
                if (link.source === d || link.target === d) {
                    linkedNodes.add(link.source);
                    linkedNodes.add(link.target);
                    return true;
                }
                return false;
            })
            .transition()
            .duration(200)
            .attr("stroke", STYLES.colors.secondary)
            .attr("stroke-width", 2)
            .attr("stroke-opacity", 1);

        container.selectAll(".node")
            .transition()
            .duration(200)
            .style("opacity", n => linkedNodes.has(n) ? 1 : 0.2);
    }

    function handleNodeUnhover() {
        container.selectAll(".node")
            .transition()
            .duration(200)
            .style("opacity", 1)
            .select("path")
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);

        container.selectAll(".link-line")
            .transition()
            .duration(200)
            .attr("stroke", "#999")
            .attr("stroke-width", 1.5)
            .attr("stroke-opacity", 0.6);
    }

    function handleNodeClick(event, d) {
        event.preventDefault();
        showNodeModal(d);
    }


    // Update the context menu action handler
    function handleContextMenuAction(action, nodeId) {
        console.log(`Action: ${action}, Node: ${nodeId}`);
        switch (action) {
            case 'expand':
                expandNode(nodeId);
                break;
            case 'hide':
                hideNode(nodeId);
                break;
            case 'focus':
                focusOnNode(nodeId);
                break;
            case 'path':
                showPathFindingModal(nodeId);
                break;
            case 'newGraph':
                openInNewGraph(nodeId);
                break;
        }
    }

    // Update the context menu handling function
    function handleContextMenu(event, d) {
        event.preventDefault();
        event.stopPropagation();
    
        // Remove any existing context menus
        document.querySelectorAll('.context-menu').forEach(menu => menu.remove());
    
        const contextMenu = document.createElement('div');
        contextMenu.className = 'context-menu';
        
        // Create menu structure
        const menuItems = [
            { action: 'expand', icon: 'add_circle_outline', text: 'Expand Node' },
            { action: 'hide', icon: 'visibility_off', text: 'Hide Node' },
            { action: 'focus', icon: 'center_focus_strong', text: 'Focus on Node' },
            { action: 'path', icon: 'timeline', text: 'Find Path' },
            { action: 'newGraph', icon: 'open_in_new', text: 'View in New Graph' }
        ];
    
        const ul = document.createElement('ul');
        ul.className = 'menu-items';
    
        menuItems.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <i class="material-icons">${item.icon}</i>
                <span>${item.text}</span>
            `;
            
            // Add event listener directly to the element
            li.addEventListener('click', () => {
                handleContextMenuAction(item.action, d.id);
                contextMenu.remove(); // Close menu after action
            });
            
            ul.appendChild(li);
        });
    
        contextMenu.appendChild(ul);
    
        // Position the menu
        contextMenu.style.left = `${event.pageX}px`;
        contextMenu.style.top = `${event.pageY}px`;
        document.body.appendChild(contextMenu);
    
        // Add click outside listener
        setTimeout(() => {
            window.addEventListener('click', function closeMenu(e) {
                if (!contextMenu.contains(e.target)) {
                    contextMenu.remove();
                    window.removeEventListener('click', closeMenu);
                }
            });
        }, 0);
    
        // Close menu if another one is opened
        window.addEventListener('contextmenu', () => {
            contextMenu.remove();
        });
    }

    

    // Example implementation of the actions
    function expandNode(nodeId) {
        console.log('Expanding node:', nodeId);
        // Add your expand implementation

        // fetch and add more data to the graph
        expandNodeForId(nodeId);

    }

    function expandNodeForId(nodeId) {
        // Fetch more data for the given node
        // First get more details for the nodeid from the globalNetworkValues
        const node = globalNetworkValues["nodes"].find(n => n.id === nodeId);
        if (!node) return;

        //copy the globalNetworkValues
        const globalNetworkValuesCopy = globalNetworkValues;

        const selectedEntityTypes = Array.from(document.querySelectorAll('#labelFilterSection input[type="checkbox"]'))
        .filter(cb => cb.checked)
        .map(cb => cb.value);

        // Get selected relationship types
        const selectedRelationTypes = Array.from(document.querySelectorAll('#relationFilterSection input[type="checkbox"]'))
            .filter(cb => cb.checked)
            .map(cb => cb.value);


        fetch(`nodes/graph`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: nodeId,
                name: node.name,
                type: node.type,
                neighbour: selectedEntityTypes.join(","), limit:10 })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch node data');
                }
                return response.json();
            })
            .then(data => {
                // now append the data to the globalNetworkValues, 
                globalNetworkValuesCopy.nodes = globalNetworkValuesCopy.nodes.concat(data.nodes);
                globalNetworkValuesCopy.links = globalNetworkValuesCopy.links.concat(data.links); 

                // remove duplicate nodes and relationshipts
                globalNetworkValuesCopy.nodes = globalNetworkValuesCopy.nodes.filter((node, index, self) =>
                    index === self.findIndex((t) => (
                        t.id === node.id
                    ))
                );

                globalNetworkValuesCopy.links = globalNetworkValuesCopy.links.filter((link, index, self) =>
                    index === self.findIndex((t) => (
                        t.id === link.id
                    ))
                );

                // Filter nodes based on selected entity types
                const filteredNodes = globalNetworkValuesCopy.nodes.filter(node =>
                    selectedEntityTypes.includes(node.type)
                );

                // Get the IDs of filtered nodes for link filtering
                const filteredNodeIds = new Set(filteredNodes.map(node => node.id));

                // Filter links based on selected relationship types and filtered nodes
                const filteredLinks = globalNetworkValuesCopy.links.filter(link => {
                    const sourceExists = filteredNodeIds.has(link.source.id || link.source);
                    const targetExists = filteredNodeIds.has(link.target.id || link.target);
                    const relationshipMatch = selectedRelationTypes.includes(link.type);

                    return sourceExists && targetExists && relationshipMatch;
                });

                // Update the graph with filtered data
                graph.updateGraph({
                    nodes: [], links: []}); // Clear the graph first
                graph.updateGraph({
                    nodes: filteredNodes,
                    links: filteredLinks
                });
                    //replace the globalNetworkValues with the updated one
                globalNetworkValues = globalNetworkValuesCopy;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }


    function hideNode(nodeId) {
        // Get the node and its connected links
        const node = d3.select(`g.node`).filter(d => d.id === nodeId);
        const connectedLinks = d3.selectAll('line').filter(d =>
            d.source.id === nodeId || d.target.id === nodeId
        );

        // Fade out and remove
        node.transition()
            .duration(300)
            .style('opacity', 0)
            .remove();

        connectedLinks.transition()
            .duration(300)
            .style('opacity', 0)
            .remove();

        // Update the simulation
        simulation.nodes(simulation.nodes().filter(n => n.id !== nodeId));
        simulation.force("link").links(
            simulation.force("link").links().filter(l =>
                l.source.id !== nodeId && l.target.id !== nodeId
            )
        );
        simulation.alpha(0.1).restart();
    }

    function focusOnNode(nodeId) {
        // Get the node
        const node = simulation.nodes().find(n => n.id === nodeId);
        if (!node) return;

        // Calculate the transform to center on this node
        const svgElement = d3.select('#network-container svg');
        const width = svgElement.node().getBoundingClientRect().width;
        const height = svgElement.node().getBoundingClientRect().height;

        const transform = d3.zoomIdentity
            .translate(width / 2 - node.x, height / 2 - node.y)
            .scale(2);  // Zoom in by a factor of 2

        // Apply the transform with transition
        svgElement.transition()
            .duration(750)
            .call(zoom.transform, transform);

        // Highlight the focused node and its immediate connections
        d3.selectAll('g.node')
            .transition()
            .duration(300)
            .style('opacity', d => {
                const isConnected = simulation.force("link").links()
                    .some(l => (l.source.id === nodeId && l.target.id === d.id) ||
                        (l.target.id === nodeId && l.source.id === d.id));
                return d.id === nodeId || isConnected ? 1 : 0.1;
            });
    }

    // function findPath(nodeId) {
    //     const targetType = document.getElementById('targetNodeType').value;
    //     const maxDepth = parseInt(document.getElementById('maxDepth').value);

    //     // Log the search parameters for now
    //     console.log('Finding path:', {
    //         sourceNodeId,
    //         targetType,
    //         maxDepth
    //     });
    // }

    function showPathFindingModal(sourceNodeId) {
        const sourceNode = simulation.nodes().find(n => n.id === sourceNodeId);
        if (!sourceNode) return;
    
        const modalContent = `
            <div class="modal-content">
                <h4>Find Path</h4>
                <div class="row">
                    <div class="input-field1 col s12">
                        <input type="text" id="sourceNode" value="${sourceNode.name}" disabled>
                        <label for="sourceNode" class="active">Source Node</label>
                    </div>
                    <div class="input-field1 col s12">
                        <select id="targetNodeType">
                            <option value="" disabled selected>Choose target type</option>
                            <option value="Drug">Drug</option>
                            <option value="Disease">Disease</option>
                            <option value="Protein">Protein</option>
                            <option value="Gene">Gene</option>
                            <option value="Metabolite">Metabolite</option>
                            <option value="Pathway">Pathway</option>
                        </select>
                        <label>Target Node Type</label>
                    </div>
                    <div class="input-field col s12">
                        <input type="number" id="maxDepth" min="1" max="5" value="3">
                        <label for="maxDepth">Maximum Path Depth</label>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="modal-close waves-effect waves-light btn-flat">Cancel</button>
                <button class="waves-effect waves-light btn" id="findPathButton">
                    Find Path
                </button>
            </div>
        `;
    
        const modalElement = document.createElement('div');
        modalElement.className = 'modal';
        modalElement.innerHTML = modalContent;
        document.body.appendChild(modalElement);
    
        const modal = M.Modal.init(modalElement, {
            onOpenEnd: () => {
                // Initialize the select dropdown
                const selects = modalElement.querySelectorAll('select');
                M.FormSelect.init(selects);
                
                // Add click handler for the Find Path button
                document.getElementById('findPathButton').addEventListener('click', () => {
                    findPath(sourceNodeId);
                    modal.close();
                });
            },
            onCloseEnd: () => modalElement.remove(),
            dismissible: true
        });
    
        modal.open();
    }


    function openInNewGraph(nodeId) {
        // Get the node data
        const node = simulation.nodes().find(n => n.id === nodeId);
        if (!node) return;

        // Open in new window/tab with parameters
        const params = new URLSearchParams({
            id: nodeId,
            name: node.name,
            type: node.type
        });
        window.open(`visualise?${params.toString()}`, '_blank');
    }

    function showNodeModal(node) {
        const modalContent = `
            <div class="modal-content">
                <div class="modal-header">
                    <h4>${node.name}</h4>
                    <i class="material-icons modal-close" style="cursor: pointer; position: absolute; right: 10px; top: 10px;">close</i>
                </div>
                <div class="entity-type ${node.type.toLowerCase()}">${node.type}</div>
                <div class="modal-body">
                    <p><strong>ID:</strong> ${node.id}</p>
                    <p><strong>Type:</strong> ${node.type}</p>
                    ${node.description ? `<p><strong>Description:</strong> ${node.description}</p>` : ''}
                    
                    <div class="relationships-section">
                        <h5>Relationships</h5>
                        <div id="nodeRelationships">
                            Loading relationships...
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-flat waves-effect waves-light modal-close">Close</button>
                    <button class="waves-effect waves-light btn" onclick="expandNode('${node.id}')">
                        Expand Node
                    </button>
                </div>
            </div>
        `;

        const modalElement = document.createElement('div');
        modalElement.className = 'modal';
        modalElement.innerHTML = modalContent;
        document.body.appendChild(modalElement);

        // Initialize modal with specific options
        const modal = M.Modal.init(modalElement, {
            onOpenEnd: () => loadNodeRelationships(node.id),
            onCloseEnd: () => {
                modalElement.remove();
                // Clean up any event listeners if needed
            },
            dismissible: true // Allows clicking outside to close
        });

        modal.open();
    }

    function loadNodeRelationships(nodeId) {
        // Fetch relationships for the given node
        // fetch from globalNetworkValues
        const relationships = globalNetworkValues["links"]
            .filter(link => link.source.id === nodeId || link.target.id === nodeId)
            .map(link => {
                const source = link.source.id === nodeId ? link.target : link.source;
                return {
                    id: source.id,
                    name: source.name,
                    type: link.type
                };
            });

        const relationshipsList = document.getElementById('nodeRelationships');
        relationshipsList.innerHTML = relationships.map(rel => `
            <div class="relationship-item">
                <span class="relationship-type">${rel.type}</span>
                <span class="relationship-name">${rel.name}</span>
            </div>
        `).join('');
    }
    function updateDetailsPanel(nodeData) {
        const panel = document.getElementById('details-content');
        panel.innerHTML = `
            <div class="entity-details">
                <span class="entity-type ${nodeData.type.toLowerCase()}">${nodeData.type}</span>
                <h6>${nodeData.name}</h6>
                <p>${nodeData.description || 'No description available'}</p>
                <div class="relationships">
                    <h6>Related Entities</h6>
                    ${getRelatedEntitiesHTML(nodeData)}
                </div>
            </div>
        `;
    }

    function getRelatedEntitiesHTML(nodeData) {
        // Implementation depends on your data structure
        return '<p>Relationship details would be shown here</p>';
    }

    function updateLabels(zoomLevel) {
        container.selectAll(".node-label")
            .style("display", zoomLevel > 0.6 ? "block" : "none")
            .style("font-size", `${Math.min(12 * zoomLevel, 16)}px`);

        container.selectAll(".link-label")
            .style("display", zoomLevel > 0.8 ? "block" : "none")
            .style("font-size", `${Math.min(10 * zoomLevel, 14)}px`);
    }

    // Drag behavior
    function drag(simulation) {
        return d3.drag()
            .on("start", (event) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            })
            .on("drag", (event) => {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            })
            .on("end", (event) => {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            });
    }

    // Return the update function and zoom controls
    return {
        updateGraph,
        zoomIn: () => svg.transition().duration(500).call(zoom.scaleBy, 1.5),
        zoomOut: () => svg.transition().duration(500).call(zoom.scaleBy, 0.75),
        resetZoom: () => svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity),
        fitToView: () => {
            const bounds = container.node().getBBox();
            const dx = bounds.width;
            const dy = bounds.height;
            const x = bounds.x + dx / 2;
            const y = bounds.y + dy / 2;
            const scale = 0.9 / Math.max(dx / width, dy / height);
            const translate = [width / 2 - scale * x, height / 2 - scale * y];

            svg.transition()
                .duration(500)
                .call(zoom.transform, d3.zoomIdentity
                    .translate(translate[0], translate[1])
                    .scale(scale));
        }
    };
}

function findPath(sourceNodeId) {
    const targetType = document.getElementById('targetNodeType').value;
    const maxDepth = parseInt(document.getElementById('maxDepth').value);
    
    console.log('Finding path:', {
        sourceNodeId,
        targetType,
        maxDepth
    });
    
    fetch('api/path-search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            startNode: sourceNodeId,
            targetType: targetType,
            maxHops: `${maxDepth}`,
            endNode: ""
        })
    }).then(response => {
        if (!response.ok) {
            throw new Error('Failed to find path');
        }
        return response.json();
    }).then(data => {
        console.log('Path found:', data);
        // Handle path data
        // returned values will be an array of each path
        // each path will be an array of nodes and relationships
        // {
        //     "paths": [
        //         {
        //             "length": 2,
        //             "nodes": [
        //                 {}
        //             ],
        //             "relationships": [
        //                 {}
        //             ]
        //         }
        //     ]
        // }
        // update the same in the graph

        paths = data.paths;
        nodes = [];
        links = [];
        //iterate through each path and update the graph
        graph.updateGraph({
            nodes: [],
            links: []
        });
        paths.forEach(path => {
            nodes.push(...path.nodes);
            links.push(...path.relationships);
            
            
        });
        

        // remove duplicate nodes and relationshipts
        nodes = nodes.filter((node, index, self) =>
            index === self.findIndex((t) => (
                t.id === node.id
            ))
        );

        links = links.filter((link, index, self) =>
            index === self.findIndex((t) => (
                t.id === link.id
            ))
        );

        graph.updateGraph({
            nodes: nodes,
            links: links
        });



        // update the graph with the path
        // updateGraphWithPaths(paths);

    }).catch(error => {
        console.error('Error:', error);
    });

    // TODO: Implement path finding logic
};


function fetchNetworkData(entityId, name, neighbours, type, depth) {
    // In a real implementation, this would fetch the data from your backend
    return fetch('nodes/graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: entityId,
            name: name,
            type: type,
            neighbour: neighbours
        }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch graph data');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}