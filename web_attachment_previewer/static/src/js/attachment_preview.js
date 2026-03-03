/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import { patch } from "@web/core/utils/patch";
import { useState, useEnv } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


patch(KanbanRecord.prototype, {
    setup() {
        super.setup();

        // Only attach FileViewer if it's an attachment record
        if (this.props.list?._config?.resModel === "ir.attachment") {
            this.fileViewer = useFileViewer();
        }
        this.store = useState(useService("mail.store"));

    },

    onGlobalClick(ev) {
        // Only trigger if target has the preview class and props exist
        if (
            ev.target.closest(".o_kanban_previewer") &&
            this.props.list?._config?.resModel === "ir.attachment" &&
            this.props.record?.data
        ) {
            const record = this.props.record.data;
            const attachmentRecord = this.store.Attachment.insert({
				id: record.id,
				name: record.name,
				filename: record.name,
				mimetype: record.mimetype,
			});

			this.fileViewer.open(attachmentRecord);
            return;
        }
        // fallback to original behavior
        return super.onGlobalClick(ev);
    },
});
