'use strict';

{
    const $ = django.jQuery;

    /**
     * Initializes the Select2 widget for all matched elements.
     *
     * This function attaches the Select2 plugin to elements, providing an
     * AJAX-based autocomplete feature. The AJAX request includes additional
     * metadata (e.g., `app_label`, `model_name`, `field_name`) for server-side
     * filtering.
     *
     * @returns {jQuery} The jQuery object for chaining.
     */
    $.fn.djangoAdminSelect2 = function() {
        $.each(this, function(i, element) {
            $(element).select2({
                ajax: {
                    /**
                     * Prepares the AJAX data payload for Select2 requests.
                     *
                     * @param {Object} params - The parameters sent by Select2, including
                     *                          the current search term and pagination.
                     * @param {string} params.term - The search term entered by the user.
                     * @param {number} params.page - The current page number for pagination.
                     * @returns {Object} An object containing the data to send in the AJAX request.
                     */
                    data: (params) => {
                        return {
                            term: params.term,
                            page: params.page,
                            app_label: element.dataset.appLabel,
                            model_name: element.dataset.modelName,
                            field_name: element.dataset.fieldName
                        };
                    }
                }
            });
        });
        return this;
    };

    $(function() {
        /**
         * Initializes the Select2 widgets for all elements with the class
         * `admin-autocomplete`, excluding those in formset templates (which
         * contain `__prefix__` in their name attribute).
         */
        $('.admin-autocomplete').not('[name*=__prefix__]').djangoAdminSelect2();
    });

    document.addEventListener('formset:added', (event) => {
        /**
         * Reinitializes Select2 widgets for dynamically added formsets.
         *
         * When a new formset is added, this function finds all `admin-autocomplete`
         * elements within the formset and applies the `djangoAdminSelect2` method.
         *
         * @param {Event} event - The event object triggered by the addition of a new formset.
         */
        $(event.target).find('.admin-autocomplete').djangoAdminSelect2();
    });
}
