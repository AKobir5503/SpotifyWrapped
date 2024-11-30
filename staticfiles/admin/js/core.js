// Core JavaScript helper functions
'use strict';

/**
 * Creates a new HTML element, optionally adds text content, and sets attributes.
 *
 * @param {string} tagType - The type of HTML element to create (e.g., 'div', 'span').
 * @param {HTMLElement} parentReference - The parent element to which the new element will be appended.
 * @param {string} [textInChildNode] - Optional text content for the new element.
 * @param {...(string|number)} [attribute, attributeValue] - Pairs of attribute names and values to set on the new element.
 * @returns {HTMLElement} The created and appended HTML element.
 */
function quickElement() {
    const obj = document.createElement(arguments[0]);
    if (arguments[2]) {
        const textNode = document.createTextNode(arguments[2]);
        obj.appendChild(textNode);
    }
    const len = arguments.length;
    for (let i = 3; i < len; i += 2) {
        obj.setAttribute(arguments[i], arguments[i + 1]);
    }
    arguments[1].appendChild(obj);
    return obj;
}

/**
 * Removes all child elements from the specified element.
 *
 * @param {HTMLElement} a - The element from which all child nodes will be removed.
 */
function removeChildren(a) {
    while (a.hasChildNodes()) {
        a.removeChild(a.lastChild);
    }
}

/**
 * Finds the X (horizontal) position of an element relative to the document.
 *
 * @param {HTMLElement} obj - The element for which to find the X position.
 * @returns {number} The X position in pixels.
 */
function findPosX(obj) {
    let curleft = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curleft += obj.offsetLeft - obj.scrollLeft;
            obj = obj.offsetParent;
        }
    } else if (obj.x) {
        curleft += obj.x;
    }
    return curleft;
}

/**
 * Finds the Y (vertical) position of an element relative to the document.
 *
 * @param {HTMLElement} obj - The element for which to find the Y position.
 * @returns {number} The Y position in pixels.
 */
function findPosY(obj) {
    let curtop = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curtop += obj.offsetTop - obj.scrollTop;
            obj = obj.offsetParent;
        }
    } else if (obj.y) {
        curtop += obj.y;
    }
    return curtop;
}

// ----------------------------------------------------------------------------
// Date object extensions
// ----------------------------------------------------------------------------

/**
 * @returns {number} The hour in 12-hour format (1-12).
 */
Date.prototype.getTwelveHours = function() {
    return this.getHours() % 12 || 12;
};

/**
 * @returns {string} The two-digit representation of the month (e.g., '01' for January).
 */
Date.prototype.getTwoDigitMonth = function() {
    return (this.getMonth() < 9) ? '0' + (this.getMonth() + 1) : (this.getMonth() + 1);
};

/**
 * @returns {string} The two-digit representation of the date (e.g., '01' for the first of the month).
 */
Date.prototype.getTwoDigitDate = function() {
    return (this.getDate() < 10) ? '0' + this.getDate() : this.getDate();
};

/**
 * @returns {string} The two-digit representation of the hour in 12-hour format.
 */
Date.prototype.getTwoDigitTwelveHour = function() {
    return (this.getTwelveHours() < 10) ? '0' + this.getTwelveHours() : this.getTwelveHours();
};

/**
 * @returns {string} The two-digit representation of the hour in 24-hour format.
 */
Date.prototype.getTwoDigitHour = function() {
    return (this.getHours() < 10) ? '0' + this.getHours() : this.getHours();
};

/**
 * @returns {string} The two-digit representation of the minute.
 */
Date.prototype.getTwoDigitMinute = function() {
    return (this.getMinutes() < 10) ? '0' + this.getMinutes() : this.getMinutes();
};

/**
 * @returns {string} The two-digit representation of the second.
 */
Date.prototype.getTwoDigitSecond = function() {
    return (this.getSeconds() < 10) ? '0' + this.getSeconds() : this.getSeconds();
};

/**
 * @returns {string} The abbreviated day name (e.g., 'Sun', 'Mon').
 */
Date.prototype.getAbbrevDayName = function() {
    return typeof window.CalendarNamespace === "undefined"
        ? '0' + this.getDay()
        : window.CalendarNamespace.daysOfWeekAbbrev[this.getDay()];
};

/**
 * @returns {string} The full day name (e.g., 'Sunday', 'Monday').
 */
Date.prototype.getFullDayName = function() {
    return typeof window.CalendarNamespace === "undefined"
        ? '0' + this.getDay()
        : window.CalendarNamespace.daysOfWeek[this.getDay()];
};

/**
 * @returns {string} The abbreviated month name (e.g., 'Jan', 'Feb').
 */
Date.prototype.getAbbrevMonthName = function() {
    return typeof window.CalendarNamespace === "undefined"
        ? this.getTwoDigitMonth()
        : window.CalendarNamespace.monthsOfYearAbbrev[this.getMonth()];
};

/**
 * @returns {string} The full month name (e.g., 'January', 'February').
 */
Date.prototype.getFullMonthName = function() {
    return typeof window.CalendarNamespace === "undefined"
        ? this.getTwoDigitMonth()
        : window.CalendarNamespace.monthsOfYear[this.getMonth()];
};

/**
 * Formats the date using a given format string.
 *
 * @param {string} format - The format string using placeholders (e.g., '%Y-%m-%d').
 * @returns {string} The formatted date string.
 */
Date.prototype.strftime = function(format) {
    const fields = {
        a: this.getAbbrevDayName(),
        A: this.getFullDayName(),
        b: this.getAbbrevMonthName(),
        B: this.getFullMonthName(),
        c: this.toString(),
        d: this.getTwoDigitDate(),
        H: this.getTwoDigitHour(),
        I: this.getTwoDigitTwelveHour(),
        m: this.getTwoDigitMonth(),
        M: this.getTwoDigitMinute(),
        p: (this.getHours() >= 12) ? 'PM' : 'AM',
        S: this.getTwoDigitSecond(),
        w: '0' + this.getDay(),
        x: this.toLocaleDateString(),
        X: this.toLocaleTimeString(),
        y: ('' + this.getFullYear()).substr(2, 4),
        Y: '' + this.getFullYear(),
        '%': '%'
    };
    let result = '', i = 0;
    while (i < format.length) {
        if (format.charAt(i) === '%') {
            result += fields[format.charAt(i + 1)];
            ++i;
        } else {
            result += format.charAt(i);
        }
        ++i;
    }
    return result;
};

// ----------------------------------------------------------------------------
// String object extensions
// ----------------------------------------------------------------------------

/**
 * Parses a date string according to a given format and returns a Date object.
 *
 * @param {string} format - The format string using placeholders (e.g., '%Y-%m-%d').
 * @returns {Date} The parsed date object.
 */
String.prototype.strptime = function(format) {
    const split_format = format.split(/[.\-/]/);
    const date = this.split(/[.\-/]/);
    let i = 0;
    let day, month, year;
    while (i < split_format.length) {
        switch (split_format[i]) {
            case "%d":
                day = date[i];
                break;
            case "%m":
                month = date[i] - 1;
                break;
            case "%Y":
                year = date[i];
                break;
            case "%y":
                if (parseInt(date[i], 10) >= 69) {
                    year = date[i];
                } else {
                    year = (new Date(Date.UTC(date[i], 0))).getUTCFullYear() + 100;
                }
                break;
        }
        ++i;
    }
    return new Date(Date.UTC(year, month, day));
};
