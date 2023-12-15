from base import OmniVentBase
from datetime import datetime
import json
import ssl
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from aiomqtt import Client, MqttError
import formatting
#import paho.mqtt.client as mqtt

from const import REGISTER_PUB_TOPIC, CONTROL_SUB_TOPIC, RESPONSE_PUB_TOPIC, API_KEY, ST_API_KEY , ST_BASE_URL
from logger import LOGGER

#
from aiohttp import ClientSession
from airquality import PubAir
from smartthings import AirMonitorClient

class BindingToPlatform(OmniVentBase):
    def __init__(
        self,
        mqtt_broker_addr,
        mqtt_broker_port,
        mqtt_username = None,
        mqtt_password = None
    ):
        super().__init__()
        self._mqtt_broker_addr = mqtt_broker_addr
        self._mqtt_broker_port = mqtt_broker_port
        self._mqtt_username = mqtt_username
        self._mqtt_password = mqtt_password
        self._register_pub_topic = REGISTER_PUB_TOPIC
        self._control_sub_topic = REGISTER_PUB_TOPIC#CONTROL_SUB_TOPIC
        self._response_pub_topic = RESPONSE_PUB_TOPIC
        self._pub_interval = 30
        self._interval_cnt = 0
        self._isfirst = True
        self._ca_certs = 'tls/ca.crt'
        self._certfile = 'tls/client.crt'
        self._keyfile = 'tls/client.key'
        #
        #
        #

    #async_binder_manager
    async def async_binder_manager(self):
        async with AsyncExitStack() as stack:
            try:
                LOGGER.info(self._data_list)
                tasks = set()
                stack.push_async_callback(self.cancel_tasks, tasks)
                client = Client(
                        hostname = self._mqtt_broker_addr,
                        username = self._mqtt_username,
                        password = self._mqtt_password,
                        client_id=""
                        )
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_context.load_cert_chain(self._certfile,self._keyfile)
                ssl_context.load_verify_locations(cafile=self._ca_certs)
                client._ssl = ssl_context
                #
                #
                #
                #client.tls_set({
                #            'ca_certs':self._ca_certs,
                #            'certfile':self_certfile,
                #            'keyfile':self_keyfile,
                #            'cert_reqs':ssl.CERT_REQUIRED,
                #            'tis_version':ssl.PROTOCOL_TLS
                #        })

                await stack.enter_async_context(client)

                #topic_filter = CONTROL_SUB_TOPIC
                topic_filter = self._control_sub_topic
                #manager = client.messages(topic_filter) 
                manager = client.filtered_messages(topic_filter) 

                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(self.log_messages(messages))
                tasks.add(task)

                messages = await stack.enter_async_context(client.unfiltered_messages())
                #messages = await stack.enter_async_context(client.messages())
                task = asyncio.create_task(self.log_messages(messages))
                tasks.add(task)

                task = asyncio.create_task(client.subscribe(self._control_sub_topic))
                tasks.add(task)

                task = asyncio.create_task(self.time_changed_handler(client, interval=self._pub_interval))
                tasks.add(task)



                await asyncio.gather(*tasks)
            #                
            except asyncio.TimeoutError:
                raise
            except asyncio.CancelledError:
	         #LOGGER.info(f"binder_async_binder_manager_CancelledError: {ce}")
                raise
            except asyncio.InvalidStateError:
	         #LOGGER.info(f"binder_async_binder_manager_InvalidStateError: {ie}")
                raise
            except asyncio.SendfileNotAvailableError:
                raise
            except asyncio.IncompleteReadError:
                raise
            except asyncio.LimitOverrunError:
                raise
            except Exception as e:
                LOGGER.info(f"binder_async_binder_manager_error: {e}")
                #loop = asyncio.get_event_loop()
                #pending = asyncio.all_tasks(loop=loop)
                #LOGGER.info(f"asyncio.all_tasks: {pending}")
                #for task in pending:
                #    task.cancel()


    async def log_messages(self, messages):
        async for message in messages:
            try:
                LOGGER.info(f"log_messages_message: {message.payload}")
                data = json.loads(message.payload)
                params = formatting.interpret_control_message(data)
                for param in params:
                    self._modbusTcp_write(address = param['address'],value = param['value'])
                #await asyncio.wait_for(self.call_service(message), timeout=1)
            except asyncio.TimeoutError:
                LOGGER.info(f"time out!!!")
            finally:
                LOGGER.info("log_messages_finaly")



    async def time_changed_handler(self, client, interval):
        while True:
            try:
                #
                
                #await self.overv_handler(client=client)
                if self._isfirst == True or self._interval_cnt == 1:
                    await self.airquality_api_handler(client=client)
                    await self.airmonitor_api_handler(client=client)
                    self._interval_cnt = 0
                self._interval_cnt+=1
                self._isfirst = False
                await asyncio.sleep(interval)
            except Exception as e:
                LOGGER.info(f"time_changed_handler_error: {e}")
                await asyncio.sleep(3)

    async def airquality_api_handler(self,client):
        async with ClientSession() as session:
            pubair = PubAir(API_KEY, "대화동", session)
            await pubair.fetching_data()
            data = pubair.get_current_airpollution()
            data = data['response']['body']['items'][0]
            data = {key: value for key, value in data.items() if 'Value' in key and 'Value24' not in key}
            data = [f'{key}:{str(value)}' for key, value in data.items()]
            LOGGER.info(f"airquality_data: {data}")
            #
        await client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(formatting.define_payload(
                building_in_complex="B08",   
                floor_in_complex="F05",
                home_in_complex="H02",
                device_id="airquality_out_502",
                device_type="A08",
                data_type="0",
                install_location="veranda",
                data_list=data)
            ), 
            qos = 0
        )
        #
    async def airmonitor_api_handler(self,client):
        async with AirMonitorClient(ST_BASE_URL,ST_API_KEY) as stclient:
            response_get = await stclient.make_authenticated_get_request('states')
            LOGGER.info(f"GET_RESPONSE: {response_get}")
            current_time = datetime.now()
            data_dict = {
                "timestamp" : current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature" : response_get['main']['temperature']['value'],
                "humidity" : response_get['main']['humidity']['value'],
                "pm10" : response_get['main']['dustLevel']['value'],
                "pm2d5" : response_get['main']['fineDustLevel']['value'],
                "pm1d0" : response_get['main']['veryFineDustLevel']['value'],
                "co2" : response_get['main']['carbonDioxide']['value'],
                "gas" : response_get['main']['odorLevel']['value']                
            }
            data = [f'{key}:{str(value)}' for key, value in data_dict.items()]
            LOGGER.info(f"@@@@@@@@@@@@@@@data: {data}")
            await client.publish(
                topic = self._register_pub_topic, 
                payload = json.dumps(formatting.define_payload(
                    building_in_complex="B08",   
                    floor_in_complex="F04",
                    home_in_complex="H01",
                    device_id="air_quality_sensor",
                    device_type="D05",
                    data_type="0",
                    install_location="거실",
                    data_list=data)
                ), 
                qos = 0
            )
            
        #

    async def overv_handler(self,client):
        self._modbusTcp_read()
        self._modbusUdp_read()
        LOGGER.info(f"self._data_list: {self._data_list}")
        await client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(formatting.define_payload(
                device_id="overv_controller_502",
                device_type="D06",
                data_type="0",
                install_location="veranda",
                data_list=self._data_list)
            ), 
            qos = 0
        )
        await client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(formatting.define_payload(
                device_id="overv_diffuser_502",
                device_type="D05",
                data_type="0",
                install_location="living1",
                data_list=self._data_list)
            ), 
            qos = 0
        )
        await client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(formatting.define_payload(
                device_id="overv_diffuser_502",
                device_type="D05",
                data_type="0",
                install_location="living2",
                data_list=self._data_list)
            ), 
            qos = 0
        )
        await client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(formatting.define_payload(
                device_id="overv_diffuser_502",
                device_type="D05",
                data_type="0",
                install_location="bedroom1",
                data_list=self._data_list)
            ), 
            qos = 0
        )
        await client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(formatting.define_payload(
                device_id="overv_diffuser_502",
                device_type="D05",
                data_type="0",
                install_location="bedroom2",
                data_list=self._data_list)
            ), 
            qos = 0
        )
        await client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(formatting.define_payload(
                device_id="overv_diffuser_502",
                device_type="D05",
                data_type="0",
                install_location="bedroom3",
                data_list=self._data_list)
            ), 
            qos = 0
        )
        self._data_list=[]

    async def cancel_tasks(self,tasks):
        for task in tasks:
            if task.done():
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def main(self):
        reconnect_interval = 3 #sec
        while True:
            try:
                await self.async_binder_manager()
            except MqttError as error:
                print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
                await asyncio.sleep(reconnect_interval)

    def start_async_binder_manager(self):
        asyncio.run(self.main())

if __name__ == '__main__':
    a = BindingToPlatform(
        'smarthousing.tnmiot.co.kr',
        8884,
        'smart',
        'smart1234'
    )
    print(a._data_list)
    a.start_async_binder_manager()
