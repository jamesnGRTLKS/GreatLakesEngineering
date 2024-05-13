from odoo.tests.common import TransactionCase
from odoo.tests import tagged, Form


@tagged('post_install')
class TestAlternativeMoProducts(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAlternativeMoProducts, cls).setUpClass()

        # Category
        cls.category = cls.env['product.category'].create({
            'name': 'Category'
        })

        # Products
        Product = cls.env['product.product']

        cls.product_a = Product.create({
            'name': 'Product A',
            'categ_id': cls.category.id,
            'detailed_type': 'product',
            'tracking': 'none'
        })

        cls.product_b = Product.create({
            'name': 'Product B',
            'categ_id': cls.category.id,
            'detailed_type': 'product',
            'tracking': 'none'
        })

        cls.product_c = Product.create({
            'name': 'Product C',
            'categ_id': cls.category.id,
            'detailed_type': 'product',
            'tracking': 'none'
        })

        # Stock Location
        cls.stock_location = cls.env['stock.location'].create({
            'name': 'Stock Location',
            'usage': 'inventory'
        })

        # Add Quantity
        cls.add_quantity = cls.env['stock.change.product.qty'].create({
            'product_tmpl_id': cls.product_c.product_tmpl_id.id,
            'product_id': cls.product_c.id,
            'new_quantity': 500,
        })

        # Alternative Product Line
        cls.AlternativeProductLine = cls.env['alternative.product.line']

        # Mrp Bill of Materials
        cls.MrpBom = cls.env['mrp.bom']

        # Mrp Production
        cls.MrpProduction = cls.env['mrp.production']

    # Checking product creation
    def test_product_creation(self):
        self.assertTrue(self.product_a.name == 'Product A', "'Product A' wasn't created.")
        self.assertTrue(self.product_b.name == 'Product B', "'Product B' wasn't created.")
        self.assertTrue(self.product_c.name == 'Product C', "'Product C' wasn't created.")

    def test_alternative_mo_products(self):
        # Checking if it changes stock quantity
        self.add_quantity.change_product_qty()

        self.assertTrue(self.product_c.stock_quant_ids, "Stock quantity of 'product_c' wasn't updated.")

        # Checking if it adds an alternative product
        product_b_alternative = self.AlternativeProductLine.create({
            'product_id': self.product_b.id,
            'alternative_product_id': self.product_c.id
        })

        self.assertTrue(self.product_b.alternative_line_ids, "'Product B' alternative wasn't created.")

        # Checking if it adds a bom to the product from the form view
        product_a_bom = Form(self.MrpBom)
        product_a_bom.product_tmpl_id = self.product_a.product_tmpl_id
        product_a_bom.product_qty = 1
        bom_b = product_a_bom.save()

        with Form(bom_b) as bom:
            with bom.bom_line_ids.new() as line:
                line.product_id = self.product_b
                line.product_qty = 1

        self.assertEqual(product_a_bom.product_id, bom_b.product_id, "Creation of bom wasn't successful.")

        # Checking manufacturing order creation
        production_a = self.MrpProduction.create({
            'product_id': self.product_a.id,
            'product_qty': 10,
            'product_uom_id': 1,
        })

        production_a._onchange_product_id()
        production_a._onchange_move_raw()

        self.assertEqual(production_a.state, 'draft', "Manufacturing Order wasn't created.")

        # Checking manufacturing order confirmation
        production_a.action_confirm()
        production_a.move_raw_ids._action_assign()

        self.assertEqual(production_a.state, 'confirmed', "Manufacturing Order wasn't confirmed.")

        # Checking if product_b has 0 quantity
        filter_production_to_find_b = production_a.move_raw_ids.filtered(lambda ml: ml.product_id == self.product_b)

        self.assertEqual(filter_production_to_find_b.product_qty, 0, "'Product B' quantity was changed and it isn't 0.")

        # Checking if manufacturing order has product alternatives
        filter_production_to_find_c = production_a.move_raw_ids.filtered(lambda ml: ml.product_id == self.product_c)

        self.assertTrue(filter_production_to_find_c, "Manufacturing Order doesn't have any product alternatives.")
