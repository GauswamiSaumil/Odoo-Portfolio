import xmlrpc.client
from pprint import pprint as pp
from datetime import datetime, date
import ssl
context = ssl._create_unverified_context()


class OdooImporterBase:
	def __init__(self, odoo15_url, odoo15_db, odoo15_username, odoo15_password, odoo17_url, odoo17_db, odoo17_username, odoo17_password):
		# Odoo 15 Connection
		self.common_15 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(odoo15_url), context=context, allow_none=True)
		self.uid_15 = self.common_15.authenticate(odoo15_db, odoo15_username, odoo15_password, {})
		self.models_15 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(odoo15_url), context=context, allow_none=True)

		# Odoo 17 Connection
		self.common_17 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(odoo17_url), context=context, allow_none=True)
		self.uid_17 = self.common_17.authenticate(odoo17_db, odoo17_username, odoo17_password, {})
		self.models_17 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(odoo17_url), context=context, allow_none=True)

		self.odoo15_db = odoo15_db
		self.odoo15_password = odoo15_password
		self.odoo17_db = odoo17_db
		self.odoo17_password = odoo17_password

		self.error_dict = {}
		self.cache = {
			'many2one': {},
			'many2many': {},
			'external_ids': {}
		}

	def search_existing_external_id(self, model_name, old_record_id):
		external_id = self.models_15.execute_kw(
			self.odoo15_db, self.uid_15, self.odoo15_password, 'ir.model.data', 'search_read',
			[[['model', '=', model_name], ['res_id', '=', old_record_id]]],
			{'fields': ['module', 'name'], 'limit': 1}
		)
		module, name = (f'__imported__', f'{model_name.replace(".", "_")}_imported_{old_record_id}') if not external_id else (external_id[0].get('module', ''), external_id[0].get('name'))
		external_17_id = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, 'ir.model.data', 'search_read', [[
			['module', '=', module], ['name', '=', name]]], {'fields': ['id', 'res_id'], 'limit': 1})
		return module, name, external_17_id[0].get('id', False) if external_17_id else False, external_17_id[0].get('res_id', False) if external_17_id else False

	def create_external_id(self, model_name, new_record_id, old_record_id):
		module, name, external_17_id, record_17_id = self.search_existing_external_id(model_name, old_record_id)
		if not external_17_id:
			external_17_id = [self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, 'ir.model.data', 'create', [{
				'module': module,
				'name': name,
				'model': model_name,
				'res_id': new_record_id,
			}]
														)]
		self.cache['external_ids'][(model_name, old_record_id)] = external_17_id[0]
		return external_17_id[0]

	def get_relation_model_name(self, field_name, is_many2many, model_id):
		field_data = self.models_15.execute_kw(
			self.odoo15_db, self.uid_15, self.odoo15_password, 'ir.model.fields', 'search_read',
			[[['name', '=', field_name], ['ttype', '=', 'many2one' if not is_many2many else 'many2many'], ['model_id', '=', model_id]]],
			{'fields': ['relation']}
		)
		if field_data:
			return field_data[0]['relation']
		return False

	def handle_many2many_field_ids(self, data_15, model_name, field):
		data_17_ids = []
		for data in data_15:
			record_15_id = data['id']
			record_15_name = data['name']
			cache_key = (model_name, record_15_id)
			if cache_key in self.cache['many2many']:
				record_17_id = self.cache['many2many'][cache_key]
				print(">>>>caching working -- many2many", self.cache['many2many'])
			else:
				record_17_id = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, model_name, 'search', [[['name', '=', record_15_name]]], {'limit': 1})
				if not record_17_id:
					record_17_id = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, model_name, 'create', [{'name': record_15_name}])
				else:
					record_17_id = record_17_id[0]
				self.cache['many2many'][cache_key] = record_17_id
			self.create_external_id(model_name, record_17_id, data['id'])
			data_17_ids.append(record_17_id)
		return data_17_ids

	def get_or_create_many2one(self, model_name, record_15_id, field, many2many_fields):
		if not record_15_id:
			return False

		cache_key = [(model_name, id_15) for id_15 in ([record_15_id] if isinstance(record_15_id, int) else record_15_id)]
		cache_found = list(filter(lambda k: k in self.cache['many2one'], cache_key))
		if cache_found:
			print(">>>>caching working -- many2one", cache_found)

			return self.cache['many2one'][cache_found[0]]

		readable_ids = record_15_id if field in many2many_fields else [record_15_id]
		record_15_data = self.models_15.execute_kw(self.odoo15_db, self.uid_15, self.odoo15_password, model_name, 'read', [readable_ids], {'fields': ['name']})
		if not record_15_data:
			return False

		if field in many2many_fields:
			return self.handle_many2many_field_ids(record_15_data, model_name, field)

		record_15_name = record_15_data[0]['name']
		record_17_id = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, model_name, 'search', [[['name', '=', record_15_name]]], {'limit': 1})

		if not record_17_id:
			record_17_id = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, model_name, 'create', [{'name': record_15_name}])
		else:
			record_17_id = record_17_id[0]
		cache_key = (model_name, record_15_id)
		self.create_external_id(model_name, record_17_id, record_15_id)
		self.cache['many2one'][cache_key] = record_17_id
		return record_17_id

	def import_attachment(self, attachment_ids):
		new_attachment_ids = []
		for attachment_id in attachment_ids:
			old_attachment = self.models_15.execute_kw(self.odoo15_db, self.uid_15, self.odoo15_password, 'ir.attachment', 'read', [attachment_id], {'fields': ['name', 'datas']})[0]
			cache_key = ('ir.attachment', attachment_id)
			if cache_key in self.cache['many2one']:
				existing_attachment = self.cache['many2one'][cache_key]
			else:
				existing_attachment = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, 'ir.attachment', 'search', [[['name', '=', old_attachment.get('name')]]], {'limit': 1})
				if existing_attachment:
					existing_attachment = existing_attachment[0]
				else:
					existing_attachment = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, 'ir.attachment', 'create', [{
						'name': old_attachment.get('name', ''),
						'datas': old_attachment.get('datas', ''),
					}])
				self.cache['many2one'][cache_key] = existing_attachment
			new_attachment_ids.append(existing_attachment)
			self.create_external_id('ir.attachment', existing_attachment, attachment_id)
		return new_attachment_ids

	def import_property_fields(self, model_name, res_id):
		property_fields = ['property_account_position_id', 'property_product_pricelist', 'property_stock_custom']
		for field in property_fields:
			properties_15 = self.models_15.execute_kw(
				self.odoo15_db, self.uid_15, self.odoo15_password, 'ir.property', 'search_read',
				[[['fields_id.name', '=', field], ['res_id', '=', f'{model_name},{res_id}']]],
				{'fields': ['value_reference', 'fields_id', 'name']}
			)
			for prop in properties_15:
				value_model, value_id = prop['value_reference'].split(',')
				value_17_id = self.get_or_create_many2one(value_model, int(value_id), field, [])
				self.models_17.execute_kw(
					self.odoo17_db, self.uid_17, self.odoo17_password, 'ir.property', 'create', [{
						'fields_id': prop['fields_id'][0],
						'name': prop['name'],
						'res_id': f'{model_name},{res_id}',
						'value_reference': f'{value_model},{value_17_id}'
					}]
				)
				self.cache['many2one'][(value_model, int(value_id))] = value_17_id


