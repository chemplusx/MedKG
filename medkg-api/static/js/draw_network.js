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
		name: 'medKGLayout',
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
	// 			<table class="details-table">
	// 				<tbody>
	// `;

	// for (let key in data) {
	// 	if (data.hasOwnProperty(key)) {
	// 		let value = data[key];
	// 		if (typeof value === 'object' && value !== null) {
	// 			value = JSON.stringify(value);
	// 		}
	// 		if (value !== null && value !== '') {
	// 			cardHtml += `
	// 				<tr>
	// 					<td class="key">${key}</td>
	// 					<td class="value" style="overflow: wrap;">${value}</td>
	// 				</tr>
	// 			`;
	// 		}
	// 	}
	// }

	// cardHtml += `
	// 				</tbody>
	// 			</table>
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
				name: $('#layout').val(),
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
				// result.search.forEach((s) => {
				// 	for (var p in s) {
				// 		apply_high(s[p]["id"], s[p][x], network_file, p);
				// 		// if( p == 'Disease' ||  p == 'KEGG Disease' || p == 'KEGG Pathway' || p == 'Pathway' || p == 'HPO' || p == 'Compound'){
				// 		// 	for (var x in s[p]) {
				// 		// 		apply_high(s[p]["id"], s[p][x], network_file, p);
				// 		// 		var l;
				// 		// 		switch(p){
				// 		// 			case 'Disease':
				// 		// 				l = 'Disease(s) - EFO';
				// 		// 			break;
				// 		// 			case 'KEGG Disease':
				// 		// 				l = 'Disease(s) - KEGG';
				// 		// 			break;
				// 		// 			case 'Pathway':
				// 		// 				l = 'Pathway(s) - Reactome';
				// 		// 			break;
				// 		// 			case 'KEGG Pathway':
				// 		// 				l = 'Pathway(s) - KEGG';
				// 		// 			break;
				// 		// 			case 'HPO':
				// 		// 				l = 'Phenotype(s)';
				// 		// 			break;
				// 		// 			case 'Compound':
				// 		// 				l = 'Compound(s)';
				// 		// 			break;
				// 		// 		}
				// 		// 		$('#search_parameters').append( '<span class="pl-4 font-italic">' +l+': '+s[p][x]+'</span>' );
				// 		// 	}
				// 		// }else if( p == 'Drug' ){
				// 		// 	l = 'Drug(s)';
				// 		// 	for (var x in s[p])
				// 		// 		for (var o in s[p][x]){
				// 		// 			apply_high(s[p]["id"], s[p][x][o], network_file, p);
				// 		// 			$('#search_parameters').append( '<span class="pl-4 font-italic">' +l+': '+s[p][x][o]+'</span>' );
				// 		// 		}
				// 		// }else{
				// 		// 	l = 'Gene(s)/Protein(s)';
				// 		// 	$('#search_parameters').append( '<span class="pl-4 font-italic">' +l+': '+s[p]+'</span>' );
				// 		// 	if(p != 'Protein'){
				// 		// 		apply_high(s[p]["id"], s[p], network_file, p);
				// 		// 	}else{
				// 		// 		var accs = s[p].split(",");
				// 		// 		for (var a in accs){
				// 		// 			apply_high(accs[a]["id"], accs[a], network_file, p);
				// 		// 		}
				// 		// 	}
				// 		// }
				// 	}
				// });
				// $('#search_parameters').append('</li>');
			
				// var check = 0;
				// if(result.options.num_of_fn_nodes == result.options.num_of_pathways)
				// 	if(result.options.num_of_fn_nodes == result.options.num_of_phenotypes)
				// 		if(result.options.num_of_fn_nodes == result.options.num_of_drugs)
				// 			if(result.options.num_of_fn_nodes == result.options.num_of_diseases)
				// 				if(result.options.num_of_fn_nodes == result.options.num_of_compounds)
				// 					check = 1;
			
				// if(check)
				// 	$('#search_parameters').append( '<li class="list-group-item">Number of Nodes: '+result.options.num_of_fn_nodes+'</li>' );
				// else{
				// 	$('#search_parameters').append( '<li class="list-group-item"><b>Number of Nodes:</b></br>'+
					
				// 	'<span class="pl-4 font-italic">Neighbouring genes/proteins: ' +result.options.num_of_fn_nodes+ '</span></br>'+
				// 	'<span class="pl-4 font-italic">Pathways: ' +result.options.num_of_pathways+ '</span></br>'+
				// 	'<span class="pl-4 font-italic">Diseases: ' +result.options.num_of_diseases+ '</span></br>'+
				// 	'<span class="pl-4 font-italic">Phenotypes: ' +result.options.num_of_phenotypes+ '</span></br>'+
				// 	'<span class="pl-4 font-italic">Drugs: ' +result.options.num_of_drugs+ '</span></br>'+
				// 	'<span class="pl-4 font-italic">Compounds: ' +result.options.num_of_compounds+ '</span></br>'
					
				// 	+'</li>');
				// }
			
				// var fn_stat = 'no';
				// if(result.options.fn)
				// 	fn_stat = 'yes';
				// $('#search_parameters').append( '<li class="list-group-item">Include interacting proteins: '+fn_stat+'</li>' );
				// var rw = 'no';
				// if(result.options.reviewed_filter)
				// 	rw = 'yes';
				// $('#search_parameters').append( '<li class="list-group-item">Only reviewed genes/proteins: '+rw+'</li>' );
			
				// var cc = 'no';
				// if(result.options.chembl_compounds)
				// 	cc = 'yes';
				// $('#search_parameters').append( '<li class="list-group-item">Include ChEMBL compounds: '+cc+'</li>' );
				
				// var pc = 'no';
				// if(result.options.predictions)
				// 	pc = 'yes';
				// $('#search_parameters').append( '<li class="list-group-item">Include predicted compounds: '+pc+'</li>' );
				
				// separator = ',';
				// $('#search_parameters').append( '<li class="list-group-item">Included tax Id(s): '+result.options.tax_ids.join(separator)+'</li>' );
				// $('#search_parameters').append( '<li class="list-group-item"><i>This query was processed in <b>'+result.options.search_runtime+'</b> seconds</i></li>' );
				
		  
			}
	  } );


	// $.ajax({
	// 	url: "/load_graph",
	// 	type: "POST",
	// 	data: {file: network_file},
	// 	success: function(data){
	// 		console.log(data);
	// 	}
	// });
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
				name: $('#layout').val(),
				rows: 4,
				orderOfNodeTypes: [1,2,3,5,6,4,7,8,9,10,11,12,13,14,15],
			  });
			  layout.run();
	  }, });
	}
