/** @odoo-module **/

import { registry } from "@web/core/registry";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { AttachmentKanbanRecord } from "./attachment_preview";

export class AttachmentKanbanRenderer extends KanbanRenderer {
    static components = {
        ...KanbanRenderer.components,
        KanbanRecord: AttachmentKanbanRecord,
    };
}

registry.category("views").add("attachment_kanban_renderer", {
    type: "kanban",
    display_name: "Attachment Kanban",
    icon: "fa fa-folder",
    multiRecord: true,
    Renderer: AttachmentKanbanRenderer,
    Controller: KanbanController,
});
