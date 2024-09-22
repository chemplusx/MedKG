function split(val) {
  return val.split('|');
}

document.addEventListener('DOMContentLoaded', function() {
  // Debounce function
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Function to fetch autocomplete results
  function fetchAutocompleteResults(query, callback) {
    // Replace this with your actual API call
    fetch(`search_in_graph?limit=10&term=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => callback(data))
      .catch(error => console.error('Error fetching autocomplete results:', error));
  }

  // Debounced version of fetchAutocompleteResults
  const debouncedFetch = debounce(fetchAutocompleteResults, 300);

  // Function to initialize autocomplete
  function initAutocomplete() {
    const elem = document.querySelector('#node_search');
    if (!elem) {
      console.error('Autocomplete element not found');
      return;
    }

    const options = {
      data: {},
      minLength: 1,
      onAutocomplete: function(result) {
        console.log('Selected:', result);
      }
    };

    let autoCompleteInstance;

    try {
      autoCompleteInstance = M.Autocomplete.init(elem, options);
    } catch (error) {
      console.error('Error initializing Autocomplete:', error);
      return;
    }

    // Add event listener for input changes
    elem.addEventListener('input', function() {
      const query = this.value;
      if (query.length >= options.minLength) {
        debouncedFetch(query, function(results) {
          // Update autocomplete data
          if (autoCompleteInstance && typeof autoCompleteInstance.updateData === 'function') {
            autoCompleteInstance.updateData(results);
            autoCompleteInstance.open();
          } else {
            console.error('Autocomplete instance not properly initialized');
          }
        });
      }
    });
  }

  // Initialize autocomplete when the DOM is fully loaded
  if (document.readyState === 'complete') {
    initAutocomplete();
  } else {
    window.addEventListener('load', initAutocomplete);
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
        LoadGraph(value.id, value.label, 'data/' + $('#node_search_f_name').val(), value.type, '');
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

function showWarning(message) {
  M.toast({
    html: message,
    classes: 'orange',
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