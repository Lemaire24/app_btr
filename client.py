# client.py

from opcua import Client
from opcua import ua


class SubHandler:
    def __init__(self, callback):
        self.callback = callback

    def datachange_notification(self, node, val, data):
        self.callback(node, val)


class OPCClient:

    def __init__(self):
        self.client = None
        self.subscription = None
        self.endpoint = None

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint

    def connect(self):
        try:
            self.client = Client(self.endpoint)
            self.client.connect()
            return True
        except Exception as e:
            print("Error conexión:", e)
            return False

    def disconnect(self):
        try:
            if self.subscription:
                self.subscription.delete()
            if self.client:
                self.client.disconnect()
        except:
            pass

    def get_namespaces(self):
        return self.client.get_namespace_array()

    def create_subscription(self, callback):
        handler = SubHandler(callback)
        self.subscription = self.client.create_subscription(500, handler)

    def subscribe(self, node_id):
        node = self.client.get_node(node_id)
        self.subscription.subscribe_data_change(node)

    def write_value(self, node_id, value):
        node = self.client.get_node(node_id)

        # Detectar tipo real del nodo
        current_value = node.get_value()

        if isinstance(current_value, bool):
            dv = ua.DataValue(ua.Variant(bool(value), ua.VariantType.Boolean))
        elif isinstance(current_value, int):
            dv = ua.DataValue(ua.Variant(int(value), ua.VariantType.Int32))
        else:
            dv = ua.DataValue(ua.Variant(value))

        node.set_value(dv)