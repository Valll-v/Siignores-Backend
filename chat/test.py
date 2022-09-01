import asyncio
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


async def notify(user_id, message):    
    asyncio.run(channel_layer.group_send(
                'chat_' + str(user_id),
                {
                    'type': 'chat_message',
                    'message': message,
                }
            ))