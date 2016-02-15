# -*- coding: utf-8 -*-
from openerp import http

# class HrExtension(http.Controller):
#     @http.route('/hr_extension/hr_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_extension/hr_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_extension.listing', {
#             'root': '/hr_extension/hr_extension',
#             'objects': http.request.env['hr_extension.hr_extension'].search([]),
#         })

#     @http.route('/hr_extension/hr_extension/objects/<model("hr_extension.hr_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_extension.object', {
#             'object': obj
#         })