# -*- coding: utf-8 -*-
import re
import csv
import io
import logging
import base64
from odoo import fields, models, api, _
import os
_logger = logging.getLogger(__name__)
import json
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id


class import_products(models.TransientModel):
    _name = "import.products"
   
    file_path = fields.Binary(type='binary', string="File To Import")

    def _read_csv_data(self, binary_data):
        """
            Reads CSV from given path and Return list of dict with Mapping
        """
        data = csv.reader(StringIO(base64.b64decode(self.file_path).decode('utf-8')), quotechar='"', delimiter=',')

        # Read the column names from the first line of the file
        fields = next(data)
        data_lines = []
        for row in data:
            items = dict(zip(fields, row))
            data_lines.append(items)
        return fields, data_lines

    def do_import_product_data(self):
        file_path = self.file_path
        if not file_path or file_path == "":
            _logger.warning("Import can not be started. Configure your schedule Actions.")
            return True
        fields = data_lines = False

        try:
            fields, data_lines = self._read_csv_data(file_path)
        except:
            _logger.warning("Can not read source file(csv) '%s', Invalid file path or File not reachable on file system."%(file_path))
            return True
        if not data_lines:
            _logger.info("File '%s' has no data or it has been already imported, please update the file."%(file_path))
            return True
        _logger.info("Starting Import Product Process from file '%s'."%(file_path))
        #product_tmpl_obj = self.env['product.template']
        #product_attribute = self.env['product.attribute']

        bounced_cust = [tuple(fields)]
        error_lst=[]
        

        rem_product_tmpl_desc = []
        duplicate_product_template = []


        variant_list = []
        stock_move_line_list = []
        stock_inventory_obj = self.env['stock.inventory']
        location_id = stock_inventory_obj._default_location_id()

        record = 0
        for data in data_lines:
            product_tmpl_obj = self.env['product.template']
            product_attribute = self.env['product.attribute']
            product_tmpl_id = False
            # Product
            name = data['Name']
            categ_id = data['Product Category'] # Internal Category
            default_code = data['Internal Reference'] # Internal Reference
            color = data['Color'] # Color
            size = data['Size'] # Size
            list_price = data['Sale price'] # Sales price
            barcode = data['EAN'] # Barcode
            quantity = data['Stock'] # Stock
            standard_price = data['Costo'] # Stock

            # Remove extra spaces
            name = name.strip()
            categ_id = categ_id.strip()
            color = color.strip()
            size = size.strip()
            default_code = default_code.strip()
            barcode = barcode.strip()

            ir_model_data_obj = self.env['ir.model.data']
            product_category_obj = self.env['product.category']
            attribute_value_obj = self.env['product.attribute.value']
    
            try:
                internal_categ_id = False
                if data['Product Category']:
                    internal_categ_id = product_category_obj.search([('name', '=', categ_id)])
                    if not internal_categ_id:
                        internal_categ_id = product_category_obj.create({'name': categ_id})
                else:
                    internal_categ_id = product_category_obj.search([('name', '=', 'All')])
                    if not internal_categ_id:
                        internal_categ_id = product_category_obj.create({'name': 'All'})
                
                # Product Attributes get
                attribute_color_id = product_attribute.search([('name', '=', 'Color')])
                if not attribute_color_id:
                    attribute_color_id = product_attribute.create({'name': 'Color'})

                attribute_size_id = product_attribute.search([('name', '=', 'Size')])
                if not attribute_size_id:
                    attribute_size_id = product_attribute.create({'name': 'Size'})

                attribute_color_value_id_lis = []
                attribute_color_value_id = False
                if color:
                    for cl in color.split('*'):
                        attribute_color_value_id = attribute_value_obj.search([('name', '=', cl), ('attribute_id', '=', attribute_color_id.id)])
                        if attribute_color_value_id:
                            attribute_color_value_id_lis.append(attribute_color_value_id.id)
                        else:
                            attribute_color_value_id = attribute_value_obj.create({'attribute_id': attribute_color_id.id, 'name': cl})
                            attribute_color_value_id_lis.append(attribute_color_value_id.id)
                            
                attribute_size_value_id_lis = []
                attribute_size_value_id = False
                if size:
                    for sz in size.split('*'):
                        attribute_size_value_id = attribute_value_obj.search([('name', '=', sz), ('attribute_id', '=', attribute_size_id.id)])
                        if attribute_size_value_id:
                            attribute_size_value_id_lis.append(attribute_size_value_id.id)
                        else:
                            attribute_size_value_id = attribute_value_obj.create({'attribute_id': attribute_size_id.id, 'name': sz})
                            attribute_size_value_id_lis.append(attribute_size_value_id.id)
                
                attribute_value_list = []
                if attribute_color_value_id:
                    attribute_value_list.append([0, 0, {'attribute_id': attribute_color_id.id, 'value_ids': [(6,0, attribute_color_value_id_lis)]}])
                if attribute_size_value_id:
                    attribute_value_list.append([0, 0, {'attribute_id': attribute_size_id.id, 'value_ids': [(6,0, attribute_size_value_id_lis)]}])

                os.system("echo '%s'"%("default_code "+str(default_code)))  
                exist_product_template = product_tmpl_obj.search([('name', '=', name)])
                
                # product_barcode = False
                # if barcode:
                #     product_barcode = self.env['product.product'].search([('barcode', '=', barcode)])
                #     if not product_barcode:
                #         barcode_search = '0' + str(barcode)
                #         product_barcode = self.env['product.product'].search([('barcode', '=', barcode_search)])

                """
                if len(exist_product_template.ids) != 1:
                    for dup in exist_product_template:
                        duplicate_product_template.append({'default_code': dup.default_code})
                    exist_product_template_test = product_tmpl_obj.search([('barcode', '=', barcode)])
                    if not exist_product_template_test and exist_product_template:
                        exist_product_template = exist_product_template[0]
                    else:
                        exist_product_template = exist_product_template_test
                """

                os.system("echo '%s'"%("cantidad de productos "+str(len(exist_product_template.ids))))  
                if exist_product_template:
                    # os.system("echo '%s'"%("el producto existe: "+exist_product_template.name))
                    # os.system("echo '%s'"%("atributo "+json.dumps(exist_product_template.attribute_line_ids.ids)))
                    # os.system("echo '%s'"%("nombre atributo "+attribute_color_id.name))
                    exist_product_template.standard_price = standard_price
                    exist_product_template.list_price = list_price

                    exist_color_line = False
                    if attribute_color_id and color:
                        exist_color_line = exist_product_template.attribute_line_ids.filtered(lambda a: a.attribute_id.id == attribute_color_id.id)
                        exist_color_line.value_ids = attribute_color_value_id_lis

                    exist_size_line = False
                    if attribute_size_id and size:
                        exist_size_line = exist_product_template.attribute_line_ids.filtered(lambda a: a.attribute_id.id == attribute_size_id.id)
                        exist_size_line.value_ids = attribute_size_value_id_lis
                    
                    exist_size_value_line = exist_size_line.value_ids if exist_size_line else attribute_value_obj
                    exist_color_value_line = exist_color_line.value_ids if exist_color_line else attribute_value_obj
                    # _logger.info("exist_product_template.create_variant_ids")
                    exist_product_template.create_variant_ids()
                    _logger.info("exist_size_line.value_ids+exist_color_line.value_ids")
                    _logger.info(exist_color_value_line)
                    _logger.info(exist_size_value_line)
                    
                    _logger.info(exist_product_template.product_variant_ids.read(["name","attribute_value_ids"]))
                    product_temp = exist_product_template.product_variant_ids.filtered(lambda p:len(p.attribute_value_ids.filtered(lambda attr:attr.attribute_id.name=="Color" and attr.name == color ))>0 )
                    _logger.info(product_temp)
                    product_temp.barcode = barcode
                    # _logger.info("exist_product_template.create_variant_ids_2")
                    # os.system("echo '%s'"%("variantes 1"+json.dumps(exist_product_template.attribute_line_ids.ids)))
                    # os.system("echo '%s'"%("variantes 2"+json.dumps(exist_product_template.product_variant_ids.ids)))

                    product_attribute_value = []
                    _logger.info(color)
                    _logger.info(size)
                    if color:
                        _logger.info("product_attribute_value_color")
                        product_attribute_value_color = self.env["product.attribute.value"].search([("attribute_id","=",attribute_color_id.id),("name","=",color)])
                        _logger.info(product_attribute_value_color)
                        if len(product_attribute_value_color) > 0:
                            product_attribute_value.append(product_attribute_value_color[0])
                    if size:
                        _logger.info("product_attribute_value_size")
                        product_attribute_value_size = self.env["product.attribute.value"].search([("attribute_id","=",attribute_size_id.id),("name","=",size)])
                        _logger.info(product_attribute_value_size)
                        if len(product_attribute_value_size) > 0:
                            product_attribute_value.append(product_attribute_value_size[0])

                    _logger.info(product_attribute_value)
                    product_attribute_value= [x.id for x in product_attribute_value]
                    

                    for variant in exist_product_template.product_variant_ids.filtered(lambda r: [att.id for att in r.attribute_value_ids]== product_attribute_value):
                        variant.default_code = default_code
                        stock_move_line_list.append([0, 0, {'product_id': variant.id, 'product_qty': quantity, 'location_id': location_id}])
                        variant_list.append(variant.id)
                else:
                    os.system("echo '%s'"%("Se crear el producto: "+name))
                    product_template_vals = {
                        'name': name,
                        'default_code': default_code,
                        'categ_id': internal_categ_id.id,
                        'barcode': barcode if barcode else False,
                        'type': 'product',
                        'description': default_code, # Unieque existing product template
                        'list_price': list_price,
                        'standard_price': standard_price
                    }

                    if attribute_value_list:
                        product_template_vals['attribute_line_ids'] = attribute_value_list
                    product_tmpl_id = product_tmpl_obj.create(product_template_vals)
                    product_tmpl_id.create_variant_ids()

                    for variant in product_tmpl_id.product_variant_ids:
                        stock_move_line_list.append([0, 0, {'product_id': variant.id, 'product_qty': quantity, 'location_id': location_id}])
                        variant_list.append(variant.id)
                    self.env.cr.commit()

                record += 1
                print ("Successfully", record)
            except Exception as e:
                os.system("echo  'Error: %s'"%(e))
                error_lst.append(e)
                reject = [data.get(f, '') for f in fields]
                bounced_cust.append(reject)
                continue
            
        # os.system("echo '%s'"%(json.dumps(variant_list)))
        if stock_move_line_list:
            # os.system("echo '%s'"%(json.dumps(stock_move_line_list,indent=4)))
            stock_inventory = stock_inventory_obj.create({'name': 'Bulk Import', 'filter': 'partial', 'line_ids': stock_move_line_list})
            stock_inventory.action_start()
            for line in stock_inventory.line_ids:
                line._onchange_product_id()
            stock_inventory.action_done()

        context = self.env.context.copy()
        self.env.context = context
        return {
                'name': _('Notification'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'output',
                'type': 'ir.actions.act_window',
                'target':'new'
                }


class output(models.TransientModel):
    _name = 'output'
    _description = "Bounce file Output"

    file_path = fields.Char('File Location', size=128)
    file = fields.Binary(type='binary', string="Download File",readonly=True)
    flag = fields.Boolean('Flag')
    note = fields.Text('Note')



