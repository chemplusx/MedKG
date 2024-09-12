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
document.addEventListener('DOMContentLoaded', function() {
        var autoCompleteElem = document.querySelector('#node_search');
        var autoCompleteInstance = M.Autocomplete.init(autoCompleteElem, {
            minLength: 1,
            onAutocomplete: function(selectedValue) {
                console.log('Selected:', selectedValue);
                value = this.options.data[selectedValue];

                LoadGraph(value.id, value.label, 'data/'+$('#network_f_name').val(), value.type);
                // Here you can add any additional logic you want to execute when an item is selected
            }
        });

        // Debounce function to limit API calls
        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        // Function to fetch autocomplete suggestions from API
        async function fetchAutocompleteSuggestions(query) {
            try {
                // Replace with your actual API endpoint
                const response = await fetch(`/search_in_graph?limit=10&term=${encodeURIComponent(query)}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                // $.ajax( {
                //   url: "search_in_graph",
                //   dataType: "json",
                //   data: {
                //     term: request.term,
                //     limit: 10,
                //     file: $('#network_f_name').val(),
                //   },
                //   success: function( data ) {
                //     //console.log( data );
                //     response( data );
                //   }
                // } );
                const data = await response.json();
                
                // Transform the data into the format Materialize expects
                const autocompleteData = {};
                data.forEach(item => {
                  key = item.label+":"+item.properties.id+" ("+item.type+")";
                    autocompleteData[key] = item;  // or item.icon if you have icons
                });

                // Update the autocomplete data
                autoCompleteInstance.updateData(autocompleteData);
                autoCompleteInstance.open();
            } catch (error) {
                console.error('Error fetching autocomplete suggestions:', error);
            }
        }

        // Debounced version of the fetch function
        const debouncedFetch = debounce(fetchAutocompleteSuggestions, 300);

        // Add event listener for input changes
        autoCompleteElem.addEventListener('input', function(e) {
            const query = e.target.value;
            if (query.length >= 1) {
                debouncedFetch(query);
            }
        });
});