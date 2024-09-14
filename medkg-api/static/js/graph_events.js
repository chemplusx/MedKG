
function make_high(ele) {
	var degree =
		(ele.outgoers()
			.union(ele.incomers())
			.length) / 2;
	degree = Math.floor(degree);



	ele.addClass('zelected');
	ele.connectedEdges().connectedNodes().addClass('highlightednode');
	ele.connectedEdges().animate({
		style: { width: "3px", "opacity": "1", "font-size": "10px" }
	});

}

function apply_high(id, name, file, type = 'empty') {
	var ele = cy.$('node[id = "' + id + '"]');
	if (ele.length)
		make_high(ele);
	else {
		ele2 = cy.$('node[id = "' + name + '"]');
		if (ele2.length)
			make_high(ele2);
	}
}

$(function () {
	cy.on('tap', function (event) {
		var evtTarget = event.target;
		if (evtTarget === cy) {

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
					style: { width: "1px", "opacity": "0.25", "font-size": "0px" }
				});
			});
		}
	});

	cy.on('select', function (e) {
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
		document.getElementById('details-section').scrollIntoView({ behavior: 'smooth' });

		if (ele.data().source) {
			conn_nodes = ele.connectedNodes();
			el1 = conn_nodes[0].data();
			if (conn_nodes.length === 1) {
				// self interaction
				el2 = conn_nodes[0].data();
			} else {
				el2 = conn_nodes[1].data();
			}
			ele.connectedNodes().addClass('highlightednode');

			ele.animate({
				style: { width: "3px", "opacity": "1", "font-size": "10px" }
			});

			if ($('#selected_edges').hasClass('d-none')) {
				$('#selected_edges').append('<h5 class="row alert alert-secondary p-1 mb-0 border-bottom-0 border-secondary">Selected Edges</h5>');
				$('#selected_edges').removeClass('d-none');
			}
		} else {
			if ($('#selected_nodes').hasClass('d-none')) {
				$('#selected_nodes').append('<h5 class="row alert alert-secondary p-1 mb-0 border-bottom-0 border-secondary">Selected Nodes</h5>');
				$('#selected_nodes').removeClass('d-none');
				$('#makeNewSearchWithSelecteds_btn').removeClass('d-none');
			}
			ele.addClass('zelected');
			ele.connectedEdges().connectedNodes().addClass('highlightednode');

			ele.connectedEdges().animate({
				style: { width: "3px", "opacity": "1", "font-size": "10px" }
			});
		}
		if (ele.data().source) {
			conn_nodes = ele.connectedNodes();
			el1 = conn_nodes[0].data();
			if (conn_nodes.length === 1) {
				// self interaction
				el2 = conn_nodes[0].data();
			} else {
				el2 = conn_nodes[1].data();
			}
			ele.connectedNodes().addClass('highlightednode');

			ele.animate({
				style: { width: "3px", "opacity": "1", "font-size": "10px" }
			});

			$.ajax({
				type: "POST",
				url: 'selected_edge.php',
				data: { node1: el1, node2: el2, Edge: ele.data() },
				success: function (result) {
					if ($('#selected_edges').hasClass('d-none')) {
						$('#selected_edges').append('<h5 class="row alert alert-secondary p-1 mb-0 border-bottom-0 border-secondary">Selected Edges</h5>');
						$('#selected_edges').removeClass('d-none');
					}
					$('#selected_edges').append(result);
				}
			});


		} else {
			var degree =
				(ele.outgoers()
					.union(ele.incomers())
					.length) / 2;
			degree = Math.floor(degree);
			$.ajax({
				type: "POST",
				url: 'selected_node.php',
				data: { node: ele.data(), degree: degree },
				success: function (result) {
					if ($('#selected_nodes').hasClass('d-none')) {
						$('#selected_nodes').append('<h5 class="row alert alert-secondary p-1 mb-0 border-bottom-0 border-secondary">Selected Nodes</h5>');
						$('#selected_nodes').removeClass('d-none');
						$('#makeNewSearchWithSelecteds_btn').removeClass('d-none');
					}
					$('#selected_nodes').append(result);
				}
			});

			ele.addClass('zelected');
			ele.connectedEdges().connectedNodes().addClass('highlightednode');

			ele.connectedEdges().animate({
				style: { width: "3px", "opacity": "1", "font-size": "10px" }
			});
		}



	});

	cy.on('mouseover', 'node', function (e) {
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
	cy.on('mouseout', 'node', function (e) {
		var ele = e.target;
		cy.elements()
			.removeClass('semitransp');
		ele.removeClass('highlight')
			.outgoers()
			.union(ele.incomers())
			.removeClass('highlight');
	});

});