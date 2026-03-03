odoo.define('web_html_extender.wysiwyg', function (require) {
'use strict';

var Wysiwyg = require('web_editor.wysiwyg');
const {closestElement} = require('@web_editor/js/editor/odoo-editor/src/OdooEditor');
const Toolbar = require('web_editor.toolbar');
var rpc = require('web.rpc');

const HtmlWysiwyg = Wysiwyg.extend({
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    startEdition: async function () {
        const res = await this._super(...arguments);
        // Prevent selection change outside of snippets.
        this.$editable.on('mousedown', e => {
            if ($(e.target).is('.o_editable:empty') || e.target.querySelector('.o_editable')) {
                e.preventDefault();
            }
        });

        this.$editable[0].addEventListener("input", this.onInput.bind(this));
        this.snippetsMenuToolbar = this.toolbar;
        return res;
    },

    onInput: async function(ev) {

        let value = $(ev.target).find('p').text();
        const matches = [...value.matchAll(/\/(\w+)\//g)];
        if (!matches.length) return;

        const keywords = matches.map(m => m[1]);
        const result = await rpc.query({
            model: "mail.shortcode",
            method: "search_read",
            args: [[["source", "in", keywords]], ["source", "substitution"]],
            kwargs: {}
        });

        const map = {};
        result.forEach(item => {
            map[item.source] = item.substitution;
        });

        for (const match of matches) {
            const fullMatch = match[0];
            const keyword = match[1];
            if (map[keyword]) {
                value = value.replace(fullMatch, map[keyword]);
            }
        }
        debugger;
        // Replace HTML inside editable div
        $(ev.target).find('p').text(value);

    },

    toggleLinkTools(options = {}) {
        this._super({
            ...options,
            // Always open the dialog when the sidebar is folded.
            forceDialog: options.forceDialog || this.snippetsMenu.folded
        });
        if (this.snippetsMenu.folded) {
            // Hide toolbar and avoid it being re-displayed after getDeepRange.
            this.odooEditor.document.getSelection().collapseToEnd();
        }
    },


    /**
     * @override
     */
    openMediaDialog: function() {
        this._super(...arguments);
        // Opening the dialog in the outer document does not trigger the selectionChange
        // (that would normally hide the toolbar) in the iframe.
        if (this.snippetsMenu.folded) {
            this.odooEditor.toolbarHide();
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _getPowerboxOptions: function () {
        const options = this._super();
        const {commands} = options;
        const linkCommands = commands.filter(command => command.name === 'Link' || command.name === 'Button');
        for (const linkCommand of linkCommands) {
            // Remove the command if the selection is within a background-image.
            const superIsDisabled = linkCommand.isDisabled;
            linkCommand.isDisabled = () => {
                if (superIsDisabled && superIsDisabled()) {
                    return true;
                } else {
                    const selection = this.odooEditor.document.getSelection();
                    const range = selection.rangeCount && selection.getRangeAt(0);
                    return !!range && !!closestElement(range.startContainer, '[style*=background-image]');
                }
            }
        }
        return {...options, commands};
    },
    /**
     * @override
     */
     _updateEditorUI: function (e) {
        this._super(...arguments);
        // Hide the create-link button if the selection is within a
        // background-image.
        const selection = this.odooEditor.document.getSelection();
        const range = selection.rangeCount && selection.getRangeAt(0);
        const isWithinBackgroundImage = !!range && !!closestElement(range.startContainer, '[style*=background-image]');
        if (isWithinBackgroundImage) {
            this.toolbar.$el.find('#create-link').toggleClass('d-none', true);
        }
    },
    _getEditorOptions: function () {
        const options = this._super(...arguments);
        const finalOptions = { autoActivateContentEditable: false, ...options };
        return finalOptions;
    },
});

return HtmlWysiwyg;

});
