from odoo.tests.common import TransactionCase


class TestKardexListGenerate(TransactionCase):
    at_install = True
    post_install =True

    def test_kardex(self):
        # record = self.env['model.a'].create({'field': 'value'})
        self.env["product.product"].create({
            "name":"Producto 123",
            "type":"product"
        })

        self.env["stock.loction"].create({})
        self.assertEqual(True,True)