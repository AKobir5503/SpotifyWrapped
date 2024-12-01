'use strict';
{
    const SelectBox = {
        cache: {},

        /**
         * Initializes the SelectBox for a given element ID and caches its options.
         * @param {string} id - The ID of the select element to initialize.
         */
        init: function(id) {
            const box = document.getElementById(id);
            SelectBox.cache[id] = [];
            const cache = SelectBox.cache[id];
            for (const node of box.options) {
                cache.push({value: node.value, text: node.text, displayed: 1});
            }
        },

        /**
         * Repopulates the HTML select box from the cache.
         * @param {string} id - The ID of the select element to redisplay.
         */
        redisplay: function(id) {
            const box = document.getElementById(id);
            const scroll_value_from_top = box.scrollTop;
            box.innerHTML = '';
            for (const node of SelectBox.cache[id]) {
                if (node.displayed) {
                    const new_option = new Option(node.text, node.value, false, false);
                    new_option.title = node.text;
                    box.appendChild(new_option);
                }
            }
            box.scrollTop = scroll_value_from_top;
        },

        /**
         * Filters the options in the select box based on a given search text.
         * @param {string} id - The ID of the select element to filter.
         * @param {string} text - The search text to filter options by.
         */
        filter: function(id, text) {
            const tokens = text.toLowerCase().split(/\s+/);
            for (const node of SelectBox.cache[id]) {
                node.displayed = 1;
                const node_text = node.text.toLowerCase();
                for (const token of tokens) {
                    if (!node_text.includes(token)) {
                        node.displayed = 0;
                        break;
                    }
                }
            }
            SelectBox.redisplay(id);
        },

        /**
         * Gets the count of hidden options in the select box.
         * @param {string} id - The ID of the select element.
         * @returns {number} The number of hidden options.
         */
        get_hidden_node_count(id) {
            const cache = SelectBox.cache[id] || [];
            return cache.filter(node => node.displayed === 0).length;
        },

        /**
         * Deletes an option from the cache by its value.
         * @param {string} id - The ID of the select element.
         * @param {string} value - The value of the option to delete.
         */
        delete_from_cache: function(id, value) {
            let delete_index = null;
            const cache = SelectBox.cache[id];
            for (const [i, node] of cache.entries()) {
                if (node.value === value) {
                    delete_index = i;
                    break;
                }
            }
            cache.splice(delete_index, 1);
        },

        /**
         * Adds an option to the cache.
         * @param {string} id - The ID of the select element.
         * @param {Object} option - The option to add, with `value` and `text` properties.
         */
        add_to_cache: function(id, option) {
            SelectBox.cache[id].push({value: option.value, text: option.text, displayed: 1});
        },

        /**
         * Checks if the cache contains an option with the specified value.
         * @param {string} id - The ID of the select element.
         * @param {string} value - The value to check for.
         * @returns {boolean} True if the value exists in the cache, otherwise false.
         */
        cache_contains: function(id, value) {
            for (const node of SelectBox.cache[id]) {
                if (node.value === value) {
                    return true;
                }
            }
            return false;
        },

        /**
         * Moves selected options from one select element to another.
         * @param {string} from - The ID of the source select element.
         * @param {string} to - The ID of the target select element.
         */
        move: function(from, to) {
            const from_box = document.getElementById(from);
            for (const option of from_box.options) {
                const option_value = option.value;
                if (option.selected && SelectBox.cache_contains(from, option_value)) {
                    SelectBox.add_to_cache(to, {value: option_value, text: option.text, displayed: 1});
                    SelectBox.delete_from_cache(from, option_value);
                }
            }
            SelectBox.redisplay(from);
            SelectBox.redisplay(to);
        },

        /**
         * Moves all options from one select element to another.
         * @param {string} from - The ID of the source select element.
         * @param {string} to - The ID of the target select element.
         */
        move_all: function(from, to) {
            const from_box = document.getElementById(from);
            for (const option of from_box.options) {
                const option_value = option.value;
                if (SelectBox.cache_contains(from, option_value)) {
                    SelectBox.add_to_cache(to, {value: option_value, text: option.text, displayed: 1});
                    SelectBox.delete_from_cache(from, option_value);
                }
            }
            SelectBox.redisplay(from);
            SelectBox.redisplay(to);
        },

        /**
         * Sorts the options in the select box alphabetically.
         * @param {string} id - The ID of the select element to sort.
         */
        sort: function(id) {
            SelectBox.cache[id].sort(function(a, b) {
                a = a.text.toLowerCase();
                b = b.text.toLowerCase();
                if (a > b) {
                    return 1;
                }
                if (a < b) {
                    return -1;
                }
                return 0;
            });
        },

        /**
         * Selects all options in the select box.
         * @param {string} id - The ID of the select element.
         */
        select_all: function(id) {
            const box = document.getElementById(id);
            for (const option of box.options) {
                option.selected = true;
            }
        }
    };

    window.SelectBox = SelectBox;
}
