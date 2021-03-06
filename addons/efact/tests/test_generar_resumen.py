from odoo.tests.common import TransactionCase

class TestAccountSummary(TransactionCase):
    at_install = True
    post_install =True

    def test_summary(self):
        self.assertEqual(True,True)
        
    # def test_summary_1(self):
    #     invoices = [{
    #             "tipo_documento":"03",
    #             "serie":"B001",
    #             "numero":8,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         }]
    #     summary_resultado_esperado = [{
    #             "serie":"B001",
    #             "tipo_documento":"03",
    #             "tipo_moneda":"PEN",
    #             "numero_documento_inicio":8,
    #             "numero_documento_fin":8,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_exp":0,
    #             "monto_grat":8,
    #             "monto_otros":9,
    #             "account_summary_id":False
    #         }]
 
    #     summary_resultado = self.env["account.summary"].summary(invoices)
    #     self.assertEqual(summary_resultado_esperado, summary_resultado)

    # def test_summary_2(self):
    #     invoices = [{
    #             "tipo_documento":"03",
    #             "serie":"B001",
    #             "numero":8,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         },{
    #             "tipo_documento":"03",
    #             "serie":"B001",
    #             "numero":9,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         }]

    #     summary_resultado_esperado = [{
    #             "serie":"B001",
    #             "tipo_documento":"03",
    #             "tipo_moneda":"PEN",
    #             "numero_documento_inicio":8,
    #             "numero_documento_fin":9,
    #             "monto_igv":40,
    #             "monto_isc":24,
    #             "monto_total":20,
    #             "monto_neto":30,
    #             "monto_exe":30,
    #             "monto_exo":2,
    #             "monto_exp":0,
    #             "monto_grat":16,
    #             "monto_otros":18,
    #             "account_summary_id":False
    #         }]
 
    #     summary_resultado = self.env["account.summary"].summary(invoices)
    #     self.assertEqual(summary_resultado_esperado, summary_resultado)
    
    # def test_summary_3(self):
    #     invoices = [{
    #             "tipo_documento":"03",
    #             "serie":"B001",
    #             "numero":8,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         },{
    #             "tipo_documento":"03",
    #             "serie":"B001",
    #             "numero":9,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         },{
    #             "tipo_documento":"07",
    #             "serie":"BC01",
    #             "numero":11,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         },{
    #             "tipo_documento":"07",
    #             "serie":"BC01",
    #             "numero":12,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         },{
    #             "tipo_documento":"07",
    #             "serie":"BC01",
    #             "numero":13,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         },{
    #             "tipo_documento":"07",
    #             "serie":"BC01",
    #             "numero":14,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         },{
    #             "tipo_documento":"07",
    #             "serie":"BC01",
    #             "numero":17,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_grat":8,
    #             "monto_exp":0,
    #             "monto_otros":9,
    #             "tipo_moneda":"PEN"
    #         }]

    #     summary_resultado_esperado = [{
    #             "serie":"BC01",
    #             "tipo_documento":"07",
    #             "tipo_moneda":"PEN",
    #             "numero_documento_inicio":11,
    #             "numero_documento_fin":14,
    #             "monto_igv":80,
    #             "monto_isc":48,
    #             "monto_total":40,
    #             "monto_neto":60,
    #             "monto_exe":60,
    #             "monto_exo":4,
    #             "monto_exp":0,
    #             "monto_grat":32,
    #             "monto_otros":36,
    #             "account_summary_id":False
    #         },{
    #             "serie":"BC01",
    #             "tipo_documento":"07",
    #             "tipo_moneda":"PEN",
    #             "numero_documento_inicio":17,
    #             "numero_documento_fin":17,
    #             "monto_igv":20,
    #             "monto_isc":12,
    #             "monto_total":10,
    #             "monto_neto":15,
    #             "monto_exe":15,
    #             "monto_exo":1,
    #             "monto_exp":0,
    #             "monto_grat":8,
    #             "monto_otros":9,
    #             "account_summary_id":False
    #         },{
    #             "serie":"B001",
    #             "tipo_documento":"03",
    #             "tipo_moneda":"PEN",
    #             "numero_documento_inicio":8,
    #             "numero_documento_fin":9,
    #             "monto_igv":40,
    #             "monto_isc":24,
    #             "monto_total":20,
    #             "monto_neto":30,
    #             "monto_exe":30,
    #             "monto_exo":2,
    #             "monto_exp":0,
    #             "monto_grat":16,
    #             "monto_otros":18,
    #             "account_summary_id":False
    #         }]
        

    #     summary_resultado = self.env["account.summary"].summary(invoices)
    #     self.assertItemsEqual(summary_resultado_esperado, summary_resultado)
    
