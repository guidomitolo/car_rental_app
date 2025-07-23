from flask_restx import Namespace, Resource, fields
from ..schemas.order import Order
from .customer import customer_model
from .vehicle import vehicle_model
from datetime import datetime


order_ns = Namespace('order', description='Rental order operations')

# https://g.co/gemini/share/f8de723e8566
order_model = order_ns.model('Order', {
    'customer_id': fields.Integer(required=True, description='The ID of the customer who placed the order'),
    'vehicle_id': fields.Integer(required=True, description='The ID of the vehicle rented'),
    'pick_up_date': fields.Date(required=True, description='The date the vehicle is picked up (YYYY-MM-DD)'),
    'return_date': fields.Date(required=True, description='The date the vehicle is returned (YYYY-MM-DD)'),
    'status': fields.String(
        required=True,
        enum=['pending', 'confirmed', 'completed', 'cancelled'],
        default='pending',
        description='The status of the rental order'
    ),
})

order_model_retrieve = order_ns.model('OrderRetrive', {
    "id": fields.Integer(readOnly=True, description="Order's DB id."),
    'customer': fields.Nested(customer_model, description='The ID of the customer who placed the order'),
    'vehicle': fields.Nested(vehicle_model, description='The ID of the vehicle rented'),
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
    
    @order_ns.marshal_list_with(order_model_retrieve)
    def get(self, order_id:int):
        return self.get_order(order_id)
    
    @order_ns.expect(order_model, validate=True)
    @order_ns.marshal_with(order_model_retrieve, code=200)
    def put(self, order_id:int):
        order = self.get_order(order_id)
        updated_attrs = order_ns.payload
        order.update(updated_attrs)
        return order

    # @order_ns.expect(order_model, validate=True)
    # @order_ns.marshal_with(order_model_retrieve, code=200)
    # def put(self, order_id:int):
    #     order_updated_data = order_ns.payload
    #     order_data = dict(self.get_order(order_id))
    #     order_data.update(order_updated_data)
    #     order_data.update({'total_amount': self.calculate_rate(order_data['pick_up_date'], order_data['return_date'], order_data['vehicle']['daily_rate'])})
    #     order_data.pop('customer')
    #     order_data.pop('vehicle')
    #     order = update(self.__table, order_id, order_data)
    #     return order

@order_ns.route('/')
class OrderListView(Resource):
    
    @order_ns.marshal_list_with(order_model_retrieve, code=200)
    def get(self):
        return Order.list()
    
    @order_ns.expect(order_model, validate=True)
    @order_ns.marshal_with(order_model_retrieve, code=200)
    def post(self,):
        return Order.create(order_ns.payload)
        