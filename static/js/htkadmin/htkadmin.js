YUI({
    classNamePrefix: 'pure'
}).use(
    'node',
    'event',
    'gallery-sm-menu',
function (Y) {
    /* -------------------------------------------------- */
    /* YUI "Local" Globals */

    // CSS selectors
    var CSS_CLASS_MENU_CONTAINER = 'menu-container';
    var CSS_CLASS_HIDDEN = 'hidden';

    // Nodes
    var main = Y.one('#main');
    var menuContainer = Y.one('.' + CSS_CLASS_MENU_CONTAINER);

    // App variables

    /* End YUI "Local" Globals */
    /* -------------------------------------------------- */

    // Custom App Functions

    // App Initializers
    function initEventHandlers() {
    }

    function init() {
        var horizontalMenu = new Y.Menu({
            container         : '#horizontal_menu',
            sourceNode        : '#menu_items',
            orientation       : 'horizontal',
            hideOnOutsideClick: false,
            hideOnClick       : false
        });

        horizontalMenu.render();
        horizontalMenu.show();
        menuContainer.removeClass(CSS_CLASS_HIDDEN);
    }
    initEventHandlers();
    init();
});
