# Copyright 2024 Jason Vu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

class AuthOauthLinked(models.Model):

    _name = "auth.oauth.linked"
    _description = "OAuth linked"
    
    oauth_provider_id = fields.Many2one('auth.oauth.provider', string='OAuth Provider')
    oauth_uid = fields.Char(string='OAuth User ID', help="Oauth Provider user_id", copy=False)
    oauth_access_token = fields.Char(string='OAuth Access Token', readonly=True, copy=False)

    _sql_constraints = [
        ('uniq_users_oauth_provider_oauth_uid', 'unique(oauth_provider_id, oauth_uid)', 'OAuth UID must be unique per provider'),
    ]
    
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    _sql_constraints = [
        ('uniq_users_oauth_provider', 'unique(user_id, oauth_uid)', 'User linked providers must be unique'),
    ]
    