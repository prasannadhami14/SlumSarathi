/**
 * Dynamic Search Functionality
 * This script provides real-time search for any list with a search input
 * 
 * Usage:
 * 1. Add data-search-endpoint="your-endpoint" to your search input
 * 2. Add data-list-container="your-container-id" to your search input
 * 3. Include this script in your template
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Search script loaded');
    
    // Find all search inputs with the required data attributes
    const searchInputs = document.querySelectorAll('input[name="q"][data-search-endpoint][data-list-container]');
    console.log('Found search inputs:', searchInputs.length);
    
    searchInputs.forEach(function(searchInput, index) {
        const endpoint = searchInput.getAttribute('data-search-endpoint');
        const containerId = searchInput.getAttribute('data-list-container');
        const listContainer = document.getElementById(containerId);
        
        console.log(`Search input ${index + 1}:`, {
            endpoint: endpoint,
            containerId: containerId,
            listContainer: listContainer
        });
        
        if (!listContainer) {
            console.warn(`Container with ID "${containerId}" not found`);
            return;
        }
        
        let timeout = null;
        
        searchInput.addEventListener('input', function() {
            console.log('Input event triggered, value:', searchInput.value);
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                const query = encodeURIComponent(searchInput.value);
                const url = `${endpoint}?q=${query}`;
                console.log('Making AJAX request to:', url);
                
                fetch(url)
                    .then(response => {
                        console.log('Response status:', response.status);
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Response data:', data);
                        if (data.html !== undefined) {
                            listContainer.innerHTML = data.html;
                            console.log('Updated container with new HTML');
                        } else {
                            console.warn('No HTML content in response');
                        }
                    })
                    .catch(error => {
                        console.error('Search request failed:', error);
                        // Optionally show user-friendly error message
                        // listContainer.innerHTML = '<div class="alert alert-danger">Search failed. Please try again.</div>';
                    });
            }, 300); // debounce for 300ms
        });
        
        console.log(`Event listener added to search input ${index + 1}`);
    });
}); 