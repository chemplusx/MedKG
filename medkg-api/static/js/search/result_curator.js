function updateResults(apiResponse) {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '';

    const exactMatches = apiResponse.exactMatches || [];
    const partialMatches = apiResponse.partialMatches || [];

    fetchedResults = {
        exactMatches: apiResponse.exactMatches || [],
        partialMatches: apiResponse.partialMatches || []
    };

    if (exactMatches.length === 0 && partialMatches.length === 0) {
        resultsContainer.innerHTML = '<p>No results found. Try adjusting your search terms or filters.</p>';
        return;
    }



    // Display exact matches section
    if (exactMatches.length > 0) {
        const exactSection = document.createElement('div');
        exactSection.className = 'matches-section';
        exactSection.innerHTML = `<h6>Exact Matches (${exactMatches.length})</h6>`;
        exactMatches.forEach(result => {
            const card = createResultCard(result);
            exactSection.appendChild(card);
        });
        resultsContainer.appendChild(exactSection);
    }

    // Display partial matches section
    if (partialMatches.length > 0) {
        const partialSection = document.createElement('div');
        partialSection.className = 'matches-section';
        partialSection.innerHTML = `<h6>Partial Matches (${partialMatches.length})</h6>`;
        partialMatches.forEach(result => {
            const card = createResultCard(result);
            partialSection.appendChild(card);
        });
        resultsContainer.appendChild(partialSection);
    }

    // updatePagination(exactMatches.length + partialMatches.length);
    applyFilters();
}

function toggleDescription(element) {
    const card = element.closest('.result-card');
    const description = card.querySelector('.result-description');

    if (description.style.webkitLineClamp === 'none') {
        description.style.webkitLineClamp = '2';
        element.innerHTML = '<i class="material-icons tiny">description</i> Show Full Description';
    } else {
        description.style.webkitLineClamp = 'none';
        element.innerHTML = '<i class="material-icons tiny">description</i> Show Less';
    }
}

function createResultCard(result) {
    const card = document.createElement('div');
    card.className = 'result-card';

    const entityType = result.type.toLowerCase();
    const entityClass = `entity-${entityType}`;
    const source = result.data_source || '';
    const sourceLink = result.publication || '';

    // Get name from either label or properties.name
    const displayName = result.label || result.properties.name;

    // Get ID from either properties.id or the main id field
    const displayId = result.properties.id || result.id;

    // Get description from properties and truncate it
    const description = result.properties.fullDesciption || result.properties.description || result.properties.function || 'No description available';

    card.innerHTML = `
        <div class="entity-type ${entityClass}">
            ${result.type}
        </div>
        <div class="result-title">${displayName}</div>
        <div class="result-description">${description}</div>
        <div class="result-meta">
            <span>ID: ${displayId}</span>
            <span>Source: ${source}    <a href="${sourceLink}"/></span>
        </div>
        <div class="result-actions">
            <a href="#" onclick="toggleRelationships('${result.id}')">
                <i class="material-icons tiny">share</i> View Relationships
            </a>
            <a href="#" onclick="toggleDescription(this)">
                <i class="material-icons tiny">description</i> Show Full Description
            </a>
            <a href="#" onclick="exportEntry('${result.id}')">
                <i class="material-icons tiny">file_download</i> Export
            </a>
        </div>
    `;

    const relationshipAction = document.createElement('a');
    relationshipAction.href = '#';
    relationshipAction.innerHTML = '<i class="material-icons">account_tree</i> View Relations';
    relationshipAction.onclick = (e) => {
        e.preventDefault();
        toggleRelationships(result.id);
    };
    
    // Add relationships dropdown container
    const relationshipsDropdown = document.createElement('div');
    relationshipsDropdown.className = 'relationships-dropdown';
    relationshipsDropdown.id = `relationships-${result.id}`;
    
    // Append new elements to the card
    // actionsDiv.appendChild(relationshipAction);
    card.appendChild(relationshipsDropdown);

    return card;
}

