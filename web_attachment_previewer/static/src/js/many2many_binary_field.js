/** @odoo-module **/

import { Many2ManyBinaryField } from "@web/views/fields/many2many_binary/many2many_binary_field";
import { patch } from "@web/core/utils/patch";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

patch(Many2ManyBinaryField.prototype, {
    setup() {
        super.setup();
        this.fileViewer = useFileViewer();
        this.store = useState(useService("mail.store"));
    },

    onPreview(file) {
        if (!file?.id) {
            return;
        }

        const attachment = this.store.Attachment.insert({
            id: file.id,
            name: file.name,
            filename: file.name,
            mimetype: file.mimetype,
        });

        this.fileViewer.open(attachment);
    },
});
