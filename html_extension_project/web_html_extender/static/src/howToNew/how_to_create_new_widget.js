/** @odoo-module **/

//import { HtmlField, HtmlFieldWysiwygAdapterComponent } from "@web_editor/js/backend/html_field";
//import { _lt } from "@web/core/l10n/translation";
//import { standardFieldProps } from "@web/views/fields/standard_field_props";
//import { Component, useEffect, useRef, onMounted, onWillUpdateProps, onWillStart, useSubEnv } from "@odoo/owl";
//import { useBus, useService } from "@web/core/utils/hooks";
//import { QWebPlugin } from '@web_editor/js/backend/QWebPlugin';
//import { OdooEditor } from "@web_editor/js/editor/odoo-editor/src/OdooEditor";
//import { getWysiwygClass } from 'web_editor.loader';
//import { ComponentAdapter } from 'web.OwlCompatibility';
//import { TranslationButton } from "@web/views/fields/translation_button";
//import legacyEnv from 'web.commonEnv';
//import { stripHistoryIds } from '@web_editor/js/backend/html_field';
//
//
//import { registry } from "@web/core/registry";
//
//
//export class HtmlFieldCannedWysiwygAdapterComponent extends ComponentAdapter {
//    setup() {
//        super.setup();
//        useSubEnv(legacyEnv);
//
//        let started = false;
//        onMounted(() => {
//            if (!started) {
//                this.props.startWysiwyg(this.widget);
//                started = true;
//            }
//        });
//    }
//
//    updateWidget(newProps) {
//        const lastValue = String(this.props.widgetArgs[0].value || '');
//        const lastRecordInfo = this.props.widgetArgs[0].recordInfo;
//        const lastCollaborationChannel = this.props.widgetArgs[0].collaborationChannel;
//        const newValue = String(newProps.widgetArgs[0].value || '');
//        const newRecordInfo = newProps.widgetArgs[0].recordInfo;
//        const newCollaborationChannel = newProps.widgetArgs[0].collaborationChannel;
//
//        if (
//            (
//                stripHistoryIds(newValue) !== stripHistoryIds(newProps.editingValue) &&
//                stripHistoryIds(lastValue) !== stripHistoryIds(newValue)
//            ) ||
//            !_.isEqual(lastRecordInfo, newRecordInfo) ||
//            !_.isEqual(lastCollaborationChannel, newCollaborationChannel))
//        {
//            this.widget.resetEditor(newValue, newProps.widgetArgs[0]);
//            this.env.onWysiwygReset && this.env.onWysiwygReset();
//        }
//    }
//    renderWidget() {}
//
//    async onInput(ev) {
//        super.onInput?.();
//        debugger;
//    }
//}
//
//export class HtmlCannedResponseField extends HtmlField {
//    setup() {
//        super.setup();
//
//        useSubEnv({
//            onWysiwygReset: this._resetIframe.bind(this),
//        });
//        this.action = useService('action');
//        this.rpc = useService('rpc');
//        this.dialog = useService('dialog');
//
//    }
//
//    get wysiwygOptions() {
//        return {
//            ...super.wysiwygOptions,
//            onIframeUpdated: () => this.onIframeUpdated(),
//            onWysiwygBlur: () => {
//                this.commitChanges();
//                this.wysiwyg.odooEditor.toolbarHide();
//            },
//            ...this.props.wysiwygOptions,
//        };
//    }
//
//    async _getWysiwygClass() {
//        return getWysiwygClass({moduleName: 'web_html_extender.wysiwyg'});
//    }
//
//    async startWysiwyg(...args) {
//        await super.startWysiwyg(...args);
//        await this._resetIframe();
//    }
//
//    async _resetIframe() {
//        this.wysiwyg.getEditable().find('img').attr('loading', '');
//
//        this.wysiwyg.odooEditor.observerFlush();
//        this.wysiwyg.odooEditor.historyReset();
//
//        this.onIframeUpdated();
//    }
//
//    onIframeUpdated() {
//        const editable = this.wysiwyg?.$iframeBody?.find(".note-editable")?.get(0);
//        if (editable) {
//            editable.addEventListener("keyup", this.onInput.bind(this));
//        }
//    }
//
//    async onInput(ev) {
//        super.onInput?.();
//        let value = $(ev.target).val()
//        const matches = [...value.matchAll(/\/(\w+)\//g)];
//        if (!matches.length) return;
//
//        const keywords = matches.map(m => m[1]);
//        const result = await this.rpc("/web/dataset/call_kw/mail.shortcode/search_read", {
//            model: "mail.shortcode",
//            method: "search_read",
//            args: [[["source", "in", keywords]], ["source", "substitution"]],
//            kwargs: {}
//        });
//
//        const map = {};
//        result.forEach(item => {
//            map[item.source] = item.substitution;
//        });
//
//        for (const match of matches) {
//            const fullMatch = match[0];
//            const keyword = match[1];
//            if (map[keyword]) {
//                value = value.replace(fullMatch, map[keyword]);
//            }
//        }
//
//        // Replace HTML inside editable div
//        $(ev.target).val(value);
//
//        // Optional: trigger update
//        this.props.update(value);
//    }
//}
//
//
//
//HtmlCannedResponseField.template = "web_editor.HtmlField";
//HtmlCannedResponseField.props = {
//    ...HtmlField.props,
//    ...standardFieldProps
//};
////HtmlCannedResponseField.extractProps = ({ attrs, field }) => {
////    const wysiwygOptions = {
////        placeholder: attrs.placeholder,
////        noAttachment: attrs.options['no-attachment'],
////        inIframe: Boolean(attrs.options.cssEdit),
////        iframeCssAssets: attrs.options.cssEdit,
////        iframeHtmlClass: attrs.iframeHtmlClass,
////        snippets: attrs.options.snippets,
////        mediaModalParams: {
////            noVideos: 'noVideos' in attrs.options ? attrs.options.noVideos : true,
////            useMediaLibrary: true,
////        },
////        linkForceNewWindow: true,
////        tabsize: 0,
////        height: attrs.options.height,
////        minHeight: attrs.options.minHeight,
////        maxHeight: attrs.options.maxHeight,
////        resizable: 'resizable' in attrs.options ? attrs.options.resizable : false,
////        editorPlugins: [QWebPlugin],
////    };
////    if ('collaborative' in attrs.options) {
////        wysiwygOptions.collaborative = attrs.options.collaborative;
////    }
////    if ('style-inline' in attrs.options) {
////        wysiwygOptions.inlineStyle = Boolean(attrs.options['style-inline']);
////    }
////    if ('allowCommandImage' in attrs.options) {
////        // Set the option only if it is explicitly set in the view so a default
////        // can be set elsewhere otherwise.
////        wysiwygOptions.allowCommandImage = Boolean(attrs.options.allowCommandImage);
////    }
////    if (field.sanitize_tags || (field.sanitize_tags === undefined && field.sanitize)) {
////        wysiwygOptions.allowCommandVideo = false; // Tag-sanitized fields remove videos.
////    } else if ('allowCommandVideo' in attrs.options) {
////        // Set the option only if it is explicitly set in the view so a default
////        // can be set elsewhere otherwise.
////        wysiwygOptions.allowCommandVideo = Boolean(attrs.options.allowCommandVideo);
////    }
////    return {
////        isTranslatable: field.translate,
////        fieldName: field.name,
////        codeview: Boolean(odoo.debug && attrs.options.codeview),
////        sandboxedPreview: Boolean(attrs.options.sandboxedPreview),
////        placeholder: attrs.placeholder,
////
////        isCollaborative: attrs.options.collaborative,
////        cssReadonlyAssetId: attrs.options.cssReadonly,
////        dynamicPlaceholder: attrs.options.dynamic_placeholder,
////        cssEditAssetId: attrs.options.cssEdit,
////        isInlineStyle: attrs.options['style-inline'],
////        wrapper: attrs.options.wrapper,
////
////        wysiwygOptions,
////    };
////};
//HtmlCannedResponseField.extractProps = (...args) => {
//    const [{ attrs }] = args;
//    const htmlProps = HtmlField.extractProps(...args);
//    return {
//        ...htmlProps,
//    };
//};
//
//HtmlCannedResponseField.supportedTypes = ["html"];
//HtmlCannedResponseField.displayName = _lt("HTML with Snippets");
//HtmlCannedResponseField.components = {
//    TranslationButton,
//    HtmlFieldCannedWysiwygAdapterComponent
//}
//HtmlCannedResponseField.template = "web_html_extender.HtmlField";
//
//registry.category("fields").add("html_canned_response", HtmlCannedResponseField);
