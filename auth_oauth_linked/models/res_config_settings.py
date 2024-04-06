from odoo import fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_portal_unlink_oauth = fields.Boolean(
        string='Allow portal users to unlink their OAuths',
        config_parameter='base_setup.allow_portal_unlink_oauth',        
        default=False,
    )
    