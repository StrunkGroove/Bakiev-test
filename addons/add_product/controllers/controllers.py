# -*- coding: utf-8 -*-
from odoo import http


class AddProduct(http.Controller):
    @http.route('/add_product/add_product', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/add_product/add_product/objects', auth='public')
    def list(self, **kw):
        return http.request.render('add_product.listing', {
            'root': '/add_product/add_product',
            'objects': http.request.env['add_product.add_product'].search([]),
        })

    @http.route('/add_product/add_product/objects/<model("add_product.add_product"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('add_product.object', {
            'object': obj
        })
