from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TicketsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'tickets_updates'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Aquí puedes procesar los datos recibidos del cliente
        # Si necesitas actualizar la tabla de Record, debes hacerlo aquí.

    async def update_records(self, event):
        await self.send(text_data=json.dumps(event['message']))

class TicketsControl(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'tickets_control'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Aquí puedes procesar los datos recibidos del cliente
        # Si necesitas actualizar la tabla de Record, debes hacerlo aquí.

    async def update_records(self, event):
        await self.send(text_data=json.dumps(event['message']))

