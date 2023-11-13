from odoo import models, fields, api


class Stocks(models.Model):
    _name = 'add_product.stocks'
    _description = 'Склады'

    name = fields.Char(string='Название')

    _sql_constraints = [
            ('uniq_name', 'unique(name)', "Name must be unique!"),
        ]