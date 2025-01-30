// Initialize filter sections
function initializeFilterSections() {
    const filterSections = document.querySelectorAll('.relation-filter-section');

    filterSections.forEach(section => {
        // Create show more button
        const showMoreBtn = document.createElement('button');
        showMoreBtn.className = 'show-more-btn';
        showMoreBtn.innerHTML = '<span>Show all filters</span><i class="material-icons">expand_more</i>';

        // Insert button after section
        section.parentNode.insertBefore(showMoreBtn, section.nextSibling);

        // Add click handler
        showMoreBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            section.classList.toggle('expanded');
            showMoreBtn.classList.toggle('expanded');
            showMoreBtn.querySelector('span').textContent =
                section.classList.contains('expanded') ? 'Show less' : 'Show all filters';
        });

        // Add click handler to collapse when clicking outside
        document.addEventListener('click', (e) => {
            if (!section.contains(e.target) && !showMoreBtn.contains(e.target)) {
                section.classList.remove('expanded');
                showMoreBtn.classList.remove('expanded');
                showMoreBtn.querySelector('span').textContent = 'Show all filters';
            }
        });
    });
}

function GetAllRelations() {
    fetch('list/relations')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            data.forEach(relation => {
                allFilterableRelations.push(relation);
            });

            let filterSection = document.getElementById('relationFilterSection');
            filterSection.innerHTML = '';

            let headDiv = document.createElement('div');
            let heading = document.createElement('h6');
            heading.innerHTML = 'Relationship Types';
            headDiv.appendChild(heading);
            let selectAllButton = document.createElement('button');
            selectAllButton.className = 'btn-small';
            selectAllButton.innerHTML = 'Select All';
            selectAllButton.style = 'margin-right: 10px;margin-bottom: 10px;';
            selectAllButton.onclick = function () {
                selectAllEntities('relation');
            };
            headDiv.appendChild(selectAllButton);
            let clearAllButton = document.createElement('button');
            clearAllButton.className = 'btn-small';
            clearAllButton.innerHTML = 'Clear All';
            clearAllButton.style = 'margin-right: 10px;margin-bottom: 10px;';
            clearAllButton.onclick = function () {
                clearAllEntities('relation');
            };
            headDiv.appendChild(clearAllButton);

            filterSection.appendChild(headDiv);
            allFilterableRelations.forEach(relation => {
                let relationCheckbox = document.createElement('label');
                relationCheckbox.innerHTML = `<input type="checkbox" class="filled-in" checked="checked" value="${relation}" />
                <span>${relation}</span>`;
                filterSection.appendChild(relationCheckbox);
            });
            initializeFilters();

            

            // Call this function when the page loads
            initializeFilterSections();
        })
        .catch(error => {
            console.error('Error:', error);
        });

}


function GetAllLabels() {
    fetch('list/labels')
        .then(response => response.json())
        .then(data => {
            console.log(data);

            data.forEach(label => {
                if (label !== 'Units' && label !== 'Subject' && label !== 'Project' && label !== 'AllEntries')
                    allFilterableLabels.push(label);
            });
            let filterSection = document.getElementById('labelFilterSection');
            filterSection.innerHTML = '';
            let headDiv = document.createElement('div');
            let heading = document.createElement('h6');
            heading.innerHTML = 'Entity Types';
            headDiv.appendChild(heading);
            let selectAllButton = document.createElement('button');
            selectAllButton.className = 'btn-small';
            selectAllButton.innerHTML = 'Select All';
            selectAllButton.style = 'margin-right: 10px;margin-bottom: 10px;';
            selectAllButton.onclick = function () {
                selectAllEntities('label');
            };
            headDiv.appendChild(selectAllButton);
            let clearAllButton = document.createElement('button');
            clearAllButton.className = 'btn-small';
            clearAllButton.innerHTML = 'Clear All';
            clearAllButton.style = 'margin-right: 10px;margin-bottom: 10px;';
            clearAllButton.onclick = function () {
                clearAllEntities('label');
            };
            headDiv.appendChild(clearAllButton);
            filterSection.appendChild(headDiv);
            allFilterableLabels.forEach(label => {

                let labelCheckbox = document.createElement('label');
                labelCheckbox.innerHTML = `<input type="checkbox" class="filled-in" checked="checked" value="${label}" />
                <span>${label}</span>`;
                filterSection.appendChild(labelCheckbox);
            });
            initializeFilters();
        })
        .catch(error => {
            console.error('Error:', error);
        });

}


function selectAllEntities(type) {
    // if label, then should be looked into elementWithId = 'labelFilterSection' -> inputs
    // if relation, then should be looked into elementWithId = 'relationFilterSection' -> inputs
    let elementWithId = type === 'label' ? 'labelFilterSection' : 'relationFilterSection';
    document.querySelectorAll(`#${elementWithId} input[type="checkbox"]`).forEach(cb => cb.checked = true);
    applyFilters();
}

function clearAllEntities(type) {
    let elementWithId = type === 'label' ? 'labelFilterSection' : 'relationFilterSection';
    document.querySelectorAll(`#${elementWithId} input[type="checkbox"]`).forEach(cb => cb.checked = false);
    applyFilters();
}


function toggleAdvancedSearch() {
    const advancedOptions = document.querySelector('.advanced-options');
    if (advancedOptions) {
        advancedOptions.style.display = advancedOptions.style.display === 'none' ? 'block' : 'none';
    }
}

function clearSearch() {
    document.getElementById('mainSearch').value = '';
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
    document.getElementById('yearFrom').value = '';
    document.getElementById('yearTo').value = '';
    currentPage = 1;
    updateResults([]);
}

function showLoading() {
    // Add loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.className = 'progress';
    loadingDiv.innerHTML = '<div class="indeterminate"></div>';
    document.querySelector('.search-bar').appendChild(loadingDiv);
}

function hideLoading() {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function showError(message) {
    M.toast({ html: message, classes: 'red' });
}

function showNotification(message) {
    M.toast({ html: message, classes: 'green' });
}

