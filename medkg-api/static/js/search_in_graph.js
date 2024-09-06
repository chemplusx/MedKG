function split( val ) {
    return val.split(  '|' );
  }
  
   $( "#node_search" ).on( "keydown", function( event ) {
          if ( event.keyCode === $.ui.keyCode.TAB &&
              $( this ).autocomplete( "instance" ).menu.active ) {
            event.preventDefault();
          }
        }).autocomplete({
          minLength: 1,
          source: function( request, response ) {
              $.ajax( {
                url: "search_in_graph",
                dataType: "json",
                data: {
                  term: request.term,
                  limit: 10,
                  file: $('#network_f_name').val(),
                },
                success: function( data ) {
                  //console.log( data );
                  response( data );
                }
              } );
          },
          focus: function() {
            // prevent value inserted on focus
            return false;
          },
          select: function( event, ui ) {
            var terms = split( this.value );
            terms.pop();
            this.value = terms.join( '' );
            //console.log(ui.item.value);
            LoadGraph(ui.item.id, ui.item.label, 'data/'+$('#network_f_name').val(), ui.item.type);
            // apply_high(ui.item.id, ui.item.label, 'data/'+$('#network_f_name').val(), ui.item.type);
            return false;
          }
        });
  