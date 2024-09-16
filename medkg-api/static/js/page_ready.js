$( function() {
	$('#network').height( screen.height - $('#top_menu').height() - 130 );
    $( "#orderingComponents" ).sortable();
    $( "#orderingComponents" ).disableSelection();
    $( "#orderingComponents_more" ).sortable();
    $( "#orderingComponents_more" ).disableSelection();

    const urlParams = new URLSearchParams(window.location.search);
            const id = urlParams.get('id');
            const name = urlParams.get('name');
            const type = urlParams.get('type');
            const neighbour = urlParams.get('neighbour');

            // LoadGraphValues(id, name, 'data/'+$('#network_f_name').val(), type);
            LoadGraph(id, name, 'data/'+$('#network_f_name').val(), type, neighbour);

});