/*global URLify*/
'use strict';
{
    const $ = django.jQuery;

    /**
     * jQuery plugin to prepopulate a field based on dependent fields.
     *
     * Populates a selected field with the values of the dependent fields, URLifies
     * and shortens the string.
     *
     * @param {Array<string>} dependencies - Array of dependent field IDs.
     * @param {number} maxLength - Maximum length of the URLify'd string.
     * @param {boolean} allowUnicode - Whether to allow Unicode characters in the URLify'd string.
     * @returns {jQuery} The jQuery object for chaining.
     */
    $.fn.prepopulate = function(dependencies, maxLength, allowUnicode) {
        return this.each(function() {
            const prepopulatedField = $(this);

            /**
             * Populates the prepopulated field with a URLified string based on dependencies.
             */
            const populate = function() {
                // Bail if the field's value has been changed by the user
                if (prepopulatedField.data('_changed')) {
                    return;
                }

                const values = [];
                $.each(dependencies, function(i, field) {
                    field = $(field);
                    if (field.val().length > 0) {
                        values.push(field.val());
                    }
                });
                prepopulatedField.val(URLify(values.join(' '), maxLength, allowUnicode));
            };

            // Initialize the field's change tracking
            prepopulatedField.data('_changed', false);
            prepopulatedField.on('change', function() {
                prepopulatedField.data('_changed', true);
            });

            // Attach event listeners to dependencies if the field is empty
            if (!prepopulatedField.val()) {
                $(dependencies.join(',')).on('keyup change focus', populate);
            }
        });
    };
}