// Add filter management functions
function applyFilters() {
    const filters = {
        entityTypes: Array.from(document.querySelectorAll('#labelFilterSection input[type="checkbox"]'))
            .filter(cb => cb.checked)
            .map(cb => cb.value),
        relationshipTypes: Array.from(document.querySelectorAll('#relationFilterSection input[type="checkbox"]'))
            .filter(cb => cb.checked)
            .map(cb => cb.value),
        evidenceLevel: Array.from(document.querySelectorAll('input[type="checkbox"][value^="experimental"], input[type="checkbox"][value^="clinical"], input[type="checkbox"][value^="computational"]'))
            .filter(cb => cb.checked)
            .map(cb => cb.value),
        yearRange: {
            from: document.getElementById('yearFrom').value,
            to: document.getElementById('yearTo').value
        }
    };

    // Filter the results
    const filteredResults = {
        exactMatches: filterResults(fetchedResults.exactMatches, filters),
        partialMatches: filterResults(fetchedResults.partialMatches, filters)
    };

    // Update the display
    displayFilteredResults(filteredResults);
}

function filterResults(results, filters) {
    return results.filter(result => {
        // Entity Type filter
        if (filters.entityTypes.length > 0) {
            if (!filters.entityTypes.includes(result.type)) {
                return false;
            }
        }else{
            return false;
        }

        // Relationship Type filter (if result has relationships)
        if (filters.relationshipTypes.length > 0 && result.relationships) {
            const hasMatchingRelationship = result.relationships.some(rel =>
                filters.relationshipTypes.includes(rel.type)
            );
            if (!hasMatchingRelationship) {
                return false;
            }
        }

        // Evidence Level filter
        if (filters.evidenceLevel.length > 0 && result.evidence) {
            const hasMatchingEvidence = result.evidence.some(ev =>
                filters.evidenceLevel.includes(ev.type.toLowerCase())
            );
            if (!hasMatchingEvidence) {
                return false;
            }
        }

        // Year Range filter
        if (filters.yearRange.from || filters.yearRange.to) {
            const year = result.year || (result.properties && result.properties.year);
            if (year) {
                if (filters.yearRange.from && year < parseInt(filters.yearRange.from)) {
                    return false;
                }
                if (filters.yearRange.to && year > parseInt(filters.yearRange.to)) {
                    return false;
                }
            }
        }

        return true;
    });
}

function displayFilteredResults(filteredResults) {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '';

    const totalExact = filteredResults.exactMatches.length;
    const totalPartial = filteredResults.partialMatches.length;

    if (totalExact === 0 && totalPartial === 0) {
        resultsContainer.innerHTML = `
    <div class="no-results">
        <p>No results match the selected filters. Try adjusting your filter criteria.</p>
    </div>`;
        document.getElementById('resultCount').textContent = '0';
        return;
    }

    // Display exact matches
    if (totalExact > 0) {
        const exactSection = document.createElement('div');
        exactSection.className = 'matches-section exact-matches';
        exactSection.innerHTML = `
    <h5>Exact Matches</h5>
    <div class="search-stats">Found ${totalExact} exact ${totalExact === 1 ? 'match' : 'matches'}</div>
`;

        filteredResults.exactMatches.forEach(result => {
            const card = createResultCard(result);
            exactSection.appendChild(card);
        });
        resultsContainer.appendChild(exactSection);
    }

    // Display partial matches toggle and content
    if (totalPartial > 0) {
        const partialSection = document.createElement('div');
        partialSection.className = 'matches-section partial-matches';

        // Create toggle button
        const toggleButton = document.createElement('div');
        toggleButton.className = 'partial-matches-toggle';
        toggleButton.innerHTML = `
            <div>
                <h6 style="margin: 0;">Additional Partial Matches Available</h6>
                <span class="partial-matches-count">Found ${totalPartial} partial ${totalPartial === 1 ? 'match' : 'matches'}</span>
            </div>
            <i class="material-icons">expand_more</i>
        `;

        // Create content container
        const contentDiv = document.createElement('div');
        contentDiv.className = 'partial-matches-content';

        if (totalExact === 0) {
            contentDiv.classList.add('visible');
            toggleButton.querySelector('.material-icons').textContent = 'expand_less';
        }

        // Add partial match cards
        filteredResults.partialMatches.forEach(result => {
            const card = createResultCard(result);
            contentDiv.appendChild(card);
        });

        // Add click handler for toggle
        toggleButton.addEventListener('click', (e) => {
            const icon = toggleButton.querySelector('.material-icons');
            const content = toggleButton.nextElementSibling;

            if (content.classList.contains('visible')) {
                content.classList.remove('visible');
                icon.textContent = 'expand_more';
            } else {
                content.classList.add('visible');
                icon.textContent = 'expand_less';
            }
        });

        partialSection.appendChild(toggleButton);
        partialSection.appendChild(contentDiv);
        resultsContainer.appendChild(partialSection);
    }

    // Update total result count
    document.getElementById('resultCount').textContent = totalExact + totalPartial;
}

