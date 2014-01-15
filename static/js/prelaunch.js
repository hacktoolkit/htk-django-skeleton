YUI().use('node', 'event', 'event-key', 'io', function (Y) {
    /* -------------------------------------------------- */
    /* YUI "Local" Globals */

    // CSS selectors
    var CSS_CLASS_INPUT_FILLED = 'input-filled';
    var CSS_CLASS_INPUT_BLANK = 'input-blank';
    var CSS_CLASS_INPUT_TYPING = 'input-typing';
    var CSS_CLASS_INPUT_ERROR = 'input-error';
    var CSS_CLASS_INPUT_VALID = 'input-valid';
    var CSS_ID_PRELAUNCH_SIGNUP = '#prelaunch_signup';
    var CSS_ID_PRELAUNCH_SIGNUP_FORM = CSS_ID_PRELAUNCH_SIGNUP + ' #prelaunch_signup_form';
    var CSS_ID_PRELAUNCH_EMAIL_FIELD = CSS_ID_PRELAUNCH_SIGNUP_FORM + ' #id_email';

    // Nodes
    var prelaunchEmailField;

    // App variables
    var emailIsValid = false;

    var PRELAUNCH_EMAIL_DEFAULT_TEXT = 'Please enter your email address';

    var VALID_EMAIL_REGEXP = new RegExp(/^([a-zA-Z0-9]{3,})(((\.|\-|\_)[a-zA-Z0-9]{2,})+)?@([a-z]{3,})(\-[a-z0-9]{3,})?(\.[a-z]{2,})+$/);

    /* End YUI "Local" Globals */
    /* -------------------------------------------------- */

    // Custom App Functions
    function resetPrelaunchEmailField(node) {
        if (!node) {
            node = Y.one(CSS_ID_PRELAUNCH_EMAIL_FIELD);
        }

        if (node) {
            node.set('value', PRELAUNCH_EMAIL_DEFAULT_TEXT);
            node.replaceClass(CSS_CLASS_INPUT_FILLED, CSS_CLASS_INPUT_BLANK);
        }
    }

    function validateEmail(email, node) {
	var matches = email.match(VALID_EMAIL_REGEXP);
	emailIsValid = matches;
        node.removeClass(CSS_CLASS_INPUT_TYPING);

	if (emailIsValid) {
	    node.replaceClass(CSS_CLASS_INPUT_ERROR, CSS_CLASS_INPUT_VALID);
	} else {
	    node.replaceClass(CSS_CLASS_INPUT_VALID, CSS_CLASS_INPUT_ERROR);
	}

	return emailIsValid;
    }

    function prelaunchEmailFieldFocused(e) {
        var value = this.get('value');
        this.addClass(CSS_CLASS_INPUT_TYPING);
        if (value === PRELAUNCH_EMAIL_DEFAULT_TEXT || !emailIsValid) {
            this.set('value', '');
            if (!emailIsValid) {
                this.removeClass(CSS_CLASS_INPUT_ERROR);
            }
        }
        this.replaceClass(CSS_CLASS_INPUT_BLANK, CSS_CLASS_INPUT_FILLED);
    }

    function prelaunchEmailFieldBlurred(e) {
        var email = this.get('value');
        this.removeClass(CSS_CLASS_INPUT_TYPING);
        if (email === '') {
            resetPrelaunchEmailField(this);
        } else {
            validateEmail(email, this);
        }
    }

    function prelaunchEmailFieldEnterKeyPressed(e) {
	e.halt();
	var email = this.get('value');
	var valid = validateEmail(email, this);
	submitEmail(e);
    }

    function submitEmail(e) {
        e.preventDefault();
        var form = Y.one(CSS_ID_PRELAUNCH_SIGNUP_FORM);
	var config = {
            method: 'POST',
	    form: {
                id: form,
		useDisabled: false
            }
	};

	if (emailIsValid) {
	    var uri = form.get('action');
	    var request = Y.io(uri, config);
	    Y.on('io:complete', handleEmailSubmitted, Y, {});
	}
    }

    function handleEmailSubmitted() {
	var message = "Thanks for signing up! We'll let you know when the site launches.";
	var container = Y.one(CSS_ID_PRELAUNCH_SIGNUP);
	container.setContent(message);
    }

    // App Initializers
    function initEventHandlers() {
        Y.delegate('focus', prelaunchEmailFieldFocused, CSS_ID_PRELAUNCH_EMAIL_FIELD);
        Y.delegate('blur', prelaunchEmailFieldBlurred, CSS_ID_PRELAUNCH_EMAIL_FIELD);

        // form submission
        Y.delegate('click', submitEmail, CSS_ID_PRELAUNCH_SIGNUP_FORM, 'button');
        Y.delegate('key', prelaunchEmailFieldEnterKeyPressed, CSS_ID_PRELAUNCH_SIGNUP_FORM, 'down:enter', 'input');
    }

    function init() {
        resetPrelaunchEmailField();
    }
    initEventHandlers();
    init();
});