class OdooPartnerImporter(OdooImporterBase):
	def __init__(self, *args):
		super().__init__(*args)
		self.current_model_17_id = 85
		self.current_model_15_id = 84
		self.company_15_id, self.company_17_id = 1, 1
		self.list_of_fields_to_fetch_partner = [
			'name', 'name_ar', 'function', 'email', 'phone', 'is_referring_doctor', 'mobile', 'ref', 'hms_contact_type',
			'street', 'street2', 'city', 'zip', 'website', 'is_company', 'gov_code', 'passport', 'sex', 'blood_group', 'credit_limit', 'image_1920'
		]
		self.many2one_fields_partner = ['country_id', 'state_id', 'title', 'user_id', 'team_id']
		self.many2many_fields_partner = ['category_id']
		self.self_model_fields_partner = ['parent_id', 'child_ids']
		self.property_fields = ['property_account_position_id', 'property_product_pricelist', 'property_stock_custom']

	def fetch_partners_15(self, limit, offset):
		return self.models_15.execute_kw(
			self.odoo15_db, self.uid_15, self.odoo15_password, 'res.partner', 'search_read', [[]], {
				'fields': self.list_of_fields_to_fetch_partner + self.many2one_fields_partner + self.many2many_fields_partner,
				'limit': limit,
				'offset': offset
			}
		)

	def fetch_and_import_partners(self):
		limit = 500
		for i in range(10259, 10000000, 500):
			partners_15 = self.fetch_partners_15(limit=limit, offset=i)
			print("\n\n\n\n\n======================Total Partners found %s================================================\n\n\n\n" % len(partners_15))
			
			total_partners_to_prepare = len(partners_15)
			created_in17 = 0
			remaining_partners = total_partners_to_prepare

			for partner in partners_15:
				# Prepare partner data
				partner_data = {
					'old_id': partner.get('id'),
					**dict(filter(lambda k: k[0] in self.list_of_fields_to_fetch_partner, partner.items()))
				}

				# Handling many2one and many2many fields
				for field in self.many2one_fields_partner + self.many2many_fields_partner:
					model_name = self.get_relation_model_name(field, field in self.many2many_fields_partner, self.current_model_15_id)
					record_15_id = partner[field][0] if partner[field] and isinstance(partner[field][-1], str) else partner[field] if partner[field] else False
					new_17_ids = self.get_or_create_many2one(model_name, record_15_id, field, self.many2many_fields_partner)
					if new_17_ids:
						partner_data[field] = [(6, 0, new_17_ids)] if isinstance(new_17_ids, list) else new_17_ids

				total_partners_to_prepare -= 1

				if total_partners_to_prepare % 2 == 0:
					print("\n\n >>>>>>>>>>>>>>>> Remaining Partners to prepare vals: %s" % total_partners_to_prepare)

				# Import partner to Odoo 17
				try:
					old_id = partner_data.pop('old_id')
					partner_id = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, 'res.partner', 'create', [partner_data])
					self.create_external_id('res.partner', partner_id, old_id)
					self.import_property_fields('res.partner', partner_id)
					created_in17 += 1
				except Exception as e:
					self.error_dict[partner_data['name']] = e

				remaining_partners -= 1

				if remaining_partners % 2 == 0:
					print("\n\n >>>>>>>>>>>>>>>> Remaining Partners: %s" % remaining_partners)

			if not self.error_dict:
				print("Partners imported successfully from Odoo 15 to Odoo 17.\n\n\n")
			else:
				print("\n\n\n\n\n======================================================================\n\n\n\n")
				print("Partners can not be imported from Odoo 15 to Odoo 17, please check the error log.\n\nTotal missing partners: %s\n\n\n" % len(list(self.error_dict.keys())))
				pp(self.error_dict)



