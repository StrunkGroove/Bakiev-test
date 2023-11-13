from odoo import models, fields, api


class Status(models.Model):
    _name = 'add_product.status'
    _description = 'Статусы'

    name = fields.Char(string='Статус')

    _sql_constraints = [
            ('uniq_name', 'unique(name)', "Status must be unique!"),
        ]