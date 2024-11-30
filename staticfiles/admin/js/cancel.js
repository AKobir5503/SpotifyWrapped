'use strict';
{
    /**
     * Executes the given function when the DOM is fully loaded.
     * If the DOM is already loaded, the function is executed immediately.
     *
     * @param {Function} fn - The function to execute when the DOM is ready.
     */
    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    ready(function() {
        /**
         * Handles the click event for cancel links.
         *
         * - Prevents the default link behavior.
         * - Closes the popup window if `_popup` is present in the URL parameters.
         * - Navigates back in browser history otherwise.
         *
         * @param {Event} event - The event object for the click event.
         */
        function handleClick(event) {
            event.preventDefault();
            const params = new URLSearchParams(window.location.search);
            if (params.has('_popup')) {
                window.close(); // Close the popup.
            } else {
                window.history.back(); // Otherwise, go back.
            }
        }

        document.querySelectorAll('.cancel-link').forEach(function(el) {
            el.addEventListener('click', handleClick);
        });
    });
}
