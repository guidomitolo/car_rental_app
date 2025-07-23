from flask_restx import Namespace, Resource, fields
from ..schemas.vehicle import Vehicle


vehicle_ns = Namespace('vehicle', description='Vehicle operations')

vehicle_model = vehicle_ns.model('Vehicle', {
    "id": fields.String(readOnly=True, description="Vehicle's DB id."),
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

    def get_vehicle(self, id:int):
        try:
            vehicle = Vehicle.get(id)
            return vehicle
        except Exception as error:
            print(error)
    
    @vehicle_ns.marshal_list_with(vehicle_model)
    def get(self, vehicle_id:int):
        return self.get_vehicle(vehicle_id)

    @vehicle_ns.expect(vehicle_model, validate=True)
    @vehicle_ns.marshal_with(vehicle_model, code=200)
    def put(self, vehicle_id:int):
        vehicle = self.get_vehicle(vehicle_id)
        updated_attrs = vehicle_ns.payload
        vehicle.update(updated_attrs)
        return vehicle

    @vehicle_ns.marshal_list_with(vehicle_model)
    def delete(self, vehicle_id:int):
        vehicle_to_delete = self.get_vehicle(vehicle_id)
        vehicle_to_delete.remove()
        return vehicle_to_delete

@vehicle_ns.route('/')
class VehicleListView(Resource):

    @vehicle_ns.marshal_list_with(vehicle_model, code=200)
    def get(self):
        return Vehicle.list()
    
    @vehicle_ns.expect(vehicle_model, validate=True)
    @vehicle_ns.marshal_with(vehicle_model, code=200)
    def post(self,):
        return Vehicle.create(vehicle_ns.payload)
        