# -*- coding: utf-8 -*-
# from odoo import http


# class VenpackInvoice(http.Controller):
#     @http.route('/venpack_invoice/venpack_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/venpack_invoice/venpack_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('venpack_invoice.listing', {
#             'root': '/venpack_invoice/venpack_invoice',
#             'objects': http.request.env['venpack_invoice.venpack_invoice'].search([]),
#         })

#     @http.route('/venpack_invoice/venpack_invoice/objects/<model("venpack_invoice.venpack_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('venpack_invoice.object', {
#             'object': obj
#         })