// Add event listeners for filters
function initializeFilters() {
    // Add change event listeners to all filter checkboxes
    document.querySelectorAll('#labelFilterSection input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
        checkbox.addEventListener('click', applyFilters);
    });
    document.querySelectorAll('#relationFilterSection input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
        checkbox.addEventListener('click', applyFilters);
    });

    // Add input event listeners to year range inputs
    document.getElementById('yearFrom').addEventListener('change', applyFilters);
    document.getElementById('yearTo').addEventListener('change', applyFilters);

    // Initialize any Materialize components
    const selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);
}

// Call this when the page loads
// document.addEventListener('DOMContentLoaded', initializeFilters);

// Modify the clear filters function
function clearFilters() {
    // Reset checkboxes
    document.querySelectorAll('.filter-section input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = true;
    });

    // Reset year range
    document.getElementById('yearFrom').value = '';
    document.getElementById('yearTo').value = '';

    // Reapply filters (which will now show all results)
    applyFilters();
}

function performSearch() {
    let destinationNodeType, depth, startNode, endNode, maxHops;

    const searchTerm = document.getElementById('mainSearch').value;
    showLoading();

    fetch(`api/global-search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            searchTerm, destinationNodeType, depth, startNode, endNode, maxHops
        }),
    })
        .then(response => response.json())
        .then(data => {
            updateResults(data);
            hideLoading();
        })
        .catch(function (error) {
            console.error('Error:', error);
            hideLoading();
            showError('An error occurred. Please try again later.', error);
        });
}


document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('mainSearch');
    const enableAutocompleteCheckbox = document.getElementById('enableAutocomplete');
    let autocompleteInstance = null;

    function initializeAutocomplete() {
        if (autocompleteInstance) {
            autocompleteInstance.destroy();
        }

        if (enableAutocompleteCheckbox.checked) {
            autocompleteInstance = M.Autocomplete.init(searchInput, {
                data: {},
                minLength: 2,
                onAutocomplete: function (text) {
                    performSearch();
                }
            });
        }
    }

    // Initialize autocomplete based on initial checkbox state
    initializeAutocomplete();

    // Handle checkbox changes
    enableAutocompleteCheckbox.addEventListener('change', function () {
        initializeAutocomplete();
    });

    // Update autocomplete data when typing
    searchInput.addEventListener('input', debounce(function (e) {
        const query = e.target.value;
        if (query.length >= 2 && enableAutocompleteCheckbox.checked) {
            fetch(`search_in_graph?limit=10&term=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    const autocompleteData = {};

                    // Process exact matches
                    if (data.exactMatches) {
                        data.exactMatches.forEach(item => {
                            const displayName = item.label || item.properties.name;
                            const key = `${displayName} (${item.type})`;
                            autocompleteData[key] = {
                                text: displayName,
                                type: item.type,
                                id: item.id
                            };
                        });
                    }

                    // Process partial matches
                    if (data.partialMatches) {
                        data.partialMatches.forEach(item => {
                            const displayName = item.label || item.properties.name;
                            const key = `${displayName} (${item.type})`;
                            autocompleteData[key] = {
                                text: displayName,
                                type: item.type,
                                id: item.id
                            };
                        });
                    }

                    autocompleteInstance.updateData(autocompleteData);
                    autocompleteInstance.open();
                })
                .catch(error => {
                    console.error('Autocomplete error:', error);
                });
        }
    }, 300));
});

