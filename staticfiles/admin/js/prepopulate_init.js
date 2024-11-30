'use strict';
{
    const $ = django.jQuery;

    /**
     * Initializes prepopulated fields in Django admin.
     *
     * - Adds the `prepopulated_field` class to fields in empty forms.
     * - Configures the prepopulated field to update its value based on dependencies.
     */
    const fields = $('#django-admin-prepopulated-fields-constants').data('prepopulatedFields');
    $.each(fields, function(index, field) {
        $(
            '.empty-form .form-row .field-' + field.name +
            ', .empty-form.form-row .field-' + field.name +
            ', .empty-form .form-row.field-' + field.name
        ).addClass('prepopulated_field');
        $(field.id).data('dependency_list', field.dependency_list).prepopulate(
            field.dependency_ids, field.maxLength, field.allowUnicode
        );
    });
}
