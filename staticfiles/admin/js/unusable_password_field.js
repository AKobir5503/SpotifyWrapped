"use strict";
// Fallback JS for browsers which do not support :has selector used in
// admin/css/unusable_password_fields.css
// Remove file once all supported browsers support :has selector

try {
    // If browser does not support :has selector this will raise an error
    document.querySelector("form:has(input)");
} catch (error) {
    console.log("Defaulting to javascript for usable password form management: " + error);

    /**
     * Handles the change event for the "usable_password" input field.
     * This function updates the visibility of password fields, warning messages, and submit buttons
     * based on the checked state of the "usable_password" checkbox.
     *
     * @listens change
     */
    document.querySelectorAll('input[name="usable_password"]').forEach(option => {
        option.addEventListener('change', function() {
            /**
             * Determines whether the password fields should be visible.
             * If the "usable_password" checkbox is checked (true), password fields are shown.
             * Otherwise, they are hidden.
             *
             * @type {boolean}
             */
            const usablePassword = (this.value === "true" ? this.checked : !this.checked);

            // Get references to submit buttons and the warning message
            const submit1 = document.querySelector('input[type="submit"].set-password');
            const submit2 = document.querySelector('input[type="submit"].unset-password');
            const messages = document.querySelector('#id_unusable_warning');

            // Toggle visibility of password fields based on usablePassword value
            document.getElementById('id_password1').closest('.form-row').hidden = !usablePassword;
            document.getElementById('id_password2').closest('.form-row').hidden = !usablePassword;

            // Toggle the visibility of the warning messages
            if (messages) {
                messages.hidden = usablePassword;
            }

            // Toggle visibility of submit buttons based on usablePassword value
            if (submit1 && submit2) {
                submit1.hidden = !usablePassword;
                submit2.hidden = usablePassword;
            }
        });

        // Trigger the 'change' event initially to set the correct state based on the initial form value
        option.dispatchEvent(new Event('change'));
    });
}
