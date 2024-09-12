
function make_high(ele){
	var degree = 
	(ele.outgoers()
		.union(ele.incomers())
		.length) / 2;
	degree = Math.floor(degree);

	

	ele.addClass('zelected');
	ele.connectedEdges().connectedNodes().addClass('highlightednode');
	ele.connectedEdges().animate({
		style: {width: "3px","opacity":"1","font-size": "10px"}
	});		
	
}

function apply_high(id, name, file, type='empty'){
	var ele = cy.$('node[id = "'+id+'"]');
	if(ele.length)
		make_high(ele);
	else{
		ele2 = cy.$('node[id = "'+name+'"]');
		if(ele2.length)
			make_high(ele2);
	}
}

$( function() {
cy.on('tap', function(event){
	var evtTarget = event.target;
	if( evtTarget === cy ){

		$('#selected_edges').html('');
		$('#selected_edges').addClass('d-none');

		$('#selected_nodes').html('');
		$('#selected_nodes').addClass('d-none');
		$('#makeNewSearchWithSelecteds_btn').addClass('d-none');
		// if clicked on the empty area (canvas)
		cy.$('node').removeClass('highlightednode');
		cy.$('node').removeClass('zelected');
		cy.$('edge').forEach((ed) => {
			//ed.removeClass('highlightededge');
			ed.animate({
				style: {width: "1px","opacity":"0.25","font-size": "0px"}
			});
		});
	}
});

cy.on('select', function(e){
	var ele = e.target;

	var target = e.target || e.cyTarget;
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
});

cy.on('mouseover', 'node', function(e) {
	var ele = e.target;
	cy.elements()
		.difference(ele.outgoers()
			.union(ele.incomers()))
		.not(ele)
		.addClass('semitransp');
	ele.addClass('highlight')
		.outgoers()
		.union(ele.incomers())
		.addClass('highlight');
});
cy.on('mouseout', 'node', function(e) {
	var ele = e.target;
	cy.elements()
		.removeClass('semitransp');
	ele.removeClass('highlight')
		.outgoers()
		.union(ele.incomers())
		.removeClass('highlight');
});


});