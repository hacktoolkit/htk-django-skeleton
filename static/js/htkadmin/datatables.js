YUI().use(
    'node',
    'event',
    'datatable',
function (Y) {
    /* -------------------------------------------------- */
    /* YUI "Local" Globals */

    // CSS selectors

    // Nodes
    var main = Y.one('#main');

    // App variables

    /* End YUI "Local" Globals */
    /* -------------------------------------------------- */

    // Custom App Functions
    function renderDatatables() {
        for (var i=0; i < datatables.length; ++i) {
            var datatable = datatables[i];
            var table = new Y.DataTable({
                columns: datatable.columns,
                data: datatable.data
            });
            table.render(datatable.container);
            table.show();
        }
    }

    // App Initializers
    function initEventHandlers() {
    }

    function init() {
        renderDatatables();
    }
    initEventHandlers();
    init();
});
