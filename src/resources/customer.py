from flask_restx import Namespace, Resource, fields
from ..schemas.customer import Customer


customer_ns = Namespace('customer', description='Customer operations')

customer_model_retrieve = customer_ns.model('CustomerRetrieve', {
    "id": fields.Integer(readOnly=True, description="Customer's DB id."),
    "created_at": fields.DateTime(readOnly=True, description="Entry creation date", required=False),
    "first_name": fields.String(max_length=50, description="Customer's first name."),
    "last_name": fields.String(max_length=50, description="Customer's last name."),
    "email": fields.String(max_length=100, description="Unique email address of the customer."),
    "phone": fields.String(max_length=20, description="Customer's phone number."),
    "address": fields.String(max_length=255, description="Customer's street address."),
    "city": fields.String(max_length=100, description="Customer's city."),
    "state": fields.String(max_length=100, description="Customer's state."),
    "zip_code": fields.String(max_length=10, description="Customer's zip code."),
    "contact_channel": fields.String(max_length=10, description="Customer's contact channel."),
})

customer_model = customer_ns.model('Customer', {
    "first_name": fields.String(max_length=50, description="Customer's first name."),
    "last_name": fields.String(max_length=50, description="Customer's last name."),
    "email": fields.String(max_length=100, description="Unique email address of the customer."),
    "phone": fields.String(max_length=20, description="Customer's phone number."),
    "address": fields.String(max_length=255, description="Customer's street address."),
    "city": fields.String(max_length=100, description="Customer's city."),
    "state": fields.String(max_length=100, description="Customer's state."),
    "zip_code": fields.String(max_length=10, description="Customer's zip code."),
    "contact_channel": fields.String(max_length=10, description="Customer's contact channel."),
})



@customer_ns.route('/<int:customer_id>')
@customer_ns.param('customer_id', 'The customer identifier')
@customer_ns.response(404, 'Customer not found')
class CustomerView(Resource):

    def get_customer(self, id:int):
        try:
            customer = Customer.get(id)
            return customer
        except Exception as error:
            print(error)
    
    @customer_ns.marshal_with(customer_model_retrieve)
    def get(self, customer_id:int):
        return self.get_customer(customer_id)

    @customer_ns.expect(customer_model, validate=True)
    @customer_ns.marshal_with(customer_model_retrieve, code=200)
    def put(self, customer_id:int):
        customer = self.get_customer(customer_id)
        updated_attrs = customer_ns.payload
        return customer.update(updated_attrs)
    
    @customer_ns.marshal_with(customer_model_retrieve)
    def delete(self, customer_id:int):
        customer_to_delete = self.get_customer(customer_id)
        customer_to_delete.remove()
        return customer_to_delete

@customer_ns.route('/')
class CustomerListView(Resource):
    
    @customer_ns.marshal_list_with(customer_model_retrieve, code=200)
    def get(self):
        return Customer.list()
    
    @customer_ns.expect(customer_model, validate=True)
    @customer_ns.marshal_with(customer_model_retrieve, code=200)
    def post(self,):
        return Customer(**customer_ns.payload).create()
        