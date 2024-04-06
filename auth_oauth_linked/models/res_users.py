# Copyright 2024 Jason Vu   
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
from odoo import _, api, fields, models
from odoo.addons.base.models.res_users import check_identity
from odoo.exceptions import AccessDenied
import werkzeug.urls

class ResUsers(models.Model):
    _inherit = "res.users"

    #user have base oauth and oauth_linked_ids are sub oauths
    oauth_linked_ids = fields.One2many(
        comodel_name="auth.oauth.linked",
        inverse_name="user_id",
        string="Linked OAuth",
        copy=False,
        readonly=True,
    )
    
    def _return_url(self, url):
        return {'type':'ir.actions.act_url','url': url, 'target': 'self'}
    
    @api.model
    def link_oauth(self, provider, params):
        access_token = params.get('access_token')
        validation = super(ResUsers, self).sudo()._auth_oauth_validate(provider, access_token)
        
        res = self._auth_oauth_link(provider, validation, params)
        return res
    
    @api.model
    def _auth_oauth_link(self, provider, validation, params):        
        oauth_uid = validation['user_id']
        oauth_access_token = params['access_token']
        
        #check base oauth exist if yes double check sub oauths
        current_user = self.env['res.users'].browse(self.env.uid)
        base_oauth = current_user.oauth_provider_id
        sub_oauths = current_user.oauth_linked_ids
        if provider == base_oauth.id or provider in sub_oauths.mapped('oauth_provider_id.id'):
            return self._return_url("/my/security?link_oauth_error=3")
        
        #check provider & oauth_uid already exist
        oauth_user = self.env['res.users'].sudo().search([("oauth_uid", "=", oauth_uid), ("oauth_provider_id", "=", provider)])
        oauth_linked = self.env['auth.oauth.linked'].sudo().search([("oauth_uid", "=", oauth_uid), ("oauth_provider_id", "=", provider)])
        if oauth_user or oauth_linked:
            return self._return_url("/my/security?link_oauth_error=4")
        
        #if not base then link to base else link to sub
        if not base_oauth:
            current_user.sudo().write({
                'oauth_provider_id': provider,
                'oauth_uid': oauth_uid,
                'oauth_access_token': oauth_access_token
            })
        else:
            current_user.sudo().write({'oauth_linked_ids': [(0, 0, {'user_id': self.env.uid,
                                                      'oauth_provider_id': provider,
                                                      'oauth_uid': oauth_uid,
                                                      'oauth_access_token': oauth_access_token})]})
            
        return self._return_url("/my/security?link_oauth=1")
    
    @api.model
    def unlink_oauth(self, oauth_provider_id, oauth_uid, unlink):  
        try:
            if unlink == 'base':
                if self.oauth_provider_id.id == oauth_provider_id and self.oauth_uid == oauth_uid:
                    self.sudo().write({
                        'oauth_provider_id': False,
                        'oauth_uid': False,
                        'oauth_access_token': False,
                    })
                    return self._return_url("/my/security?link_oauth=1")
            elif unlink == 'sub':
                for oauth_linked_id in self.oauth_linked_ids:
                    if oauth_linked_id.oauth_provider_id.id == oauth_provider_id and oauth_linked_id.oauth_uid == oauth_uid:
                        oauth_linked_id.unlink()
                        return self._return_url("/my/security?link_oauth=1")
            return self._return_url("/my/security?link_oauth_error=1")
        except:
            return self._return_url("/my/security?link_oauth_error=1")

    @check_identity
    def action_link_oauth(self):
        """force check identity before link
        """
        if self.env.user != self:
            return self._return_url("/my/security?link_oauth_error=2")
        
        url=self.env.context.get('url')
        if not url:
            url="/"
        return self._return_url(url)
    
    @check_identity
    def action_unlink_oauth(self):
        """force check identity before unlink
        """
        if self.env.user != self:
            return self._return_url("/my/security?link_oauth_error=2")
        
        oauth = self.env.context.get('oauth')
        params = dict(
            oauth_provider_id = oauth.get('oauth_provider_id'),
            oauth_uid = oauth.get('oauth_uid'),
            unlink = oauth.get('unlink'),
        )
        url = "%s?%s" % ("/auth_oauth/unlink", werkzeug.urls.url_encode(params))
        return self._return_url(url)
        
    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        state = json.loads(params['state'])
        if state.get('l'):
            oauth_uid = validation['user_id']
            try:
                oauth_linked_user = self.env['auth.oauth.linked'].sudo().search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
                if not oauth_linked_user:
                    return super()._auth_oauth_signin(provider, validation, params)
                assert len(oauth_linked_user) == 1
                oauth_linked_user.write({'oauth_access_token': params['access_token']})
                oauth_user = self.browse(oauth_linked_user.user_id.id)
                return oauth_user.login
            except:
                return super()._auth_oauth_signin(provider, validation, params)
        else:
            return super()._auth_oauth_signin(provider, validation, params)
    
    def _check_credentials(self, password, env):
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            passwd_allowed = env['interactive'] or not self.env.user._rpc_api_keys_only()
            if passwd_allowed and self.env.user.active:
                res = self.env['auth.oauth.linked'].sudo().search([('user_id', '=', self.env.uid), ('oauth_access_token', '=', password)])
                if res:
                    return
            raise