/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ImageSelector } from '@web_editor/components/media_dialog/image_selector';

patch(ImageSelector, {
    /**
     * Utility method used by the MediaDialog component.
     */
    async createElements(selectedMedia, {orm, rpc}) {
        const keep = document.getElementById('keep-external-cdn-image-url')
        if (keep.checked) {
            selectedMedia[0].image_src = selectedMedia[0].url
        }
        return await super.createElements(selectedMedia, {orm, rpc})
    }
})