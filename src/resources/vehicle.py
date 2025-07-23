from flask_restx import Namespace, Resource, fields
from src.database import retrieve, select, update, create


vehicle_ns = Namespace('vehicle', description='Vehicle operations')

vehicle_model = vehicle_ns.model('Vehicle', {
    "manufacturer": fields.String( description="Manufacturer of the vehicle."),
    "model": fields.String( description="Model of the vehicle."),
    "type": fields.String(enum=['Sedan','SUV','VAN'], description="Type of the vehicle (Sedan, SUV, VAN)."),
    "year": fields.Integer(description="Manufacturing year of the vehicle."),
    "license_plate": fields.String(description="Unique license plate of the vehicle."),
    "daily_rate": fields.Float(description="Daily rental rate for the vehicle."),
    "is_available": fields.Boolean(description="Availability status of the vehicle.")
})

@vehicle_ns.route('/<int:vehicle_id>')
@vehicle_ns.param('vehicle_id', 'The vehicle identifier')
@vehicle_ns.response(404, 'Vehicle not found')
class VehicleView(Resource):

    __table = "vehicle"

    def get_vehicle(self, id:int):
        try:
            vehicle = retrieve(self.__table, id)
            return vehicle
        except:
            raise {'error': 'Not Found'}
    
    @vehicle_ns.marshal_list_with(vehicle_model)
    def get(self, vehicle_id:int):
        return self.get_vehicle(vehicle_id)

    @vehicle_ns.expect(vehicle_model, validate=True)
    @vehicle_ns.marshal_with(vehicle_model, code=200)
    def put(self, vehicle_id:int):
        vehicle_updated_data = vehicle_ns.payload
        vehicle_data = dict(self.get_vehicle(vehicle_id))
        availability = vehicle_updated_data.get('is_available')
        if isinstance(availability, bool):
            vehicle_updated_data['is_available'] = '1' if availability else '0' 
        vehicle_data.update(vehicle_updated_data)
        vehicle = update(self.__table, vehicle_id, vehicle_data)
        return vehicle

@vehicle_ns.route('/')
class VehicleListView(Resource):
    
    __table = "vehicle"

    @vehicle_ns.marshal_list_with(vehicle_model, code=200)
    def get(self):
        return select(self.__table)
    
    @vehicle_ns.expect(vehicle_model, validate=True)
    @vehicle_ns.marshal_with(vehicle_model, code=200)
    def post(self,):
        new_vehicle_data = vehicle_ns.payload
        return create(self.__table, new_vehicle_data)
        