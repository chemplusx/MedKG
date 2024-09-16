function split(val) {
  return val.split('|');
}

$("#node_search").on("keydown", function (event) {
  if (event.keyCode === $.ui.keyCode.TAB &&
    $(this).autocomplete("instance").menu.active) {
    event.preventDefault();
  }
}).autocomplete({
  minLength: 1,
  source: function (request, response) {
    $.ajax({
      url: "search_in_graph",
      dataType: "json",
      data: {
        term: request.term,
        limit: 10,
        file: $('#network_f_name').val(),
      },
      success: function (data) {
        //console.log( data );
        response(data);
      }
    });
  },
  focus: function () {
    // prevent value inserted on focus
    return false;
  },
  select: function (event, ui) {
    var terms = split(this.value);
    terms.pop();
    this.value = terms.join('');
    //console.log(ui.item.value);
    LoadGraph(ui.item.id, ui.item.label, 'data/' + $('#network_f_name').val(), ui.item.type, '');
    // apply_high(ui.item.id, ui.item.label, 'data/'+$('#network_f_name').val(), ui.item.type);
    return false;
  }
});


function loadEverything() {
  document.addEventListener('DOMContentLoaded', function () {
    var autoCompleteElem = document.querySelector('#node_search');
    var autoCompleteInstance = M.Autocomplete.init(autoCompleteElem, {
      minLength: 1,
      onAutocomplete: function (selectedValue) {
        console.log('Selected:', selectedValue);
        const value = this.options.data[selectedValue].value;
        LoadGraph(value.id, value.label, 'data/' + $('#network_f_name').val(), value.type, '');
      }
    });

    // Debounce function to limit API calls
    function debounce(func, wait) {
      let timeout;
      return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    }

    // Function to fetch autocomplete suggestions from API
    async function fetchAutocompleteSuggestions(query) {
      try {
        const response = await fetch(`/search_in_graph?limit=10&term=${encodeURIComponent(query)}`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();

        // Transform the data into the format Materialize expects
        const autocompleteData = {};
        data.forEach(item => {
          const key = item.label + ":" + item.properties.id + " (" + item.type + ")";
          autocompleteData[key] = {
            value: item,
            imageSrc: "images/" + getImageName(item) // Assuming `item.icon` contains the image URL
          };
        });

        // Update the autocomplete data
        autoCompleteInstance.updateData(autocompleteData);
        autoCompleteInstance.open();

        // Add images to the dropdown
        setTimeout(() => {
          const dropdownItems = document.querySelectorAll('.autocomplete-content li');
          dropdownItems.forEach(item => {
            const key = item.textContent.trim();
            if (autocompleteData[key]) {
              const img = item.querySelector('img')
              // const img = document.createElement('img');
              img.src = autocompleteData[key].imageSrc;
              img.style.width = '30px';
              img.style.height = '30px';
              img.style.marginRight = '10px';
              item.prepend(img);
            }
          });
        }, 0);

      } catch (error) {
        console.error('Error fetching autocomplete suggestions:', error);
      }
    }

    // Debounced version of the fetch function
    const debouncedFetch = debounce(fetchAutocompleteSuggestions, 300);

    // Add event listener for input changes
    autoCompleteElem.addEventListener('input', function (e) {
      const query = e.target.value;
      if (query.length >= 1) {
        debouncedFetch(query);
      }
    });
  });
}
function getImageName(item) {
  return "1_" + item.type.toLowerCase() + ".png";
}

// check if path is /visualise , then run loadEverything
if (window.location.pathname === '/visualise') {
  loadEverything();
}

function showLoading() {
	document.getElementById('loadingOverlay').style.display = 'flex';
}

// Function to hide the loading overlay
function hideLoading() {
	document.getElementById('loadingOverlay').style.display = 'none';
}