// data = fetch(network_file+'.json', {mode: 'no-cors'}).then(function(res){return res.json()}).then(function(data){
// 	return data;
// });


// my_style = fetch('css/css.json', {mode: 'no-cors'}).then(function(res) { return res.json()}).then(function(style){
// 	return style;
// });

// var cy = window.cy = cytoscape({
// 	container: $('#network'),
// 	style: my_style,
// 	elements: data,
// 	layout: {
// 		name: 'medKGLayout',
// 		fit: 'viewport',
// 		//separated: 1,
// 		//lesslayer: 0,
// 		orderOfNodeTypes: [1,2,3,5,6,4,7]
// 		//orderOfNodeTypes: [3,1,2,4,5,6,7]
// 	}
// });

// data.then(function(result) {
// 	$('#search_parameters').append( '<li class="list-group-item"><b>Query Terms:</b></br>');
// 	result.search.forEach((s) => {
// 		for (var p in s) {
// 			if( p == 'Disease' ||  p == 'KEGG Disease' || p == 'KEGG Pathway' || p == 'Pathway' || p == 'HPO' || p == 'Compound'){
// 				for (var x in s[p]) {
// 					apply_high(s[p]["id"], s[p][x], network_file, p);
// 					var l;
// 					switch(p){
// 						case 'Disease':
// 							l = 'Disease(s) - EFO';
// 						break;
// 						case 'KEGG Disease':
// 							l = 'Disease(s) - KEGG';
// 						break;
// 						case 'Pathway':
// 							l = 'Pathway(s) - Reactome';
// 						break;
// 						case 'KEGG Pathway':
// 							l = 'Pathway(s) - KEGG';
// 						break;
// 						case 'HPO':
// 							l = 'Phenotype(s)';
// 						break;
// 						case 'Compound':
// 							l = 'Compound(s)';
// 						break;
// 					}
// 					$('#search_parameters').append( '<span class="pl-4 font-italic">' +l+': '+s[p][x]+'</span>' );
// 				}
// 			}else if( p == 'Drug' ){
// 				l = 'Drug(s)';
// 				for (var x in s[p])
// 					for (var o in s[p][x]){
// 						apply_high(s[p]["id"], s[p][x][o], network_file, p);
// 						$('#search_parameters').append( '<span class="pl-4 font-italic">' +l+': '+s[p][x][o]+'</span>' );
// 					}
// 			}else{
// 				l = 'Gene(s)/Protein(s)';
// 				$('#search_parameters').append( '<span class="pl-4 font-italic">' +l+': '+s[p]+'</span>' );
// 				if(p != 'Protein'){
// 					apply_high(s[p]["id"], s[p], network_file, p);
// 				}else{
// 					var accs = s[p].split(",");
// 					for (var a in accs){
// 						apply_high(accs[a]["id"], accs[a], network_file, p);
// 					}
// 				}
// 			}
// 		}
// 	});
// 	$('#search_parameters').append('</li>');

