/**
 * Persist changelist filters state (collapsed/expanded).
 */
'use strict';
{
    // Initialize filters.
    let filters = JSON.parse(sessionStorage.getItem('django.admin.filtersState'));

    if (!filters) {
        filters = {};
    }

    Object.entries(filters).forEach(([key, value]) => {
        const detailElement = document.querySelector(`[data-filter-title='${CSS.escape(key)}']`);

        // Check if the filter is present, it could be from another view.
        if (detailElement) {
            value ? detailElement.setAttribute('open', '') : detailElement.removeAttribute('open');
        }
    });

    /**
     * Saves the state of filter elements when toggled.
     *
     * Adds an event listener to all `<details>` elements to track their
     * open/closed state and stores this information in `sessionStorage`.
     */
    const details = document.querySelectorAll('details');
    details.forEach(detail => {
        detail.addEventListener('toggle', event => {
            filters[`${event.target.dataset.filterTitle}`] = detail.open;
            sessionStorage.setItem('django.admin.filtersState', JSON.stringify(filters));
        });
    });
}
