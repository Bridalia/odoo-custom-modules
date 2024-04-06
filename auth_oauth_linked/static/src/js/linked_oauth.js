/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { handleCheckIdentity } from "@portal/js/portal_security";
import publicWidget from "@web/legacy/js/public/public_widget";
import { session } from "@web/session";


publicWidget.registry.LinkedOAuthButton = publicWidget.Widget.extend({
    selector: '.linked_oauth',
    events: {
        click: '_onClick',
    },

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
        this.dialog = this.bindService("dialog");
        
    },

    async _onClick(e) {
        e.preventDefault();
        
        const w = await handleCheckIdentity(
            this.orm.call("res.users", "action_link_oauth", [session.user_id], {context: {'url': e.target.value}}),
            this.orm,
            this.dialog
        );
        if (!w) {
            location.reload();
        }
        else {
            window.location = w.url;
        }
    },
});

publicWidget.registry.UnlinkedOAuthButton = publicWidget.Widget.extend({
    selector: '.unlink_oauth',
    events: {
        click: '_onClick',
    },

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
        this.dialog = this.bindService("dialog");
    },

    async _onClick(e) {
        e.preventDefault();

        const w = await handleCheckIdentity(
            this.orm.call("res.users", "action_unlink_oauth", [session.user_id], {context: {'oauth': JSON.parse(e.target.value.replace(/'/g, '"'))}}),
            this.orm,
            this.dialog
        );
        if (!w) {
            location.reload();
        }
        else {
            window.location = w.url;
        }
    },
});