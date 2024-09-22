var network_file = document.getElementById("graph_starter").getAttribute("data-attr");
// cytoscape.use(cytoscapeCola);
my_style = fetch('css/css.json', { mode: 'no-cors' }).then(function (res) { return res.json() }).then(function (style) {
	return style;
});
// cytoscape.use('cytoscape-context-menus');
var cy = window.cy = cytoscape({
	container: $('#network'),
	style: my_style,
	elements: [],
	userZoomingEnabled: false,
	layout: {
		//orderOfNodeTypes: [3,1,2,4,5,6,7]
	}
});

var layout = cy.layout({
	name: 'cola',
	nodeSpacing: 30,
	edgeLength: 100,
	animate: true,
	randomize: false,
	maxSimulationTime: 1500,
	fit: true,
	padding: 30,
	nodeRepulsion: function (node) {
		return 2500;
	},
	gravity: 100,
	infinite: true,
	refresh: 1,
	//separated: 1,
	//lesslayer: 0,
	orderOfNodeTypes: [1, 2, 3, 5, 6, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15]
});

cy.on('mousedown', 'node', function (e) {
	if (isLayoutRunning) {
		layout.stop();
		isLayoutRunning = false;
	}
});

// Example of adding a context menu item
cy.on('cxttap', 'node', function (evt) {
	console.log('Context menu opened on node: ' + this.id());
	// Here you can implement your context menu logic
});

// Optionally, restart layout on canvas tap
cy.on('tap', function (e) {
	if (e.target === cy && !isLayoutRunning) {
		layout = cy.layout({
			name: 'cola',
			nodeSpacing: 30,
			edgeLength: 100,
			animate: true,
			randomize: false,
			maxSimulationTime: 1500,
			fit: false,
			padding: 30,
			nodeRepulsion: function (node) {
				return 2500;
			},
			gravity: 100,
			refresh: 1
		});
		layout.run();
		isLayoutRunning = true;
	}
});

// Run the layout
layout.run();

// Variable to track if layout is running
var isLayoutRunning = true;


function formatJSON(obj) {
	return JSON.stringify(obj, null, 2)
		.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
		.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
			var cls = 'json-number';
			if (/^"/.test(match)) {
				if (/:$/.test(match)) {
					cls = 'json-key';
				} else {
					cls = 'json-string';
				}
			} else if (/true|false/.test(match)) {
				cls = 'json-boolean';
			} else if (/null/.test(match)) {
				cls = 'json-null';
			}
			return '<span class="' + cls + '">' + match + '</span>';
		});
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

