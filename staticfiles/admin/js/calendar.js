'use strict';
{
    // CalendarNamespace -- Provides a collection of HTML calendar-related helper functions
    const CalendarNamespace = {
        /**
         * Determines if a given year is a leap year.
         * @param {number} year - The year to check.
         * @returns {boolean} True if the year is a leap year, false otherwise.
         */
        isLeapYear: function(year) {
            return (((year % 4) === 0) && ((year % 100) !== 0 ) || ((year % 400) === 0));
        },

        /**
         * Gets the number of days in a specific month of a specific year.
         * @param {number} month - The month (1-12).
         * @param {number} year - The year.
         * @returns {number} The number of days in the month.
         */
        getDaysInMonth: function(month, year) {
            let days;
            if (month === 1 || month === 3 || month === 5 || month === 7 || month === 8 || month === 10 || month === 12) {
                days = 31;
            } else if (month === 4 || month === 6 || month === 9 || month === 11) {
                days = 30;
            } else if (month === 2 && CalendarNamespace.isLeapYear(year)) {
                days = 29;
            } else {
                days = 28;
            }
            return days;
        },

        /**
         * Draws a calendar for a specific month and year in a given container.
         * @param {number} month - The month to draw (1-12).
         * @param {number} year - The year to draw.
         * @param {string} div_id - The ID of the container where the calendar will be drawn.
         * @param {function} callback - A callback function to execute when a day is clicked.
         * @param {Date} [selected] - The selected date to highlight, if any.
         */
        draw: function(month, year, div_id, callback, selected) {
            const today = new Date();
            const todayDay = today.getDate();
            const todayMonth = today.getMonth() + 1;
            const todayYear = today.getFullYear();
            let todayClass = '';

            let isSelectedMonth = false;
            if (typeof selected !== 'undefined') {
                isSelectedMonth = (selected.getUTCFullYear() === year && (selected.getUTCMonth() + 1) === month);
            }

            month = parseInt(month);
            year = parseInt(year);
            const calDiv = document.getElementById(div_id);
            removeChildren(calDiv);
            const calTable = document.createElement('table');
            quickElement('caption', calTable, CalendarNamespace.monthsOfYear[month - 1] + ' ' + year);
            const tableBody = quickElement('tbody', calTable);

            // Draw days-of-week header
            let tableRow = quickElement('tr', tableBody);
            for (let i = 0; i < 7; i++) {
                quickElement('th', tableRow, CalendarNamespace.daysOfWeekInitial[(i + CalendarNamespace.firstDayOfWeek) % 7]);
            }

            const startingPos = new Date(year, month - 1, 1 - CalendarNamespace.firstDayOfWeek).getDay();
            const days = CalendarNamespace.getDaysInMonth(month, year);

            let nonDayCell;

            // Draw blanks before first of month
            tableRow = quickElement('tr', tableBody);
            for (let i = 0; i < startingPos; i++) {
                nonDayCell = quickElement('td', tableRow, ' ');
                nonDayCell.className = "nonday";
            }

            function calendarMonth(y, m) {
                function onClick(e) {
                    e.preventDefault();
                    callback(y, m, this.textContent);
                }
                return onClick;
            }

            // Draw days of month
            let currentDay = 1;
            for (let i = startingPos; currentDay <= days; i++) {
                if (i % 7 === 0 && currentDay !== 1) {
                    tableRow = quickElement('tr', tableBody);
                }
                if ((currentDay === todayDay) && (month === todayMonth) && (year === todayYear)) {
                    todayClass = 'today';
                } else {
                    todayClass = '';
                }

                if (isSelectedMonth && currentDay === selected.getUTCDate()) {
                    if (todayClass !== '') {
                        todayClass += " ";
                    }
                    todayClass += "selected";
                }

                const cell = quickElement('td', tableRow, '', 'class', todayClass);
                const link = quickElement('a', cell, currentDay, 'href', '#');
                link.addEventListener('click', calendarMonth(year, month));
                currentDay++;
            }

            // Draw blanks after end of month (optional, but makes for valid code)
            while (tableRow.childNodes.length < 7) {
                nonDayCell = quickElement('td', tableRow, ' ');
                nonDayCell.className = "nonday";
            }

            calDiv.appendChild(calTable);
        }
    };

    /**
     * Creates a new calendar instance.
     * @class
     * @param {string} div_id - The ID of the container where the calendar will be drawn.
     * @param {function} callback - A callback function to execute when a day is clicked.
     * @param {Date} [selected] - The selected date to highlight, if any.
     */
    function Calendar(div_id, callback, selected) {
        this.div_id = div_id;
        this.callback = callback;
        this.today = new Date();
        this.currentMonth = this.today.getMonth() + 1;
        this.currentYear = this.today.getFullYear();
        if (typeof selected !== 'undefined') {
            this.selected = selected;
        }
    }
    Calendar.prototype = {
        /**
         * Draws the calendar for the currently selected month and year.
         */
        drawCurrent: function() {
            CalendarNamespace.draw(this.currentMonth, this.currentYear, this.div_id, this.callback, this.selected);
        },

        /**
         * Draws the calendar for a specific month and year.
         * @param {number} month - The month to draw (1-12).
         * @param {number} year - The year to draw.
         * @param {Date} [selected] - The selected date to highlight, if any.
         */
        drawDate: function(month, year, selected) {
            this.currentMonth = month;
            this.currentYear = year;
            if (selected) {
                this.selected = selected;
            }
            this.drawCurrent();
        },

        /**
         * Draws the calendar for the previous month.
         */
        drawPreviousMonth: function() {
            if (this.currentMonth === 1) {
                this.currentMonth = 12;
                this.currentYear--;
            } else {
                this.currentMonth--;
            }
            this.drawCurrent();
        },

        /**
         * Draws the calendar for the next month.
         */
        drawNextMonth: function() {
            if (this.currentMonth === 12) {
                this.currentMonth = 1;
                this.currentYear++;
            } else {
                this.currentMonth++;
            }
            this.drawCurrent();
        },

        /**
         * Draws the calendar for the previous year.
         */
        drawPreviousYear: function() {
            this.currentYear--;
            this.drawCurrent();
        },

        /**
         * Draws the calendar for the next year.
         */
        drawNextYear: function() {
            this.currentYear++;
            this.drawCurrent();
        }
    };

    window.Calendar = Calendar;
    window.CalendarNamespace = CalendarNamespace;
}
