/**
 * Persist changelist filters state (collapsed/expanded).
 * This script ensures that the state of filters (open or collapsed) is remembered
 * across page reloads by using the browser's session storage.
 */
'use strict';
{
    /**
     * Initialize the filters state from session storage.
     * If no stored state exists, create an empty object.
     * @type {Object.<string, boolean>} A dictionary where keys are filter titles and values are their open states.
     */
    let filters = JSON.parse(sessionStorage.getItem('django.admin.filtersState'));

    if (!filters) {
        filters = {}; // If no filters state exists, initialize as an empty object.
    }

    // Restore the state of each filter based on the stored information.
    Object.entries(filters).forEach(([key, value]) => {
        /**
         * @param {string} key - The filter's title used as the identifier.
         * @param {boolean} value - The state of the filter (true for open, false for collapsed).
         */
        const detailElement = document.querySelector(`[data-filter-title='${CSS.escape(key)}']`);

        // Ensure the filter exists on the current view.
        if (detailElement) {
            value ? detailElement.setAttribute('open', '') : detailElement.removeAttribute('open');
        }
    });

    // Save the filter state when a user toggles the filter open or closed.
    const details = document.querySelectorAll('details');
    details.forEach(detail => {
        /**
         * Event listener for the toggle event.
         * Updates the filter's state in session storage.
         * @param {Event} event - The toggle event fired when the <details> element's state changes.
         */
        detail.addEventListener('toggle', event => {
            filters[`${event.target.dataset.filterTitle}`] = detail.open;

            // Update the session storage with the new state of filters.
            sessionStorage.setItem('django.admin.filtersState', JSON.stringify(filters));
        });
    });
}
