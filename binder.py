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
from mongodb import MongoDBHandler

class BindingToPlatform(OmniVentBase):
    def __init__(
        self,
        tnm_mqtt_broker_addr,
        kic_mqtt_broker_addr,
        mqtt_broker_port,
        mqtt_username = None,
        mqtt_password = None
    ):
        super().__init__()
        self._tnm_mqtt_broker_addr = tnm_mqtt_broker_addr
        self._kic_mqtt_broker_addr = kic_mqtt_broker_addr
        self._mqtt_broker_port = mqtt_broker_port
        self._mqtt_username = mqtt_username
        self._mqtt_password = mqtt_password
        self._register_pub_topic = REGISTER_PUB_TOPIC
        self._control_sub_topic = CONTROL_SUB_TOPIC
        self._response_pub_topic = RESPONSE_PUB_TOPIC
        self._pub_interval = 30
        self._interval_cnt = 0
        self._isfirst = True
        self._ca_certs = 'tls/ca.crt'
        self._certfile = 'tls/client.crt'
        self._keyfile = 'tls/client.key'
        self._db_handler = MongoDBHandler(
            host='localhost',
            port=27017
        )
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
                tnm_client = Client(
                        hostname = self._tnm_mqtt_broker_addr,
                        port = 1883,
                        username = self._mqtt_username,
                        password = self._mqtt_password,
                        client_id=""
                        )
                kic_client = Client(
                        hostname = self._kic_mqtt_broker_addr,
                        port = 1888,
                        client_id=""
                        )
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_context.load_cert_chain(self._certfile,self._keyfile)
                ssl_context.load_verify_locations(cafile=self._ca_certs)
                tnm_client._ssl = ssl_context
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
######################################################################################
                await stack.enter_async_context(tnm_client)


                #topic_filter = CONTROL_SUB_TOPIC
                topic_filter = self._control_sub_topic
                #manager = client.messages(topic_filter) 
                manager = tnm_client.filtered_messages(topic_filter) 

                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(self.log_messages(messages,tnm_client,kic_client))
                tasks.add(task)

                messages = await stack.enter_async_context(tnm_client.unfiltered_messages())
                #messages = await stack.enter_async_context(client.messages())
                task = asyncio.create_task(self.log_messages(messages,tnm_client,kic_client))
                tasks.add(task)

                task = asyncio.create_task(tnm_client.subscribe(self._control_sub_topic))
                tasks.add(task)

#######################################################################################
                await stack.enter_async_context(kic_client)

                #topic_filter = CONTROL_SUB_TOPIC
                topic_filter = 'himpel/#'
                #manager = client.messages(topic_filter) 
                manager = kic_client.filtered_messages(topic_filter) 

                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(self.log_messages(messages,tnm_client, kic_client))
                tasks.add(task)

                messages = await stack.enter_async_context(kic_client.unfiltered_messages())
                #messages = await stack.enter_async_context(client.messages())
                task = asyncio.create_task(self.log_messages(messages,tnm_client, kic_client))
                tasks.add(task)

                task = asyncio.create_task(kic_client.subscribe('himpel/#'))
                tasks.add(task)
