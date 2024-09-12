var network_file = document.getElementById("graph_starter").getAttribute("data-attr");

my_style = fetch('css/css.json', {mode: 'no-cors'}).then(function(res) { return res.json()}).then(function(style){
	return style;
});
// cytoscape.use('cytoscape-context-menus');
var cy = window.cy = cytoscape({
	container: $('#network'),
	style: my_style,
	elements: [],
	userZoomingEnabled: false,
	layout: {
		name: 'cose-bilkent',// 'medKGLayout',
  		rows: 4,
		fit: 'viewport',
		//separated: 1,
		//lesslayer: 0,
		orderOfNodeTypes: [1,2,3,5,6,4,7,8,9,10,11,12,13,14,15]
		//orderOfNodeTypes: [3,1,2,4,5,6,7]
	}
});
cy.on('cxttap', (event) => {
	// Suppress the default context menu
	event.preventDefault();
  });


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

function LoadGraph(id, name, file, type='empty'){
	neighbour = $('#neighbour-type').val();
	if (neighbour === 'Any'){
		neighbour = null;
	}
	showLoading();
	$.ajax( {
		url: "nodes/graph",
		data: {
		  id: id,
		  name: name,
		  type: type,
		  neighbour: neighbour
		},
		success: function( result ) {
			// remove any data present in the network
			hideLoading();
			cy.remove(cy.elements());
			cy.add(result)
			var layout = cy.layout({
				name: 'cose-bilkent', //$('#layout').val(),
				rows: 4,
				orderOfNodeTypes: [1,2,3,5,6,4,7,8,9,10,11,12,13,14,15],
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
					}
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
                            document.getElementById('details-section').scrollIntoView({behavior: 'smooth'});
					}
				},
				]
			  });
			
				$('#search_parameters').append( '<li class="list-group-item"><b>Query Terms:</b></br>');
				
				
		  
			}
	  } );

}

function expandForNodeId(nodeId, name, type){
	neighbour = $('#neighbour-type').val();
	if (neighbour === 'Any'){
		neighbour = null;
	}
	showLoading();
	$.ajax( {
		url: "nodes/graph",
		data: {
			id: nodeId,
			name: name,
			type: type,
			neighbour: neighbour
		},
		success: function( result ) {
			hideLoading();
			// cy.nodes().forEach(node => node.lock());
			cy.add(result)
			var layout = cy.layout({
				name: 'cose-bilkent', //$('#layout').val(),
				rows: 4,
				orderOfNodeTypes: [1,2,3,5,6,4,7,8,9,10,11,12,13,14,15],
			  });
			  layout.run();
	  }, });
	}

function showLoading() {
	document.getElementById('loadingOverlay').style.display = 'flex';
}

// Function to hide the loading overlay
function hideLoading() {
	document.getElementById('loadingOverlay').style.display = 'none';
}