// Utility function for debouncing
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















async function toggleRelationships(entityId) {
    const dropdown = document.getElementById(`relationships-${entityId}`);
    const isActive = dropdown.classList.contains('active');
    
    if (!isActive) {
        const selectedRelations = Array.from(document.querySelectorAll('#relationFilterSection input:checked'))
            .map(cb => cb.value);
        
        try {
            const relationships = await fetchRelationships(entityId, selectedRelations);
            if (relationships.length === 0) {
                dropdown.innerHTML = '<p>No relationships found. Try changing the filters.</p>';
                return;
            }
            // Group relationships by source
            const sourceEntity = relationships[0]?.sourceEntity;
            
            // Clear previous content
            dropdown.innerHTML = '';
            
            // Create container
            const container = document.createElement('div');
            container.className = 'relationship-container';
            
            // Add source entity
            const sourceDiv = document.createElement('div');
            sourceDiv.className = 'source-entity';
            sourceDiv.textContent = sourceEntity;
            container.appendChild(sourceDiv);
            
            // Create relationships list
            const relationshipsList = document.createElement('div');
            relationshipsList.className = 'relationships-list';
            
            // Add relationships
            relationships.forEach(rel => {
                const relItem = document.createElement('div');
                relItem.className = 'relationship-item';
                
                const relType = document.createElement('span');
                relType.className = 'relationship-type';
                relType.textContent = rel.relationType;
                
                const targetBadge = document.createElement('span');
                targetBadge.className = `entity-badge ${getEntityTypeStyle(rel.targetType)}`;
                targetBadge.textContent = rel.targetEntity;
                targetBadge.onclick = (e) => {
                    e.stopPropagation();
                    showEntityModal(rel.targetDetails, e);
                };
                
                relItem.appendChild(relType);
                relItem.appendChild(targetBadge);
                relationshipsList.appendChild(relItem);
            });
            
            container.appendChild(relationshipsList);
            dropdown.appendChild(container);

            // Add network visualization button
            const networkBtn = document.createElement('button');
            networkBtn.className = 'view-network-btn';
            networkBtn.innerHTML = '<i class="material-icons">bubble_chart</i> View Network';
            networkBtn.onclick = (e) => {
                // scroll page to the top
                window.scrollTo(0, 0);

                e.preventDefault();
                showNetworkVisualization(entityId);
            };
            dropdown.appendChild(networkBtn);
            
        } catch (error) {
            console.error('Error fetching relationships:', error);
            dropdown.innerHTML = '<p>Error loading relationships. Try changing the filters.</p>';
        }
    }
    
    dropdown.classList.toggle('active');
}

