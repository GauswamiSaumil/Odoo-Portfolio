/** @odoo-module **/

import { HtmlField, HtmlFieldWysiwygAdapterComponent } from "@web_editor/js/backend/html_field";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class HtmlCannedResponseField extends HtmlField {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.popup = null;
        this.suggestions = [];
        this.activeIndex = 0;
    }

    /*
        @Override:
        To bind the events to the triggered keys
        returns: None
    */

    async startWysiwyg(wysiwyg) {
        await super.startWysiwyg(wysiwyg);
        if (this.wysiwyg?.odooEditor?.editable) {
            this.wysiwyg.odooEditor.editable.addEventListener('keyup', this._onKeyUp.bind(this));
            this.wysiwyg.odooEditor.editable.addEventListener('keydown', this._onKeyDown.bind(this));
        }
    }

    /*
        @Event:
        Bind event on keyup
        returns: None
    */

    async _onKeyUp(ev) {
        if (ev.key === '*') {
            await this._showPopup(ev);
        } else if (this.popup) {
            if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp' || ev.key === 'Enter') {
                // handled in keydown
            } else {
                this._closePopup();
            }
        }
    }

    /*
        @Event:
        Bind event on keydown
        returns: None
    */

    _onKeyDown(ev) {
        if (!this.popup) return;
        if (ev.key === 'ArrowDown') {
            this.activeIndex = (this.activeIndex + 1) % this.suggestions.length;
            this._highlightSelection();
            ev.preventDefault();
        } else if (ev.key === 'ArrowUp') {
            this.activeIndex = (this.activeIndex - 1 + this.suggestions.length) % this.suggestions.length;
            this._highlightSelection();
            ev.preventDefault();
        } else if (ev.key === 'Enter') {
            this._insertSelected();
            ev.preventDefault();
        }
    }

    /*
        @Event:
        Showing suggestions of canned responses in popup
        returns: None
    */

    async _showPopup(ev) {
        const suggestions = await this.rpc("/web/dataset/call_kw/mail.shortcode/search_read", {
            model: "mail.shortcode",
            method: "search_read",
            args: [[], ["source", "substitution"]],
            kwargs: {},
        });
        console.log(suggestions)
        this.suggestions = suggestions;
        this.activeIndex = 0;

        this._renderPopup(ev);
    }

    /*
        @Render:
        Rendering popup
        returns: None
    */

    _renderPopup(ev) {
        this._closePopup();
        const popup = document.createElement("div");
        popup.style.position = "absolute";
        popup.style.background = "white";
        popup.style.border = "1px solid #ccc";
        popup.style.zIndex = 1100;
        popup.style.padding = "5px";
        popup.style.borderRadius = "5px";
        popup.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
        popup.style.minWidth = "150px";
        popup.style.fontSize = "14px";
        debugger;
        this.suggestions.forEach((sug, index) => {
            const div = document.createElement("div");
            div.textContent = sug.source;
            div.style.padding = "3px";
            div.style.cursor = "pointer";
            div.dataset.index = index;
            div.addEventListener('click', () => {
                this.activeIndex = index;
                this._insertSelected();
            });
            popup.appendChild(div);
        });

        document.body.appendChild(popup);
        this.popup = popup;
        this._highlightSelection();

        // Position popup
        const rect = this.wysiwyg.odooEditor.editable.getBoundingClientRect();
        popup.style.top = (rect.top + 30) + "px";
        popup.style.left = (rect.left + 10) + "px";
    }

    /*
        @Style:
        Styling popup
        returns: None
    */

    _highlightSelection() {
        if (!this.popup) return;
        [...this.popup.children].forEach((el, idx) => {
            el.style.background = (idx === this.activeIndex) ? "#eef" : "white";
        });
    }

    /*
        @Event:
        Add popup in the current visible body
        returns: None
    */

    _insertSelected() {
        const selected = this.suggestions[this.activeIndex];
        if (!selected) return;

        const editable = this.wysiwyg.odooEditor.editable;
        const selection = window.getSelection();
        if (selection.rangeCount) {
            const range = selection.getRangeAt(0);
            range.setStart(range.startContainer, range.startOffset - 1);
            range.deleteContents();
            const node = document.createTextNode(selected.substitution);
            range.insertNode(node);
            range.setStartAfter(node);
            range.setEndAfter(node);
            selection.removeAllRanges();
            selection.addRange(range);
        }

        this._closePopup();
        editable.focus();
    }

    /*
        @Event:
        Close popup
        returns: None
    */
    _closePopup() {
        if (this.popup) {
            this.popup.remove();
            this.popup = null;
        }
    }
}

registry.category("fields").add("html", HtmlCannedResponseField, { force: true });
