'use strict';
{
    const SelectBox = {
        cache: {},

        /**
         * Initializes the SelectBox for a given HTML `select` element by caching its options.
         *
         * @param {string} id - The ID of the HTML `select` element.
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
         * Redisplays the `select` element based on its cached options.
         *
         * @param {string} id - The ID of the HTML `select` element.
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
         * Filters the options in the `select` element based on a search string.
         *
         * @param {string} id - The ID of the HTML `select` element.
         * @param {string} text - The search string to filter by.
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
         * Returns the count of hidden options in the `select` element.
         *
         * @param {string} id - The ID of the HTML `select` element.
         * @returns {number} The count of hidden options.
         */
        get_hidden_node_count: function(id) {
            const cache = SelectBox.cache[id] || [];
            return cache.filter(node => node.displayed === 0).length;
        },

        /**
         * Deletes an option from the cache.
         *
         * @param {string} id - The ID of the HTML `select` element.
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
         *
         * @param {string} id - The ID of the HTML `select` element.
         * @param {Object} option - The option object to add ({value, text, displayed}).
         */
        add_to_cache: function(id, option) {
            SelectBox.cache[id].push({value: option.value, text: option.text, displayed: 1});
        },

        /**
         * Checks if a value exists in the cache.
         *
         * @param {string} id - The ID of the HTML `select` element.
         * @param {string} value - The value to check for.
         * @returns {boolean} `true` if the value exists, otherwise `false`.
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
         * Moves selected options from one `select` element to another.
         *
         * @param {string} from - The ID of the source `select` element.
         * @param {string} to - The ID of the destination `select` element.
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
         * Moves all options from one `select` element to another.
         *
         * @param {string} from - The ID of the source `select` element.
         * @param {string} to - The ID of the destination `select` element.
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
         * Sorts the options in the cache alphabetically.
         *
         * @param {string} id - The ID of the HTML `select` element.
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
         * Selects all options in a `select` element.
         *
         * @param {string} id - The ID of the HTML `select` element.
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
