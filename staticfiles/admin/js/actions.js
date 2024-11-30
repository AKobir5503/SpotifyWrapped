/* global gettext, interpolate, ngettext, Actions */
'use strict';

{
    /**
     * Shows all elements matching the given selector.
     * @param {string} selector - CSS selector for the elements to show.
     */
    function show(selector) {
        document.querySelectorAll(selector).forEach(function (el) {
            el.classList.remove('hidden');
        });
    }

    /**
     * Hides all elements matching the given selector.
     * @param {string} selector - CSS selector for the elements to hide.
     */
    function hide(selector) {
        document.querySelectorAll(selector).forEach(function (el) {
            el.classList.add('hidden');
        });
    }

    /**
     * Shows the "question" section and hides other sections.
     * @param {Object} options - Configuration options for the operation.
     */
    function showQuestion(options) {
        hide(options.acrossClears);
        show(options.acrossQuestions);
        hide(options.allContainer);
    }

    /**
     * Shows the "clear" section and hides other sections.
     * @param {Object} options - Configuration options for the operation.
     */
    function showClear(options) {
        show(options.acrossClears);
        hide(options.acrossQuestions);
        document.querySelector(options.actionContainer).classList.remove(options.selectedClass);
        show(options.allContainer);
        hide(options.counterContainer);
    }

    /**
     * Resets the display to its default state.
     * @param {Object} options - Configuration options for the operation.
     */
    function reset(options) {
        hide(options.acrossClears);
        hide(options.acrossQuestions);
        hide(options.allContainer);
        show(options.counterContainer);
    }

    /**
     * Clears the "across" inputs and resets the display.
     * @param {Object} options - Configuration options for the operation.
     */
    function clearAcross(options) {
        reset(options);
        const acrossInputs = document.querySelectorAll(options.acrossInput);
        acrossInputs.forEach(function (acrossInput) {
            acrossInput.value = 0;
        });
        document.querySelector(options.actionContainer).classList.remove(options.selectedClass);
    }

    /**
     * Checks or unchecks action checkboxes and updates the display accordingly.
     * @param {NodeList} actionCheckboxes - List of action checkboxes.
     * @param {Object} options - Configuration options for the operation.
     * @param {boolean} checked - Whether the checkboxes should be checked.
     */
    function checker(actionCheckboxes, options, checked) {
        if (checked) {
            showQuestion(options);
        } else {
            reset(options);
        }
        actionCheckboxes.forEach(function (el) {
            el.checked = checked;
            el.closest('tr').classList.toggle(options.selectedClass, checked);
        });
    }

    /**
     * Updates the counter display based on the number of selected checkboxes.
     * @param {NodeList} actionCheckboxes - List of action checkboxes.
     * @param {Object} options - Configuration options for the operation.
     */
    function updateCounter(actionCheckboxes, options) {
        const sel = Array.from(actionCheckboxes).filter(function (el) {
            return el.checked;
        }).length;
        const counter = document.querySelector(options.counterContainer);

        // `data-actions-icnt` contains the total number of objects in the queryset
        const actions_icnt = Number(counter.dataset.actionsIcnt);
        counter.textContent = interpolate(
            ngettext('%(sel)s of %(cnt)s selected', '%(sel)s of %(cnt)s selected', sel), {
                sel: sel,
                cnt: actions_icnt,
            }, true
        );

        const allToggle = document.getElementById(options.allToggleId);
        allToggle.checked = sel === actionCheckboxes.length;

        if (allToggle.checked) {
            showQuestion(options);
        } else {
            clearAcross(options);
        }
    }

    /** Default configuration options. */
    const defaults = {
        actionContainer: "div.actions",
        counterContainer: "span.action-counter",
        allContainer: "div.actions span.all",
        acrossInput: "div.actions input.select-across",
        acrossQuestions: "div.actions span.question",
        acrossClears: "div.actions span.clear",
        allToggleId: "action-toggle",
        selectedClass: "selected",
    };

    /**
     * Initializes the Actions functionality for managing bulk actions.
     * @param {NodeList} actionCheckboxes - List of action checkboxes.
     * @param {Object} options - Configuration options for customization.
     */
    window.Actions = function (actionCheckboxes, options) {
        options = Object.assign({}, defaults, options);
        let list_editable_changed = false;
        let lastChecked = null;
        let shiftPressed = false;

        document.addEventListener('keydown', (event) => {
            shiftPressed = event.shiftKey;
        });

        document.addEventListener('keyup', (event) => {
            shiftPressed = event.shiftKey;
        });

        document.getElementById(options.allToggleId).addEventListener('click', function () {
            checker(actionCheckboxes, options, this.checked);
            updateCounter(actionCheckboxes, options);
        });

        document.querySelectorAll(options.acrossQuestions + " a").forEach(function (el) {
            el.addEventListener('click', function (event) {
                event.preventDefault();
                const acrossInputs = document.querySelectorAll(options.acrossInput);
                acrossInputs.forEach(function (acrossInput) {
                    acrossInput.value = 1;
                });
                showClear(options);
            });
        });

        document.querySelectorAll(options.acrossClears + " a").forEach(function (el) {
            el.addEventListener('click', function (event) {
                event.preventDefault();
                document.getElementById(options.allToggleId).checked = false;
                clearAcross(options);
                checker(actionCheckboxes, options, false);
                updateCounter(actionCheckboxes, options);
            });
        });

        /**
         * Identifies the checkboxes affected by a shift-click operation.
         * @param {HTMLElement} target - The checkbox that was clicked.
         * @param {boolean} withModifier - Whether the shift key was pressed.
         * @returns {HTMLElement[]} Array of affected checkboxes.
         */
        function affectedCheckboxes(target, withModifier) {
            const multiSelect = lastChecked && withModifier && lastChecked !== target;
            if (!multiSelect) {
                return [target];
            }
            const checkboxes = Array.from(actionCheckboxes);
            const targetIndex = checkboxes.findIndex((el) => el === target);
            const lastCheckedIndex = checkboxes.findIndex((el) => el === lastChecked);
            const startIndex = Math.min(targetIndex, lastCheckedIndex);
            const endIndex = Math.max(targetIndex, lastCheckedIndex);
            return checkboxes.filter((_, index) => startIndex <= index && index <= endIndex);
        }

        Array.from(document.getElementById('result_list').tBodies).forEach(function (el) {
            el.addEventListener('change', function (event) {
                const target = event.target;
                if (target.classList.contains('action-select')) {
                    const checkboxes = affectedCheckboxes(target, shiftPressed);
                    checker(checkboxes, options, target.checked);
                    updateCounter(actionCheckboxes, options);
                    lastChecked = target;
                } else {
                    list_editable_changed = true;
                }
            });
        });

        document.querySelector('#changelist-form button[name=index]').addEventListener('click', function (event) {
            if (list_editable_changed) {
                const confirmed = confirm(gettext("You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost."));
                if (!confirmed) {
                    event.preventDefault();
                }
            }
        });

        const el = document.querySelector('#changelist-form input[name=_save]');
        if (el) {
            el.addEventListener('click', function (event) {
                if (document.querySelector('[name=action]').value) {
                    const text = list_editable_changed
                        ? gettext("You have selected an action, but you haven’t saved your changes to individual fields yet. Please click OK to save. You’ll need to re-run the action.")
                        : gettext("You have selected an action, and you haven’t made any changes on individual fields. You’re probably looking for the Go button rather than the Save button.");
                    if (!confirm(text)) {
                        event.preventDefault();
                    }
                }
            });
        }

        window.addEventListener('pageshow', () => updateCounter(actionCheckboxes, options));
    };

    /**
     * Executes the given function when the DOM is fully loaded.
     * @param {Function} fn - The function to execute.
     */
    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    ready(function () {
        const actionsEls = document.querySelectorAll('tr input.action-select');
        if (actionsEls.length > 0) {
            Actions(actionsEls);
        }
    });
}
