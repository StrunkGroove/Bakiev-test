import uuid

from odoo import models, fields, api


class Products(models.Model):
    _name = 'add_product.add_product'
    _description = 'Добавление товара'

    name = fields.Char(string='Название')
    description = fields.Text(string='Описание')

    _sql_constraints = [
        ('unique_name_description', 'unique(name, description)',
         'Комбинация Названия и Описания должна быть уникальной!'),
    ]
    

class MarksProducts(models.Model):
    _name = 'add_product.mark_products'
    _description = 'Маркированные товары'

    unique_id = fields.Char(
        string='Идентификатор товара', unique=True, readonly=True
    )
    costs = fields.Many2many(
        'add_product.costs_product', string='Затраты/Приходы', readonly=True
    )
    summ = fields.Float(
        string='Прибыль', compute='_compute_summ', store=True, readonly=True
    )
    products = fields.Many2one(
        'add_product.add_product', string='Товар', readonly=True
    )
    stock = fields.Many2one(
        'add_product.stocks', string='Последний назначенный склад',
        readonly=True
    )
    status = fields.Many2one(
        'add_product.status', string='Последний назначенный статус',
        readonly=True
        )

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.products.name} # {record.unique_id}"
            result.append((record.id, name))
        return result
    
    @api.depends('costs.price')
    def _compute_summ(self):
        for record in self:
            record.summ = sum(record.costs.mapped('price'))

    @api.model
    def create(self, values):
        values['unique_id'] = str(uuid.uuid4())[:18]
        return super(MarksProducts, self).create(values)