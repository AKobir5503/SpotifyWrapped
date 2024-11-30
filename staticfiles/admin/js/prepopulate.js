/*global URLify*/
'use strict';
{
    const $ = django.jQuery;

    /**
     * Populates a selected field with URLified and shortened values from dependent fields.
     *
     * @param {string[]} dependencies - Array of CSS selectors for the dependent fields.
     * @param {number} maxLength - Maximum length of the URLified string.
     * @param {boolean} allowUnicode - Whether to allow Unicode in the URLified string.
     * @returns {jQuery} The jQuery object for chaining.
     */
    $.fn.prepopulate = function(dependencies, maxLength, allowUnicode) {
        /*
            Depends on urlify.js
            Populates a selected field with the values of the dependent fields,
            URLifies and shortens the string.
            dependencies - array of dependent fields ids
            maxLength - maximum length of the URLify'd string
            allowUnicode - Unicode support of the URLify'd string
        */
        return this.each(function() {
            const prepopulatedField = $(this);

            /**
             * Populates the prepopulated field with a URLified string based on the dependent fields' values.
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

            prepopulatedField.data('_changed', false);

            prepopulatedField.on('change', function() {
                prepopulatedField.data('_changed', true);
            });

            if (!prepopulatedField.val()) {
                $(dependencies.join(',')).on('keyup change focus', populate);
            }
        });
    };
}