#########################################################################################

                task = asyncio.create_task(self.time_changed_handler(tnm_client, interval=self._pub_interval))
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


    async def log_messages(self, messages, tnm_client, kic_client):
        async for message in messages:
            try:
                LOGGER.info(f"log_messages_message: {message.topic}")
                LOGGER.info(f"log_messages_message: {message.payload}")
                data = json.loads(message.payload)

                if message.topic == "himpel/device/report_info/000C65230FF9":
                    await self.himpel_handler(kic_client=kic_client, tnm_client=tnm_client, data=data)
                elif message.topic == CONTROL_SUB_TOPIC and data['device_id'] == 'heat_exchanger':
                    await self.himpel_handler(kic_client=kic_client, tnm_client=tnm_client, data=data, isControl=True)
                #######
                #params = formatting.interpret_control_message(data)
                #for param in params:
                #    self._modbusTcp_write(address = param['address'],value = param['value'])
                #await asyncio.wait_for(self.call_service(message), timeout=1)
            except asyncio.TimeoutError:
                LOGGER.info(f"time out!!!")
            finally:
                LOGGER.info("log_messages_finaly")



    async def time_changed_handler(self, tnm_client, interval):
        while True:
            try:
                #
                #await self.overv_handler(client=client)
                if self._isfirst == True or self._interval_cnt == 2:
                    await self.airquality_api_handler(tnm_client=tnm_client)
                    await self.airmonitor_api_handler(tnm_client=tnm_client)
                    self._interval_cnt = 0
                self._interval_cnt+=1
                self._isfirst = False
                await asyncio.sleep(interval)
            except Exception as e:
                LOGGER.info(f"time_changed_handler_error: {e}")
                await asyncio.sleep(3)

    async def airquality_api_handler(self,tnm_client):
        async with ClientSession() as session:
            pubair = PubAir(API_KEY, "대화동", session)
            await pubair.fetching_data()
            data = pubair.get_current_airpollution()
            data = data['response']['body']['items'][0]
            data = {key: value for key, value in data.items() if 'Value' in key and 'Value24' not in key}
            data = [f'{key}:{str(value)}' for key, value in data.items()]
            LOGGER.info(f"airquality_data: {data}")
            #
        payload = formatting.define_payload(
                building_in_complex="B08",   
                floor_in_complex="F05",
                home_in_complex="H02",
                device_id="airquality_out_502",
                device_type="A08",
                data_type="0",
                install_location="veranda",
                data_list=data
                )
        await tnm_client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(payload), 
            qos = 0
        )
        self._db_handler.insert_data(
            db_name = 'devices',
            collection_name='airQuality_out',
            data_to_insert = payload
        )
        #
    async def airmonitor_api_handler(self,tnm_client):
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
            payload = formatting.define_payload(
                    building_in_complex="B08",   
                    floor_in_complex="F04",
                    home_in_complex="H01",
                    device_id="air_quality_sensor",
                    device_type="D05",
                    data_type="0",
                    install_location="거실",
                    data_list=data
                    )
            await tnm_client.publish(
                topic = self._register_pub_topic, 
                payload = json.dumps(payload), 
                qos = 0
            )
            self._db_handler.insert_data(
                db_name= 'devices',
                collection_name='airQuality_in_401',
                data_to_insert = payload
            )
            
    async def himpel_handler(self, tnm_client=None, kic_client=None, data=None, isControl=None):
        if isControl:
            received_data = data
            received_data['msg_err_code'] = "1" #response
            data = data['parameter'][0]
            control_format = {"command":"","data":""}
            if data['parameter_name'] == 'control_type':
                control_format['command'] = "ctl_pw"
                control_format['data'] = "1" if data['parameter_value'] == "turn_on" else "0"
            elif data['parameter_name'] == "select_option_mode":
                control_format['command'] = 'ctl_mode'
                control_format['data'] = data['parameter_value'] #1:bypass
            elif data['parameter_name'] == "select_option_fanspeed":
                control_format['command'] = 'ctl_fan_speed'
                control_format['data'] = data['parameter_value']
            await kic_client.publish(
                topic="himpel/server/command/000C65230FF9",
                payload= json.dumps(control_format),
                qos=0
            )
            await tnm_client.publish(
                topic=RESPONSE_PUB_TOPIC,
                payload = json.dumps(received_data),
                qos=0
            )
        else:
            current_time = datetime.now()
            data = {
                'timestamp' : current_time.strftime("%Y-%m-%d %H:%M:%S"),
                'power': 'on' if data['pw_status'] == '1' else 'off',
                'mode': data['av_mode'],
                'fan_speed': data['fan_speed']
            }
            LOGGER.info(f"@@@@@@@@@@@@@@@data: {data}")
            data = [f'{key}:{str(value)}' for key, value in data.items()]
            payload = formatting.define_payload(
                    building_in_complex="B08",
                    floor_in_complex="F04",
                    home_in_complex="H01",
                    device_id="heat_exchanger",
                    device_type="O01",
                    data_type="0",
                    install_location="입구",
                    data_list=data
                    )
            await tnm_client.publish(
                topic = self._register_pub_topic, 
                payload = json.dumps(payload), 
                qos = 0
            )
            self._db_handler.insert_data(
                db_name='devices',
                collection_name='heat_exchanger_401',
                data_to_insert = payload
            )

    async def overv_handler(self,tnm_client):
        self._modbusTcp_read()
        self._modbusUdp_read()
        LOGGER.info(f"self._data_list: {self._data_list}")
        payload = formatting.define_payload(
                device_id="overv_controller_502",
                device_type="D06",
                data_type="0",
                install_location="veranda",
                data_list=self._data_list
                )
        await tnm_client.publish(
            topic = self._register_pub_topic, 
            payload = json.dumps(payload), 
            qos = 0
        )
        self._db_handler.insert_data(
            db_name='devices',
            collection_name='overv_controller_502',
            data_to_insert = payload
        )
        await tnm_client.publish(
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
        await tnm_client.publish(
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
        await tnm_client.publish(
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
        await tnm_client.publish(
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
        await tnm_client.publish(
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
        'kictechdatahub.duckdns.org',
        8884,
        'smart',
        'smart1234'
    )
    print(a._data_list)
    a.start_async_binder_manager()