function LoadGraph(id, name, file, type = 'empty', neighbour = '') {
	neighbour = neighbour === '' ? $('#neighbour-type').val() !== 'Any' ? $('#neighbour-type').val() : null : neighbour;
	// neighbour = $('#neighbour-type').val();
	if (neighbour === 'Any') {
		neighbour = null;
	}
	showLoading();
	$.ajax({
		url: "nodes/graph",
		data: {
			id: id,
			name: name,
			type: type,
			neighbour: neighbour
		},
		success: function (result) {
			// remove any data present in the network
			hideLoading();
			cy.remove(cy.elements());
			cy.add(result)
			var layout = cy.layout({
				name: 'cola',
				nodeSpacing: 30,
				edgeLength: 100,
				animate: true,
				randomize: false,
				maxSimulationTime: 1500,
				fit: true,
				padding: 30,
				nodeRepulsion: function (node) {
					return 2500;
				},
				gravity: 100,
				infinite: false,
				refresh: 1,
				orderOfNodeTypes: [1, 2, 3, 5, 6, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15],
			});
			layout.run();
			var contextMenus = cy.contextMenus({
				menuItems: [
					{
						id: 'remove',
						content: 'Remove Node',
						tooltipText: 'Remove Node',
						selector: 'node',
						onClickFunction: function (event) {
							var target = event.target || event.cyTarget;
							target.remove();
						}
					},
					{
						id: 'expand',
						content: 'Expand',
						tooltipText: 'Expand Neighbours',
						selector: 'node',
						onClickFunction: function (event) {
							var target = event.target || event.cyTarget;
							expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"]);
						},
						submenu: [
							{
								id: 'remove-type-1',
								content: 'Any Neighbour',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"]);
								}
							},
							{
								id: 'remove-type-2',
								content: 'Drug',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Drug');
								}
							},
							{
								id: 'remove-all',
								content: 'Protein',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Protein');
								}
							},
							{
								id: 'remove-all',
								content: 'Disease',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Disease');
								}
							},
							{
								id: 'remove-all',
								content: 'Metabolite',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Metabolite');
								}
							},
							{
								id: 'remove-all',
								content: 'Phenotype',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Phenotype');
								}
							},
							{
								id: 'remove-all',
								content: 'Gene',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Gene');
								}
							},
							{
								id: 'remove-all',
								content: 'Pathway',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Pathway');
								}
							},
							{
								id: 'remove-all',
								content: 'Chromosome',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Chromosome');
								}
							},
							{
								id: 'remove-all',
								content: 'Publication',
								onClickFunction: function (event) {
									var target = event.target || event.cyTarget;
									expandForNodeId(target.data()["id"], target.data()["properties"]["name"], target.data()["Node_Type"], 'Publication');
								}
							}
						]
					},
					{
						id: 'show-details',
						content: 'Show Details',
						selector: 'node, edge',
						onClickFunction: function (event) {
							var target = event.target || event.cyTarget;
							var detailsContent = document.getElementById('details-content');

							// Clear previous content
							detailsContent.innerHTML = '';

							// Add general info card
							var generalInfo = {
								'ID': target.id(),
								'Type': target.isNode() ? 'Node' : 'Edge'
							};
							detailsContent.innerHTML += createDetailsCard('General Information', generalInfo);

							// Add data card
							detailsContent.innerHTML += createDetailsCard('Element Data', target.data()["properties"]);

							// Scroll to details section
							document.getElementById('details-section').scrollIntoView({ behavior: 'smooth' });
						}
					},
				]
			});

			$('#search_parameters').append('<li class="list-group-item"><b>Query Terms:</b></br>');



		},
		error: function (result) {
			hideLoading();
			alert('Failed to load the graph');
		}
	});

}

function expandForNodeId(nodeId, name, type, neighbour = '') {
	// neighbour = neighbour === '' ? $('#neighbour-type').val() !== 'Any' ? $('#neighbour-type').val() : null : neighbour;
	neighbour = neighbour === '' ? 'Any' : neighbour;
	if (neighbour === 'Any') {
		neighbour = null;
	}
	showLoading();
	$.ajax({
		url: "nodes/graph",
		data: {
			id: nodeId,
			name: name,
			type: type,
			neighbour: neighbour
		},
		success: function (result) {
			hideLoading();

			if ((result.edges == null || result.edges.length === 0) && (result.nodes == null || result.nodes.length === 0)) {
				showError("No new data was added to the graph.");
				return;
			}
			showNotification("Successfully expanded the graph.");
			// cy.nodes().forEach(node => node.lock());
			var initialNodeCount = cy.nodes().length;
			var initialEdgeCount = cy.edges().length;

			// Add the new data
			cy.add(result);

			// Check the new number of nodes and edges
			var newNodeCount = cy.nodes().length;
			var newEdgeCount = cy.edges().length;
			// cy.add(result)
			if (newNodeCount === initialNodeCount && newEdgeCount === initialEdgeCount) {
				// No new elements were added
				showError("No new data was added to the graph.");
			} else {
				var layout = cy.layout({
					name: 'cola',
					nodeSpacing: 30,
					edgeLength: 100,
					animate: true,
					randomize: false,
					maxSimulationTime: 1500,
					fit: true,
					padding: 30,
					nodeRepulsion: function (node) {
						return 2500;
					},
					gravity: 100,
					infinite: false,
					refresh: 1,
					orderOfNodeTypes: [1, 2, 3, 5, 6, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15],
				});
				layout.run();
			}
		},
	});
}

function showLoading() {
	document.getElementById('loadingOverlay').style.display = 'flex';
}

// Function to hide the loading overlay
function hideLoading() {
	document.getElementById('loadingOverlay').style.display = 'none';
}

function showError(message) {
	M.toast({
		html: message,
		classes: 'red',
		displayLength: 5000,
		inDuration: 300,
		outDuration: 375,
		activationPercent: 0.1
	});
}

function showNotification(message) {
	M.toast({
		html: message,
		classes: 'green',
		displayLength: 5000,
		inDuration: 300,
		outDuration: 375,
		activationPercent: 0.1
	});
}