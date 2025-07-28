from flask_restx import Namespace, Resource, fields
from ..schemas.order import Order
from .customer import customer_model_retrieve
from .vehicle import vehicle_model_retrieve



order_ns = Namespace('order', description='Rental order operations')

# https://g.co/gemini/share/f8de723e8566
order_model = order_ns.model('Order', {
    'customer_id': fields.Integer(required=True, description='The ID of the customer who placed the order'),
    'vehicle_id': fields.Integer(required=True, description='The ID of the vehicle rented'),
    'pick_up_date': fields.Date(required=True, description='The date the vehicle is picked up (YYYY-MM-DD)'),
    'return_date': fields.Date(required=True, description='The date the vehicle is returned (YYYY-MM-DD)'),
    'status': fields.String(
        enum=['pending', 'confirmed', 'completed', 'cancelled'],
        default='pending',
        description='The status of the rental order'
    ),
})

order_model_retrieve = order_ns.model('OrderRetrive', {
    "id": fields.Integer(readOnly=True, description="Order's DB id."),
    'customer': fields.Nested(customer_model_retrieve, description='The ID of the customer who placed the order'),
    'vehicle': fields.Nested(vehicle_model_retrieve, description='The ID of the vehicle rented'),
    'pick_up_date': fields.Date(description='The date the vehicle is picked up (YYYY-MM-DD)'),
    'return_date': fields.Date(description='The date the vehicle is returned (YYYY-MM-DD)'),
    'total_amount': fields.Float(description='The total amount for the rental', precision=2),
    'status': fields.String(description='The status of the rental order'),
})


@order_ns.route('/<int:order_id>')
@order_ns.param('order_id', 'The order identifier')
@order_ns.response(404, 'Order not found')
class OrderView(Resource):

    def get_order(self, id:int):
        try:
            order = Order.get(id)
            return order
        except Exception as error:
            print(error)
    
    @order_ns.marshal_with(order_model_retrieve)
    def get(self, order_id:int):
        return self.get_order(order_id)
    
    @order_ns.expect(order_model, validate=True)
    @order_ns.marshal_with(order_model_retrieve, code=200)
    def put(self, order_id:int):
        order = self.get_order(order_id)
        updated_attrs = order_ns.payload
        order.update(updated_attrs)
        return order
    
    @order_ns.marshal_with(order_model_retrieve)
    def delete(self, order_id:int):
        order_to_delete = self.get_order(order_id)
        order_to_delete.remove()
        return order_to_delete

@order_ns.route('/')
class OrderListView(Resource):
    
    @order_ns.marshal_list_with(order_model_retrieve, code=200)
    def get(self):
        return Order.list()
    
    @order_ns.expect(order_model, validate=True)
    @order_ns.marshal_with(order_model_retrieve, code=200)
    def post(self,):
        return Order(**order_ns.payload).create()
        