function showEntityModal(entityData, event) {
    // Remove any existing modals
    const existingModal = document.querySelector('.entity-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.className = 'entity-modal';
    modal.style.left = `${event.pageX + 10}px`;
    modal.style.top = `${event.pageY + 10}px`;
    
    // Close button
    const closeBtn = document.createElement('span');
    closeBtn.className = 'modal-close';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = () => modal.remove();
    
    // Header
    const header = document.createElement('div');
    header.className = 'modal-header';
    header.innerHTML = `<h4>${entityData.Props.name}</h4>`;
    
    // Content
    const content = document.createElement('div');
    content.className = 'modal-content';
    content.innerHTML = `
        <p><strong>Type:</strong> ${entityData.Labels.join(', ')}</p>
        <p><strong>Description:</strong> ${entityData.Props.description || 'No description available'}</p>
    `;
    
    // Actions
    const actions = document.createElement('div');
    actions.className = 'modal-actions';
    
    const searchBtn = document.createElement('button');
    searchBtn.className = 'btn waves-effect waves-light';
    searchBtn.innerHTML = '<i class="material-icons left">search</i>Search This Entity';
    searchBtn.onclick = () => {
        document.getElementById('mainSearch').value = entityData.Props.name;
        performSearch();
        modal.remove();
    };
    
    const exportBtn = document.createElement('button');
    exportBtn.className = 'btn waves-effect waves-light';
    exportBtn.innerHTML = '<i class="material-icons left">file_download</i>Export';
    exportBtn.onclick = () => {
        exportEntity(entityData);
    };
    
    actions.appendChild(searchBtn);
    actions.appendChild(exportBtn);
    
    modal.appendChild(closeBtn);
    modal.appendChild(header);
    modal.appendChild(content);
    modal.appendChild(actions);
    
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    document.addEventListener('click', function closeModal(e) {
        if (!modal.contains(e.target)) {
            modal.remove();
            document.removeEventListener('click', closeModal);
        }
    });
    modal.style.display = 'block';
}

// Function to export entity data
function exportEntity(entityData) {
    const data = {
        name: entityData.Props.name,
        type: entityData.Labels.join(', '),
        description: entityData.Props.description,
        id: entityData.ElementId
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${entityData.Props.name.toLowerCase().replace(/\s+/g, '_')}_data.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Function to process relationships data
function processRelationships(data) {
    return data.map(rel => ({
        sourceEntity: rel.source.Props.name || 'Unknown Source',
        relationType: rel.label.replace(/_/g, ' ').toLowerCase(),
        targetEntity: rel.target.Props.name || 'Unknown Target',
        sourceType: rel.source.Labels[0],
        targetType: rel.target.Labels[0],
        sourceDetails: rel.source,
        targetDetails: rel.target
    }));
}

// Function to get entity type style
function getEntityTypeStyle(type) {
    const typeStyles = {
        'Drug': 'entity-drug',
        'Disease': 'entity-disease',
        'Protein': 'entity-protein',
        'Gene': 'entity-gene',
        'Compound': 'entity-drug' // Treating Compound same as Drug for styling
    };
    return typeStyles[type] || '';
}

// Function to fetch relationships from backend
async function fetchRelationships(entityId, relationTypes) {
    // Replace with your actual API endpoint
    const response = await fetch(`api/node-relations`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ entityId, relationTypes })
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch relationships');
    }
    
    const data =  await response.json();
    return processRelationships(data);
}

// Function to show network visualization
function showNetworkVisualization(entityId) {
    // Use the existing visualization panel
    const panel = document.getElementById('visualizationPanel');
    // const content = document.getElementById('visualizationContent');
    
    // Show loading state
    // content.innerHTML = '<div class="progress"><div class="indeterminate"></div></div>';
    panel.classList.add('open');

    // Find the node details from fetchedResults
    // id, name, neighbour, type, depth
    // Get all Entity filters
    let neighbours = Array.from(document.querySelectorAll('#labelFilterSection input[type="checkbox"]'))
    .filter(cb => cb.checked)
    .map(cb => cb.value);
    // Join all the filters
    let neighboursString = neighbours.join(',');
    let entityData = fetchedResults.exactMatches.find(entity => entity.id === entityId);
    if (!entityData) {
        entityData = fetchedResults.partialMatches.find(entity => entity.id === entityId);
    }
    ShowNetwork(entityData.id, entityData.label, neighboursString, entityData.type, 5);
    
    // Fetch and display network data
    // fetchNetworkData(entityId)
    //     .then(data => {
    //         // Replace with your actual network visualization code
    //         content.innerHTML = '<div id="network-viz"></div>';
    //         // Initialize network visualization here
    //     })
    //     .catch(error => {
    //         content.innerHTML = '<p>Error loading network visualization</p>';
    //     });
}

// Function to fetch network data
async function fetchNetworkData(entityId) {
    const response = await fetch(`/api/network/${entityId}`);
    if (!response.ok) {
        throw new Error('Failed to fetch network data');
    }
    return await response.json();
}