// Constants for styling
// Context menu options
const CONTEXT_MENU_ITEMS = [
    { text: "Expand Node", icon: "add_circle_outline", action: "expand" },
    { text: "Hide Node", icon: "visibility_off", action: "hide" },
    { text: "Focus on this Node", icon: "center_focus_strong", action: "focus" },
    { text: "Explore Connections", icon: "timeline", action: "path" },
    { text: "View in New Graph", icon: "open_in_new", action: "newGraph" }
];


const style = document.createElement('style');
style.textContent = `
    .context-menu {
        position: fixed;
        background: white;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        padding: 4px 0;
        min-width: 150px;
        z-index: 1000;
    }

    .menu-items {
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .menu-item {
        padding: 8px 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        position: relative;
    }

    .menu-item:hover {
        background: #f0f0f0;
    }

    .menu-item i {
        font-size: 18px;
    }

    .sub-menu {
        position: absolute;
        left: 100%;
        top: 0;
        background: white;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        display: none;
        min-width: 180px;
        z-index: 1001;
    }

    .menu-item:hover > .sub-menu {
        display: block;
    }
`;
document.head.appendChild(style);
document.head.appendChild(style);

const STYLES = {
    colors: {
        primary: '#2c3e50',
        secondary: '#3498db',
        accent: '#e74c3c',
        background: '#f8f9fa',
        nodeTypes: {
            Drug: '#ff7675',
            Protein: '#4834d4',
            Disease: '#51d6df',
            Gene: '#00b894',
            Metabolite: '#e17055',
            Pathway: '#fdcb6e',
            Default: '#95a5a6',
            Transcript: '#e84393',
            Peptide: '#fbc531'
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
            .attr("dy", -4)
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
            case 'Metabolite':
                return d3.symbol().type(d3.symbolWye).size(size)();
            case 'Pathway':
                return d3.symbol().type(d3.symbolStar).size(size)();
            case 'Peptide':
                return d3.symbol().type(d3.symbolCross).size(size)();
            case 'Transcript':
                return d3.symbol().type(d3.symbolCross).size(size)();
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

        const ul = document.createElement('ul');
        ul.className = 'menu-items';

        CONTEXT_MENU_ITEMS.forEach(item => {
            const li = document.createElement('li');
            li.className = 'menu-item';
            
            // For expand action, create a special menu item with sub-menu
            if (item.action === 'expand') {
                const itemContent = document.createElement('div');
                itemContent.style.display = 'flex';
                itemContent.style.alignItems = 'center';
                itemContent.style.gap = '8px';
                itemContent.style.width = '100%';
                itemContent.innerHTML = `
                    <i class="material-icons">${item.icon}</i>
                    <span>${item.text}</span>
                    <i class="material-icons" style="margin-left: auto; font-size: 16px;">chevron_right</i>
                `;
                li.appendChild(itemContent);
                
                // Create sub-menu for node types
                const subMenu = createExpandSubMenu(d);
                li.appendChild(subMenu);
            } else {
                li.innerHTML = `
                    <i class="material-icons">${item.icon}</i>
                    <span>${item.text}</span>
                `;
                
                // Add event listener for other actions
                li.addEventListener('click', () => {
                    handleContextMenuAction(item.action, d.id);
                    contextMenu.remove();
                });
            }

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

    function createExpandSubMenu(node) {
        const subMenu = document.createElement('div');
        subMenu.className = 'sub-menu';
        
        const subUl = document.createElement('ul');
        subUl.className = 'menu-items';
        
        // Define node types with their icons and colors
        const nodeTypes = [
            { type: 'Drug', icon: 'local_pharmacy', color: '#ff7675' },
            { type: 'Disease', icon: 'healing', color: '#51d6df' },
            { type: 'Protein', icon: 'science', color: '#4834d4' },
            { type: 'Gene', icon: 'dashboard', color: '#00b894' },
            { type: 'Metabolite', icon: 'bubble_chart', color: '#e17055' },
            { type: 'Pathway', icon: 'account_tree', color: '#fdcb6e' },
            { type: 'Transcript', icon: 'description', color: '#e84393' },
            { type: 'Peptide', icon: 'architecture', color: '#fbc531' }
        ];
    
        nodeTypes.forEach(nodeType => {
            const li = document.createElement('li');
            li.className = 'menu-item';
            li.innerHTML = `
                <i class="material-icons" style="color: ${nodeType.color}">${nodeType.icon}</i>
                <span>Expand ${nodeType.type}</span>
            `;
            
            li.addEventListener('click', () => {
                expandNodeWithType(node.id, nodeType.type);
                // Close all menus
                document.querySelectorAll('.context-menu').forEach(menu => menu.remove());
            });
            
            subUl.appendChild(li);
        });
        
        subMenu.appendChild(subUl);
        return subMenu;
    }
    
    function expandNodeWithType(nodeId, nodeType) {
        // Set expansion settings for single node type
        window.expansionSettings = {
            neighbourTypes: [nodeType],
            maxNeighbours: 10,  // Default value
            maxDepth: 2         // Default value
        };
        
        // Call the existing expand function
        expandNodeForId(nodeId);
    }

    // Example implementation of the actions
    function expandNode(nodeId) {
        console.log('Expanding node:', nodeId);
        // Add your expand implementation

        // fetch and add more data to the graph
        expandNodeForId(nodeId);

    }

    function getExpansionSettings() {
        return window.expansionSettings || {
            neighbourTypes: ['Drug', 'Disease', 'Protein', 'Gene', 'Metabolite', 'Pathway', 'Transcript', 'Peptide'],
            maxNeighbours: 10,
            maxDepth: 1
        };
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

        const expansionSetting = getExpansionSettings()

        showLoading();
        fetch(`nodes/graph`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: nodeId,
                name: node.name,
                type: node.type,
                neighbour: expansionSetting.neighbourTypes.join(",") || selectedEntityTypes.join(","),
                existingNodes: globalNetworkValuesCopy.nodes.map(n => { if (n !== null) { return n.id } }),
                limit: `${expansionSetting.maxNeighbours || 10}`,
                depth: `${expansionSetting.maxDepth || 2}`,
            })
        })
            .then(response => {
                hideLoading();
                if (!response.ok) {
                    throw new Error('Failed to fetch node data');
                }
                return response.json();
            })
            .then(data => {
                if (data.nodes === null || data.links === null) {
                    console.log("No data found for the node");
                    return;
                }
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
                    nodes: [], links: []
                }); // Clear the graph first
                graph.updateGraph({
                    nodes: filteredNodes,
                    links: filteredLinks
                });
                //replace the globalNetworkValues with the updated one
                globalNetworkValues = globalNetworkValuesCopy;

                if (data.publications) {
                    // Update the publication section
                    globalNetworkValues.publications = { ...globalNetworkValues.publications, ...data.publications }
                    updatePublications();
                }
            })
            .catch(error => {
                hideLoading();
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
                        <input type="number" id="maxDepthFP" min="1" max="5" value="3">
                        <label for="maxDepthFP">Maximum Path Depth</label>
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
        getNodeDetails(node.id).then(nodeData => {
            const modalContent = `
            <style>
                .modal.open {
                    max-width: 80%;
                }
                .modal-content {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    max-width: 900px;
                    margin: 20px auto;
                    position: relative;
                }

                .modal-header {
                    padding: 20px;
                    border-bottom: 1px solid #eee;
                    background: #f8f9fa;
                    border-radius: 8px 8px 0 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .modal-header h4 {
                    margin: 0;
                    font-size: 1.4rem;
                    color: #2c3e50;
                    font-weight: 600;
                }

                .modal-close {
                    cursor: pointer;
                    font-size: 1.5rem;
                    color: #666;
                }

                .entity-badge {
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: white;
                    margin-left: 12px;
                }

                .entity-disease { background: #e74c3c; }
                .entity-protein { background: #3498db; }
                .entity-drug { background: #2ecc71; }

                .modal-body {
                    padding: 20px;
                }

                .info-section {
                    margin-bottom: 24px;
                    background: #fff;
                    border-radius: 8px;
                    border: 1px solid #e1e4e8;
                }

                .section-header {
                    padding: 12px 16px;
                    background: #f8f9fa;
                    border-bottom: 1px solid #e1e4e8;
                    font-weight: 600;
                    color: #2c3e50;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }

                .section-content {
                    padding: 16px;
                }

                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 16px;
                }

                .info-item {
                    background: #f8f9fa;
                    padding: 12px;
                    max-height: 300px;
                    overflow-y: auto;
                    border-radius: 6px;
                    border: 1px solid #e1e4e8;
                }

                .info-label {
                    font-size: 0.875rem;
                    color: #666;
                    margin-bottom: 4px;
                    font-weight: 500;
                }

                .info-value {
                    font-size: 0.95rem;
                    color: #2c3e50;
                    line-height: 1.4;
                }

                .long-text {
                    white-space: pre-wrap;
                    max-height: 300px;
                    overflow-y: auto;
                    padding: 12px;
                    background: #f8f9fa;
                    border-radius: 6px;
                    border: 1px solid #e1e4e8;
                    font-size: 0.95rem;
                    line-height: 1.5;
                }

                .tag-container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                }

                .tag {
                    background: #e9ecef;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.875rem;
                    color: #495057;
                    max-width: 200px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }

                .copy-button {
                    padding: 4px 8px;
                    font-size: 0.8rem;
                    color: #666;
                    background: #e9ecef;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-left: auto;
                }

                .copy-button:hover {
                    background: #dee2e6;
                }

                .chemical-formula {
                    font-family: monospace;
                    background: #f1f8ff;
                    padding: 2px 6px;
                    border-radius: 4px;
                    color: #0366d6;
                }

                .collapsible-content {
                    max-height: 0;
                    overflow: hidden;
                    transition: max-height 0.3s ease-out;
                }

                .expanded {
                    max-height: 1000px;
                }

                .toggle-button {
                    background: none;
                    border: none;
                    color: #0366d6;
                    cursor: pointer;
                    padding: 0;
                    font-size: 0.9rem;
                }
            </style>

            <div class="modal-content">
                <div class="modal-header">
                    <div style="display: flex; align-items: center;">
                        <h4 id="entityName"></h4>
                        <span id="entityType" class="entity-badge"></span>
                    </div>
                    <span class="modal-close">×</span>
                </div>
                <div class="modal-body" id="modalBody">
                    <!-- Content will be dynamically inserted here -->
                </div>
            </div>
            `;

            function formatData(data, label) {
                const modalBody = document.getElementById('modalBody');
                const entityName = document.getElementById('entityName');
                const entityType = document.getElementById('entityType');

                // Set entity name and type
                entityName.textContent = data.name;
                // let type = determineEntityType(data);
                entityType.textContent = label;
                entityType.className = `entity-badge entity-${label.toLowerCase()}`;

                modalBody.innerHTML = ''; // Clear existing content

                // Create sections based on entity type
                if (label === 'Disease') {
                    createDiseaseView(data, modalBody);
                } else if (label === 'Protein') {
                    createProteinView(data, modalBody);
                } else if (label === 'Drug') {
                    createDrugView(data, modalBody);
                } else if (label === 'Gene') {
                    createGeneView(data, modalBody);
                } else if (label === 'Metabolite') {
                    createMetaboliteView(data, modalBody);
                } else if (label === 'Pathway') {
                    createPathwayView(data, modalBody);
                } else if (label === 'Transcript') {
                    createTranscriptView(data, modalBody);
                } else if (label === 'Peptide') {
                    createPeptideView(data, modalBody);
                }
            }

            function determineEntityType(data) {
                if (data.id?.startsWith('DOID:')) return 'Disease';
                if (data.molecular_weight && data.organism) return 'Protein';
                if (data.drugbank_id) return 'Drug';
                return 'Unknown';
            }

            function createSection(title, content) {
                const section = document.createElement('div');
                section.className = 'info-section';

                const header = document.createElement('div');
                header.className = 'section-header';
                header.textContent = title;

                const sectionContent = document.createElement('div');
                sectionContent.className = 'section-content';
                sectionContent.appendChild(content);

                section.appendChild(header);
                section.appendChild(sectionContent);
                return section;
            }

            function createInfoItem(label, value, isLongText = false) {
                const item = document.createElement('div');
                isLongText = false;
                item.className = isLongText ? 'info-item' : 'info-item';

                if (!isLongText) {
                    const labelDiv = document.createElement('div');
                    labelDiv.className = 'info-label';
                    labelDiv.textContent = label;
                    item.appendChild(labelDiv);
                } else {
                    const labelDiv = document.createElement('div');
                    labelDiv.className = 'info-label';
                    labelDiv.textContent = label;
                    item.appendChild(labelDiv);
                }

                const valueDiv = document.createElement('div');
                valueDiv.className = isLongText ? 'info-value' : 'info-value';

                if (Array.isArray(value)) {
                    const tagContainer = document.createElement('div');
                    tagContainer.className = 'tag-container';
                    value.forEach(v => {
                        const tag = document.createElement('span');
                        tag.className = 'tag';
                        tag.textContent = v;
                        tagContainer.appendChild(tag);
                    });
                    valueDiv.appendChild(tagContainer);
                } else {
                    valueDiv.textContent = value;
                }

                if (!isLongText) {
                    item.appendChild(valueDiv);
                } else {
                    item.textContent = value;
                }

                return item;
            }

            function createDiseaseView(data, container) {
                // Overview section
                const overviewGrid = document.createElement('div');
                overviewGrid.className = 'info-grid';
                overviewGrid.appendChild(createInfoItem('ID', data.id));
                overviewGrid.appendChild(createInfoItem('Name', data.name));
                if (data.source) overviewGrid.appendChild(createInfoItem('Source', data.source));
                if (data.orphanet_definition) overviewGrid.appendChild(createInfoItem('Is Orphanet?', 'Yes'));
                container.appendChild(createSection('Overview', overviewGrid));

                // Description section
                let descContent = createInfoItem('Full Description', data.full_description, true);
                if (!data.full_description) {
                    descContent = createInfoItem('Description', data.description, true);
                    if (!data.description) {
                        descContent = createInfoItem('Description', data.umls_description, true);
                    }
                }
                container.appendChild(createSection('Description', descContent));

                if (data.orphanet_definition) {
                    // Orphanet section
                    const orphanetGrid = document.createElement('div');
                    orphanetGrid.className = 'info-grid';
                    orphanetGrid.appendChild(createInfoItem('Orphanet Definition', data.orphanet_definition));
                    orphanetGrid.appendChild(createInfoItem('Orphanet Epidemiology', data.orphanet_epidemiology));
                    orphanetGrid.appendChild(createInfoItem('Orphanet Treatment', data.orphanet_management_and_treatment));
                    container.appendChild(createSection('Orphanet Information', orphanetGrid));
                }

                // Identifiers section
                const identifiersGrid = document.createElement('div');
                identifiersGrid.className = 'info-grid';
                identifiersGrid.appendChild(createInfoItem('Synonyms', data.synonyms));
                container.appendChild(createSection('Identifiers', identifiersGrid));
            }

            function createProteinView(data, container) {
                // Basic Information
                const basicGrid = document.createElement('div');
                basicGrid.className = 'info-grid';
                basicGrid.appendChild(createInfoItem('Accession', data.accession));
                basicGrid.appendChild(createInfoItem('Full Name', data.full_name));
                basicGrid.appendChild(createInfoItem('Organism', data.organism));
                basicGrid.appendChild(createInfoItem('Molecular Weight', data.molecular_weight));
                container.appendChild(createSection('Basic Information', basicGrid));

                // Function Information
                if (data.general_function) {
                    const functionContent = createInfoItem('General Function', data.general_function, true);
                    container.appendChild(createSection('Function', functionContent));
                }

                // Technical Details
                const techGrid = document.createElement('div');
                techGrid.className = 'info-grid';
                if (data.isoelectric_point) techGrid.appendChild(createInfoItem('Isoelectric Point', data.isoelectric_point));
                if (data.specific_function) techGrid.appendChild(createInfoItem('Specific Function', data.specific_function));
                container.appendChild(createSection('Technical Details', techGrid));

                // Identifiers
                const identifiersGrid = document.createElement('div');
                identifiersGrid.className = 'info-grid';
                identifiersGrid.appendChild(createInfoItem('Synonyms', data.synonyms));
                container.appendChild(createSection('Identifiers', identifiersGrid));
            }

            function createDrugView(data, container) {
                // Basic Information
                const basicGrid = document.createElement('div');
                basicGrid.className = 'info-grid';
                basicGrid.appendChild(createInfoItem('Name', data.name));
                basicGrid.appendChild(createInfoItem('DrugBank ID', data.drugbank_id));
                basicGrid.appendChild(createInfoItem('CAS Number', data.cas_number));
                container.appendChild(createSection('Basic Information', basicGrid));

                // Clinical Information
                const clinicalContent = document.createElement('div');
                clinicalContent.className = 'info-grid';
                if (data.indication) clinicalContent.appendChild(createInfoItem('Indication', data.indication));
                if (data.mechanism_of_action) {
                    const mechanismContent = createInfoItem('Mechanism of Action', data.mechanism_of_action, true);
                    clinicalContent.appendChild(mechanismContent);
                }
                container.appendChild(createSection('Clinical Information', clinicalContent));

                // Chemical Properties
                const chemGrid = document.createElement('div');
                chemGrid.className = 'info-grid';
                if (data.chemical_formula) chemGrid.appendChild(createInfoItem('Chemical Formula', data.chemical_formula));
                if (data.molecular_weight) chemGrid.appendChild(createInfoItem('Molecular Weight', data.molecular_weight));
                if (data.state) chemGrid.appendChild(createInfoItem('State', data.state));
                container.appendChild(createSection('Chemical Properties', chemGrid));

                // Pharmacological Properties
                const pharmaGrid = document.createElement('div');
                pharmaGrid.className = 'info-grid';
                if (data.half_life) pharmaGrid.appendChild(createInfoItem('Half Life', data.half_life));
                if (data.protein_binding) pharmaGrid.appendChild(createInfoItem('Protein Binding', data.protein_binding));
                if (data.route_of_elimination) pharmaGrid.appendChild(createInfoItem('Route of Elimination', data.route_of_elimination));
                container.appendChild(createSection('Pharmacological Properties', pharmaGrid));
            }

            function createPeptideView(data, container) {
                const overviewGrid = document.createElement('div');
                overviewGrid.className = 'info-grid';
                overviewGrid.appendChild(createInfoItem('ID', data.id));
                overviewGrid.appendChild(createInfoItem('Type', data.type));
                if (data.source) overviewGrid.appendChild(createInfoItem('Unique', data.unique));
                container.appendChild(createSection('Overview', overviewGrid));

                // Identifiers
                if (data.synonyms) {
                    const identifiersGrid = document.createElement('div');
                    identifiersGrid.className = 'info-grid';
                    identifiersGrid.appendChild(createInfoItem('Synonyms', data.synonyms));
                    container.appendChild(createSection('Identifiers', identifiersGrid));
                }
            }

            function createTranscriptView(data, container) {
                /*
                {
                "id": "NM_080876.4",
                "assembly": "GCF_000001405.39",
                "name": "dual specificity phosphatase 19, transcript variant 1",
                "embedding": null,
                "taxid": "9606"
                }
                */
                const overviewGrid = document.createElement('div');
                overviewGrid.className = 'info-grid';
                overviewGrid.appendChild(createInfoItem('ID', data.id));
                overviewGrid.appendChild(createInfoItem('Name', data.name));
                overviewGrid.appendChild(createInfoItem('Assembly', data.assembly));
                overviewGrid.appendChild(createInfoItem('Tax ID', data.taxid));
                container.appendChild(createSection('Overview', overviewGrid));
            }


            function createGeneView(data, container) {
                const overviewGrid = document.createElement('div');
                overviewGrid.className = 'info-grid';
                overviewGrid.appendChild(createInfoItem('ID', data.id));
                overviewGrid.appendChild(createInfoItem('Name', data.name));
                if (data.source) overviewGrid.appendChild(createInfoItem('Source', data.source));
                if (data.family) overviewGrid.appendChild(createInfoItem('Family', data.family));
                container.appendChild(createSection('Overview', overviewGrid));

                // Identifiers
                if (data.synonyms) {
                    const identifiersGrid = document.createElement('div');
                    identifiersGrid.className = 'info-grid';
                    identifiersGrid.appendChild(createInfoItem('Synonyms', data.synonyms));
                    container.appendChild(createSection('Identifiers', identifiersGrid));
                }
            }

            function createMetaboliteView(data, container) {
                /*
                {
                    "id": "FDB005417",
                    "biomarker_type": "Chemical",
                    "name": "Guanidoacetic acid",
                    "biomarker_normal_state_values": [
                        "age: Adult,
                        sex: Both,
                        biofluid: Blood,
                        concentration: 16.8 (0.81-32.9) uM,
                        citation: Gatti, R. & Gioia, M. G. Liquid chromatographic analysis of guanidino compounds using furoin as a new fluorogenic reagent. J Pharm Biomed Anal 48, 754-759 (2008).",
                        "age: Adult,
                        sex: Both,
                    b   iofluid: Blood,
                    concentration: 16.8 (0.81-32.9) uM,
                    citation: Salomons, G. S., van Dooren, S. J., Verhoeven, N. M., Cecil, K. M., Ball, W. S., Degrauw, T. J. & Jakobs, C. X-linked creatine-transporter gene (SLC6A8) defect: a new creatine-deficiency syndrome. Am J Hum Genet 68, 1497-1500 (2001)."
                    ],
                    "embedding": null
                }
                */
                const overviewGrid = document.createElement('div');
                overviewGrid.className = 'info-grid';
                overviewGrid.appendChild(createInfoItem('ID', data.id));
                overviewGrid.appendChild(createInfoItem('Name', data.name));
                overviewGrid.appendChild(createInfoItem('Type', data.biomarker_type));
                container.appendChild(createSection('Overview', overviewGrid));

                // Normal State Values
                const normalValuesGrid = document.createElement('div');
                normalValuesGrid.className = 'info-grid';
                data.biomarker_normal_state_values.forEach((value, index) => {
                    const valueContent = createInfoItem(`Value ${index + 1}`, value, true);
                    normalValuesGrid.appendChild(valueContent);
                }
                );
                container.appendChild(createSection('Normal State Values', normalValuesGrid));
            }

            function createPathwayView(data, container) {
                /*{
                    "id": "R-HSA-983168",
                    "source": "Reactome",
                    "description": "Antigen processing: Ubiquitination & Proteasome degradation",
                    "name": "Antigen processing: Ubiquitination & Proteasome degradation",
                    "linkout": "https://reactome.org/PathwayBrowser/#/R-HSA-983168",
                    "embedding": null
                    }*/
                const overviewGrid = document.createElement('div');
                overviewGrid.className = 'info-grid';
                overviewGrid.appendChild(createInfoItem('ID', data.id));
                overviewGrid.appendChild(createInfoItem('Name', data.name));
                overviewGrid.appendChild(createInfoItem('Source', data.source));
                container.appendChild(createSection('Overview', overviewGrid));

                // Description
                const descContent = createInfoItem('Description', data.description, true);
                container.appendChild(createSection('Description', descContent));

                // Linkout, a better view
                const linkoutContent = createInfoItem('Linkout', data.linkout);
                container.appendChild(createSection('Linkout', linkoutContent));
            }


            // Close button functionality
            document.querySelector('.modal-close').addEventListener('click', () => {
                // Add your close modal logic here
                console.log('Modal closed');
            });

            const modalElement = document.createElement('div');
            modalElement.className = 'modal';
            modalElement.innerHTML = modalContent;
            document.body.appendChild(modalElement);

            // Initialize modal with specific options
            const modal = M.Modal.init(modalElement, {
                onOpenEnd: () => {
                    // formatProperties(nodeData);

                    // const relationships = globalNetworkValues["links"]
                    //     .filter(link => link.target.id === node.id)
                    //     .map(link => {
                    //         const source = link.source.id === node.id ? link.target : link.source;
                    //         return {
                    //             id: source.id,
                    //             name: source.name,
                    //             type: link.type
                    //         };
                    //     });
                    // formatRelationships(relationships);

                    formatData(nodeData.Properties, nodeData.Type);
                    // loadNodeRelationships(node.id);
                },
                onCloseEnd: () => {
                    modalElement.remove();
                    // Clean up any event listeners if needed
                },
                dismissible: true // Allows clicking outside to close
            });

            modal.open();
        });
    }

    function getNodeDetails(nodeId) {
        // Fetch node details for the given ID
        return fetch(`api/node-details?id=${nodeId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch node details');
                }
                return response.json();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }


    function loadNodeRelationships(nodeId) {
        // Fetch relationships for the given node
        // fetch from globalNetworkValues
        const relationships = globalNetworkValues["links"]
            .filter(link => link.target.id === nodeId)
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
    const maxDepth = parseInt(document.getElementById('maxDepthFP').value);

    console.log('Finding path:', {
        sourceNodeId,
        targetType,
        maxDepth
    });

    showLoading();
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
        hideLoading();
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