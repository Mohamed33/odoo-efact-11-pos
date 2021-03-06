# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from itertools import groupby

class SaleOrder(models.Model):
    _inherit = "sale.order"
    incluir_imagenes = fields.Boolean(string="Incluir Imágenes")

    @api.multi
    def order_lines_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        #print(list(groupby(self.order_line, lambda l: l.layout_category_id)))
        for category, lines in groupby(self.order_line, lambda l: l.layout_category_id):

            if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
                report_pages.append([])
            report_pages[-1].append({
                'parent':category.parent.name,
                'name': category and category.name or _('Uncategorized'),
                'subtotal': category and category.subtotal,
                'pagebreak': category and category.pagebreak,
                'lines': list(lines)
            })

        return report_pages




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        #name = product.name_get()[0][1]
        name = product.name
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        return result

class section(models.Model):
    _inherit = "sale.layout_category"
    parent = fields.Many2one("sale.layout_category",string="Sección Padre")

    @api.multi
    def name_get(self):
        records=[]
        for record in self:
            if record.parent:
                records.append((record.id,record.parent.name+"/"+record.name))
            else:
                records.append((record.id,record.name))
        return records


class ProductTemplate(models.Model):
    _inherit = "product.template"
    margen = fields.Float(string="% Márgen de Ganancia")

    @api.onchange("margen")
    def _compute_list_price(self):
        self.list_price= (1+self.margen/100)*self.standard_price

class ResCompany(models.Model):
    _inherit = "res.company"
    servicio=fields.Text("Descripción de Servicios - Cabecera de Informe")

class ProductTemplate(models.Model):
    _inherit = "product.template"
    modelo = fields.Char(string="Modelo")
    marca = fields.Char(string="Marca")

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            #return (d['id'], '[%s]'%(d.get('modelo',''))+" "+name)
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '[%s] %s' % (code, name)
            if d.get('modelo'):
                name = '[%s] %s' % (d.get('modelo'), name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []
        for product in self.sudo():
            # display only the attributes with multiple possible values on the template
            variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped(
                'attribute_id')
            variant = product.attribute_value_ids._variant_name(variable_attributes)

            name = variant and "%s (%s)" % (product.name, variant) or product.name

            sellers = []
            if partner_ids:
                sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
                if not sellers:
                    sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'modelo':product.modelo,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'modelo': product.modelo,
                    'default_code': product.default_code,
                }
                result.append(_name_get(mydict))
        return result