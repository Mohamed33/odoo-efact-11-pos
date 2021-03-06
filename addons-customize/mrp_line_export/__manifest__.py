# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 SysNeo (<http://sysneoconsulting.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
	'name' : 'Mrp Line Export',
	'version' : '1.0',
	'author' : 'SysNeo Consulting S.A.C',
	'website': "http://www.sysneo.pe",
	'summary' : '',
	'description' : 
'''

- Permite exportar las lineas de las ordenes de produccion de forma agrupada.

''',
	'depends' : ['stock','mrp','report_xlsx',],
	'data' : [
		'views/mrp_view.xml',
		'wizard/mrp_line_export.xml',
		],
	'installable' : True,
	'aplication' : True,
}