class OdooEmployeeImporter(OdooImporterBase):
	def __init__(self, *args):
		super().__init__(*args)
		self.current_model_id = 116
		self.list_of_fields_to_fetch_employee = [
			'name', 'work_email', 'work_phone', 'work_location', 'mobile_phone',
		]
		self.many2one_fields_employee = ['country_id', 'department_id', 'job_id']
		self.many2many_fields_employee = ['skill_ids']
		self.self_model_fields_employee = ['parent_id', 'child_ids']

	def fetch_employees_15(self):
		return self.models_15.execute_kw(
			self.odoo15_db, self.uid_15, self.odoo15_password, 'hr.employee', 'search_read', [[]], {
				'fields': self.list_of_fields_to_fetch_employee + self.many2one_fields_employee + self.many2many_fields_employee,
				'limit': 40,
				'offset': 0
			}
		)

	def prepare_employees_for_import(self, employees_15):
		employees_17 = []
		for employee in employees_15:
			employee_data = {
				'old_id': employee.get('id'),
				**dict(filter(lambda k: k[0] in self.list_of_fields_to_fetch_employee, employee.items()))
			}

			# Handling many2one fields
			for field in self.many2one_fields_employee + self.many2many_fields_employee:
				model_name = self.get_relation_model_name(field, field in self.many2many_fields_employee, self.current_model_id)
				record_15_id = employee[field][0] if employee[field] and isinstance(employee[field][-1], str) else employee[field] if employee[field] else False
				new_17_ids = self.get_or_create_many2one(model_name, record_15_id, field, self.many2many_fields_employee)
				if new_17_ids:
					employee_data[field] = [(6, 0, new_17_ids)] if isinstance(new_17_ids, list) else new_17_ids

			employees_17.append(employee_data)
		return employees_17

	def import_employees_to_17(self, employees_17):
		created_in17 = 0
		remaining_employees = len(employees_17)

		for employee in employees_17:
			try:
				old_id = employee.pop('old_id')
				employee_id = self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, 'hr.employee', 'create', [employee])
				self.create_external_id('hr.employee', employee_id, old_id)
				created_in17 += 1
			except Exception as e:
				self.error_dict[employee['name']] = e
			remaining_employees -= 1

			if remaining_employees % 2 == 0:
				print("\n\n >>>>>>>>>>>>>>>> Remaining Employees: %s" % remaining_employees)

	def run(self):
		employees_15 = self.fetch_employees_15()
		employees_17 = self.prepare_employees_for_import(employees_15)
		self.import_employees_to_17(employees_17)

		if not self.error_dict:
			print("Employees imported successfully from Odoo 15 to Odoo 17.\n\n\n")
		else:
			print("\n\n\n\n\n======================================================================\n\n\n\n")
			print("Employees can not be imported from Odoo 15 to Odoo 17, please check the error log.\n\n\n")
			pp(self.error_dict)


	def update_plan_status(self):
		status_to_method_mapping = {
			'running': 'action_confirm',
			'cancel': 'action_cancel',
		}
		for plan in self.models_15.execute_kw(self.odoo15_db, self.uid_15, self.odoo15_password, 'acs.insurance.plan', 'search_read', [[['state', '!=', 'draft']]], {'fields': ['id', 'state']}):
			print(f">>>>>>.checking plan to update: {plan}")
			module, name, external_17_id, record_17_id = self.search_existing_external_id('acs.insurance.plan', plan.get('id', False))
			call_method = status_to_method_mapping.get(plan.get('state', False))
			if call_method:
				try:
					self.models_17.execute_kw(self.odoo17_db, self.uid_17, self.odoo17_password, 'acs.insurance.plan', call_method, [[record_17_id]])
					print(f">>>>>>.plan updated with status: {plan.get('state', False)}, after updating status with {call_method}")
				except Exception as e:
					print(f"\n\n\n --------- Error ---------------- {e} ----------------------- Error---------------ID: {record_17_id} \n\n\n")

# Example usage
# Connection details for both servers
odoo15_url = ''
odoo15_db = ''
odoo15_username = 'odoo@'
odoo15_password = '123456'

odoo17_url = ''
odoo17_db = ''
odoo17_username = 'odoo@'
odoo17_password = 'admin'

# partner_importer = OdooPartnerImporter(odoo15_url, odoo15_db, odoo15_username, odoo15_password, odoo17_url, odoo17_db, odoo17_username, odoo17_password)
# partner_importer.fetch_and_import_partners()

employee_importer = OdooEmployeeImporter(odoo15_url, odoo15_db, odoo15_username, odoo15_password, odoo17_url, odoo17_db, odoo17_username, odoo17_password)
employee_importer.update_plan_status()



