import logging
from odoo.http import request
from odoo import api, http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.auth_oauth.controllers.main import OAuthLogin, fragment_to_query_string
from odoo.addons.web.controllers.utils import ensure_db
import json
import werkzeug.urls
import werkzeug.utils

_logger = logging.getLogger(__name__)

class OAuthsLogin(OAuthLogin):
    def get_state(self, provider):
        res = super().get_state(provider)
        res['l'] = 1
        return res

class LinkedOAuthPortalController(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        res = super()._prepare_portal_layout_values()
        
        try:
            linked_providers = []
            if request.env.user.oauth_provider_id:
                linked_providers.append(request.env.user.oauth_provider_id.id)
            if request.env.user.oauth_linked_ids:
                for oauth_linked_id in request.env.user.oauth_linked_ids:
                    linked_providers.append(oauth_linked_id.oauth_provider_id.id)
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True),('id', 'not in', linked_providers)])
        except Exception:
            providers = []
        for provider in providers:
            return_url = request.httprequest.url_root + 'auth_oauth/link'
            state = OAuthLogin.get_state(self, provider)
            state['l'] = 1
            state['u'] = request.env.user.id
            params = dict(
                response_type='token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state),
            )
            provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.urls.url_encode(params))
        res['providers'] = providers
        
        allow_unlink = request.env['ir.config_parameter'].sudo().get_param('base_setup.allow_portal_unlink_oauth', False)     
        res['allow_unlink'] = allow_unlink   
        
        link_oauth_msg = request.params.get('link_oauth')
        link_oauth_error_msg = request.params.get('link_oauth_error')
        if link_oauth_msg:
            res['link_oauth'] = (_("Success!"))
        if link_oauth_error_msg:
            if link_oauth_error_msg == '1':
                res['link_oauth_error'] = (_("Fail to link/unlink OAuth!"))
            elif link_oauth_error_msg == '2':
                res['link_oauth_error'] = (_("OAuth can only be link/unlink for yourself!"))
            elif link_oauth_error_msg == '3':
                res['link_oauth_error'] = (_("This OAuth already linked!"))
            elif link_oauth_error_msg == '4':
                res['link_oauth_error'] = (_("This OAuth already used by an other account!"))
            else:
                res['link_oauth_error'] = (_("Fail!"))
        return res
    
    def _return_url(self, url):
        redirect = request.redirect(url, 303)
        redirect.autocorrect_location_header = False
        return redirect
    
    @http.route('/auth_oauth/link', type='http', auth='none')
    @fragment_to_query_string
    def link_oauth(self, **kw):        
        state = json.loads(kw['state'])
        dbname = state.get('d')
        u_id = state.get('u')
        provider = state['p']
        is_link_oauth = state.get('l')
        if not http.db_filter([dbname]):
            return self._return_url("/my/security?link_oauth_error=1")
        ensure_db(db=dbname)
        
        if not is_link_oauth:
            return self._return_url("/my/security?link_oauth_error=1")
        
        #make sure update current user        
        if u_id != request.env.context.get('uid'):
            return self._return_url("/my/security?link_oauth_error=2")
        
        try:
            current_user = request.env['res.users'].browse(u_id)
            res = current_user.with_user(u_id).link_oauth(provider, kw)
            request.env.cr.commit()
            
            # update session token so the user does not get logged out (cache cleared by passwd change)
            request.env.user = current_user
            new_token = request.env.user._compute_session_token(request.session.sid)
            request.session.session_token = new_token
            
            return self._return_url(res.get('url'))
        except:
            return self._return_url("/my/security?link_oauth_error=1")
        
    @http.route('/auth_oauth/unlink', type='http', auth='user', csrf=False)
    @fragment_to_query_string
    def unlink_oauth(self, **kw):
        allow_unlink = request.env['ir.config_parameter'].sudo().get_param('base_setup.allow_portal_unlink_oauth', False)     
        if not allow_unlink:
            return self._return_url("/my/security?link_oauth_error=1")
        
        oauth_provider_id = int(kw['oauth_provider_id'])
        oauth_uid = kw['oauth_uid']
        unlink = kw['unlink']
        
        try:
            res = request.env.user.unlink_oauth(oauth_provider_id, oauth_uid, unlink)
            request.env.cr.commit()
            
            # update session token so the user does not get logged out (cache cleared by passwd change)
            new_token = request.env.user._compute_session_token(request.session.sid)
            request.session.session_token = new_token
            
            return self._return_url(res.get('url'))
        except:
            return self._return_url("/my/security?link_oauth_error=1")
        