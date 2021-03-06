from odoo import http
from odoo.http import request


class GoogleMapAPI(http.Controller):

    @http.route("/get_api_key_google_map",type="json",auth="user",methods=["POST"])
    def get_api_key_google_map(self):
        api_key = request.env["ir.config_paramenter"].search([("key","=","API_KEY_GOOGLE_MAP")])
        if api_key.exists():
            return {"API_KEY":api_key.value}
        else:
            return {"API_KEY":False}