'use strict';
{
    /**
     * Initializes prepopulated fields for Django's admin interface.
     */
    const $ = django.jQuery;

    // Retrieve prepopulated field constants from the DOM.
    const fields = $('#django-admin-prepopulated-fields-constants').data('prepopulatedFields');

    /**
     * Iterates through each prepopulated field and applies necessary configurations.
     * @param {number} index - The index of the current field in the array.
     * @param {Object} field - The prepopulated field object containing its properties.
     */
    $.each(fields, function(index, field) {
        $(
            '.empty-form .form-row .field-' + field.name +
            ', .empty-form.form-row .field-' + field.name +
            ', .empty-form .form-row.field-' + field.name
        ).addClass('prepopulated_field'); // Add the 'prepopulated_field' class to empty form fields.

        // Apply prepopulation logic to the field.
        $(field.id).data('dependency_list', field.dependency_list).prepopulate(
            field.dependency_ids, field.maxLength, field.allowUnicode
        );
    });
}
