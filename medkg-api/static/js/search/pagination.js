function updatePagination(totalItems) {
    totalResults = totalItems;
    const totalPages = Math.ceil(totalItems / resultsPerPage);

    document.getElementById('resultCount').textContent = totalItems;
    document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;

    document.getElementById('prevButton').disabled = currentPage === 1;
    document.getElementById('nextButton').disabled = currentPage === totalPages;
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        performSearch();
    }
}

function nextPage() {
    const totalPages = Math.ceil(totalResults / resultsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        performSearch();
    }
}

function updateSort() {
    const sortOrder = document.getElementById('sortOrder').value;
    performSearch();
}