// 	var check = 0;
// 	if(result.options.num_of_fn_nodes == result.options.num_of_pathways)
// 		if(result.options.num_of_fn_nodes == result.options.num_of_phenotypes)
// 			if(result.options.num_of_fn_nodes == result.options.num_of_drugs)
// 				if(result.options.num_of_fn_nodes == result.options.num_of_diseases)
// 					if(result.options.num_of_fn_nodes == result.options.num_of_compounds)
// 						check = 1;

// 	if(check)
// 		$('#search_parameters').append( '<li class="list-group-item">Number of Nodes: '+result.options.num_of_fn_nodes+'</li>' );
// 	else{
// 		$('#search_parameters').append( '<li class="list-group-item"><b>Number of Nodes:</b></br>'+
		
// 		'<span class="pl-4 font-italic">Neighbouring genes/proteins: ' +result.options.num_of_fn_nodes+ '</span></br>'+
// 		'<span class="pl-4 font-italic">Pathways: ' +result.options.num_of_pathways+ '</span></br>'+
// 		'<span class="pl-4 font-italic">Diseases: ' +result.options.num_of_diseases+ '</span></br>'+
// 		'<span class="pl-4 font-italic">Phenotypes: ' +result.options.num_of_phenotypes+ '</span></br>'+
// 		'<span class="pl-4 font-italic">Drugs: ' +result.options.num_of_drugs+ '</span></br>'+
// 		'<span class="pl-4 font-italic">Compounds: ' +result.options.num_of_compounds+ '</span></br>'
		
// 		+'</li>');
// 	}

// 	var fn_stat = 'no';
// 	if(result.options.fn)
// 		fn_stat = 'yes';
// 	$('#search_parameters').append( '<li class="list-group-item">Include interacting proteins: '+fn_stat+'</li>' );
// 	var rw = 'no';
// 	if(result.options.reviewed_filter)
// 		rw = 'yes';
// 	$('#search_parameters').append( '<li class="list-group-item">Only reviewed genes/proteins: '+rw+'</li>' );

// 	var cc = 'no';
// 	if(result.options.chembl_compounds)
// 		cc = 'yes';
// 	$('#search_parameters').append( '<li class="list-group-item">Include ChEMBL compounds: '+cc+'</li>' );
	
// 	var pc = 'no';
// 	if(result.options.predictions)
// 		pc = 'yes';
// 	$('#search_parameters').append( '<li class="list-group-item">Include predicted compounds: '+pc+'</li>' );
	
// 	separator = ',';
// 	$('#search_parameters').append( '<li class="list-group-item">Included tax Id(s): '+result.options.tax_ids.join(separator)+'</li>' );
// 	$('#search_parameters').append( '<li class="list-group-item"><i>This query was processed in <b>'+result.options.search_runtime+'</b> seconds</i></li>' );
	
	
// });
function showLoading() {
	document.getElementById('loadingOverlay').style.display = 'flex';
}

// Function to hide the loading overlay
function hideLoading() {
	document.getElementById('loadingOverlay').style.display = 'none';
}

