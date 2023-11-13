from odoo import models, fields, api, exceptions


class CostsProducts(models.Model):
    _name = 'add_product.costs_product'
    _description = 'Затраты/Приходы'

    timestamp = fields.Date(
        string='Дата', default=fields.Date.today, readonly=True
    )
    name = fields.Char(string='Затраты/Приходы', required=True)
    price = fields.Float(string='Значение', required=True)


class CostsDone(models.Model):
    _name = 'add_product.costs_done'
    _description = 'Затраты/Приходы'

    name = fields.Char(string='Затраты/Приходы', required=True)
    price = fields.Float(string='Значение', required=True)


class CostsName(models.Model):
    _name = 'add_product.cost_name'
    _description = 'Затраты/Приходы'

    name = fields.Char(
        string='Наименование', required=True, unique=True
    )

class Costs(models.Model):
    _name = 'add_product.cost_type'
    _description = 'Затраты/Приходы'

    name = fields.Many2one('add_product.cost_name', string='Наименование Затрат/Приходов', required=True)
    price = fields.Float(string='Значение', default=0)
    base_act_id = fields.Many2one('add_product.act_actions', string='Базовый акт')


class BaseAct(models.AbstractModel):
    _name = 'add_product.base_act'
    _description = 'Базовый акт'

    num_products = fields.Integer(string='Количество')
    # costs = fields.Many2many('add_product.cost_type', string='Затраты/Приходы')
    summ = fields.Float(string='Сумма', compute='_compute_summ', store=True)
    status = fields.Many2one('add_product.status', string='Назначаемый статус')
    from_stock = fields.Many2one(
        'add_product.stocks', string='Применить для товаров со склада', 
        required=False
    )
    to_stock = fields.Many2one(
        'add_product.stocks', string='Назначить новый склад'
    )
    products = fields.Many2one('add_product.add_product', string='Продукт')

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.products.name}"
            result.append((record.id, name))
        return result
    
    @api.depends('costs')
    def _compute_summ(self):
        for record in self:
            record.summ = sum(record.costs.mapped('price'))


class DoneAct(models.Model):
    _name = 'add_product.done_act'
    _description = 'Акты изменения свойств товаров'

    num_products = fields.Integer(string='Количество', readonly=True)

    @api.constrains('num_products')
    def check_num_products_positive(self):
        for record in self:
            if record.num_products <= 0:
                raise exceptions.ValidationError("Количество должно быть больше 0.")

    costs = fields.Many2many(
        'add_product.costs_done', string='Затраты/Приходы', readonly=True
    )
    summ = fields.Float(
        string='Сумма', compute='_compute_summ', store=True, readonly=True
    )
    status = fields.Many2one(
        'add_product.status', string='Назначаемый статус', readonly=True
    )
    from_stock = fields.Many2one(
        'add_product.stocks', string='Применить для товаров со склада',
        required=False, readonly=True
    )
    to_stock = fields.Many2one(
        'add_product.stocks', string='Назначить новый склад', readonly=True
    )
    products = fields.Many2one(
        'add_product.add_product', string='Продукт', readonly=True
    )
    number = fields.Integer(
        string='Номер', compute='_compute_count', store=True, readonly=True,
        unique=True
    )
    timestamp = fields.Date(
        string='Дата', default=fields.Date.today, readonly=True
    )

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.products.name}, АКТ № {record.number}"
            result.append((record.id, name))
        return result

    @api.depends('costs')
    def _compute_summ(self):
        for record in self:
            record.summ = sum(record.costs.mapped('price'))

    @api.depends('create_uid')
    def _compute_count(self):
        for record in self:
            number = self.env['add_product.done_act'].search_count([]) + 1
            record.number = str(number).zfill(4)
            

class Act(models.Model):
    _name = 'add_product.act_actions'
    _description = 'Шаблоны актов'
    _inherit = 'add_product.base_act'

    costs = fields.One2many('add_product.cost_type', 'base_act_id', string='Затраты/Приходы', copy=True)
    
    def create_actions_done(self, costs: list) -> list:
        actions = [
            self.env['add_product.costs_done'].create({
                'name': cost.name.name,
                'price': cost.price,
            }) for cost in costs
        ]
        return actions
    
    def create_actions(self, costs: list, num_products: int) -> list:
        actions = [
            self.env['add_product.costs_product'].create({
                'name': cost.name.name,
                'price': cost.price / num_products,
            }) for cost in costs
        ]
        return actions

    def link_costs(self, actions: list) -> list:
        return [(4, cost.id) for cost in actions]
    
    def select_records(self, mark_products, product_id: int, 
                       from_stock: str, num_products: int) -> list:
        products = mark_products.search([
            ('products', '=', product_id),
            ('stock', '=', from_stock),
            ('status.name', '!=', 'Продажа')
        ], limit=num_products)
        return products
    
    def apply_product(self) -> bool:
        mark_products = self.env['add_product.mark_products']
        record_id = self.id
        act_action = self.env['add_product.act_actions'].search([('id', '=', record_id)])

        num_products = act_action.num_products
        product_id = act_action.products.id
        from_stock = act_action.from_stock.id
        to_stock = act_action.to_stock.id
        costs = act_action.costs
        status_name = act_action.status.name
        status_id = act_action.status.id
        summ = act_action.summ
        
        actions_done = self.create_actions_done(costs)
        self.env['add_product.done_act'].create({
            'num_products': num_products,
            'products': product_id,
            'from_stock': from_stock,
            'to_stock': to_stock,
            'costs': self.link_costs(actions_done),
            'status': status_id,
            'summ': summ,
        })
        
        actions = self.create_actions(costs, num_products)

        if status_name == 'Покупка':
            for i in range(num_products):
                mark_products.create({
                    'products': product_id,
                    'stock': to_stock,
                    'status': status_id,
                    'costs': self.link_costs(actions)
                })
            return True

        products = self.select_records(mark_products, product_id, 
                                        from_stock, num_products)

        if not from_stock:
            raise exceptions.ValidationError(
                f"Поле 'Применить для товаров со склада' обязательно к заполнению при выборе статуса: 'Продажа' или 'Внутреннее перемещение'!"
            )
        
        if len(products) != num_products:
            raise exceptions.ValidationError(
                f'Количество продуктов превышает максимально возможное: {len(products)}!'
            )
        
        if status_name == 'Внутреннее перемещение':
            for product in products:
                product.write({
                    'stock': to_stock,
                    'status': status_id,
                    'costs': self.link_costs(actions)
                })

        elif status_name == 'Продажа':
            for product in products:
                product.write({
                    'status': status_id,
                    'costs': self.link_costs(actions)
                })
            
        return True