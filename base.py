import sys
#sys.path.append("C:\테스트코드\pymodbus")
import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from const import REGISTER_MAP,PLC_REQUEST_PACKET
import formatting
from logger import LOGGER

class OmniVentBase:
    def __init__(
            self,
            converter_addr: str = '192.168.7.11',
            converter_port: int = 502,
            converter_unit_id : int = 1,
            starting_register_address: int = 0,
            number_of_register: int = 30,
            plc_addr: str = '192.168.7.13',
            plc_port: int = 10262

    ):
        self._converter_addr = converter_addr
        self._converter_port = converter_port
        self._converter_unit_id = converter_unit_id
        self._starting_register_address = starting_register_address
        self._number_of_register = number_of_register
        self._plc_addr = plc_addr
        self._plc_port = plc_port
        self._plc_request_packet = PLC_REQUEST_PACKET
        self._plc_response = None
        self._diffuser_id = 0x01
        self._formatting = formatting
        self._data_list = []
        self._data_dict = {}

    def _modbusTcp_read(self):
        try:
            client = ModbusTcpClient(host=self._converter_addr, port=self._converter_port)
            if client.connect():
                #response = client.read_input_registers(address=address, count=count, unit=unit)
                response = client.read_holding_registers(address=self._starting_register_address, count=self._number_of_register, unit=self._converter_unit_id)
                for holding_register in REGISTER_MAP['READ_HOLDING_REGISTER']:
                    self._data_list.append(f"{list(holding_register.keys())[0]}:{response.registers[list(holding_register.values())[0]]}")
                    LOGGER.info(f"{list(holding_register.keys())[0]}:{response.registers[list(holding_register.values())[0]]}")

                response = client.read_input_registers(address=self._starting_register_address, count=self._number_of_register, unit=self._converter_unit_id)
                for input_register in REGISTER_MAP['READ_INPUT_REGISTER']:
                    if list(input_register.values())[1] == 1:
                        LOGGER.info(f"{list(input_register.keys())[0]}:{response.registers[list(input_register.values())[0]]/10}")
                        self._data_list.append(f"{list(input_register.keys())[0]}:{response.registers[list(input_register.values())[0]]/10}")
                    else:
                        LOGGER.info(f"{list(input_register.keys())[0]}:{response.registers[list(input_register.values())[0]]}")           
                        self._data_list.append(f"{list(input_register.keys())[0]}:{response.registers[list(input_register.values())[0]]}")
                
                self._formatting.list_to_dict(arr=self._data_list,dict=self._data_dict)

                if not response.isError():
                    decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big)
                    data = decoder.decode_32bit_float()  # Adjust this based on your data format
                else:
                    LOGGER.info("Modbus error:", response)
            else:
                LOGGER.info("Unable to connect to Modbus server")
        except Exception as e:
            LOGGER.info("Error:", e)
        finally:
            client.close()

    def _modbusUdp_read(self):
        try:
            volume_contents_start_num = 22
            volume_contents_len = 12
            volume_contents_end_num = volume_contents_start_num + (volume_contents_len*4)

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(self._plc_request_packet, (self._plc_addr, self._plc_port))
            
            response, _ = client_socket.recvfrom(1024)  # Adjust buffer size as needed
            response = response.hex()
            self._plc_response = self._formatting.split_string_into_pairs(
                start_num=0 ,
                end_num=len(response),
                pair_length=2,
                input_str=response
            )
            self._plc_response = self._formatting.split_string_into_pairs(
                start_num=volume_contents_start_num,
                end_num=volume_contents_end_num,
                pair_length=4,
                input_str=self._plc_response
            )
            self._plc_response = self._formatting.combine_third_fourth_to_decimal(self._plc_response)
            for udp_register in REGISTER_MAP['READ_UDP_REGISTER']:
                LOGGER.info(f"{list(udp_register.keys())[0]}:{self._plc_response[list(udp_register.values())[0]]}")
                self._data_list.append(f"{list(udp_register.keys())[0]}:{self._plc_response[list(udp_register.values())[0]]}")
                self._formatting.list_to_dict(arr=self._data_list,dict=self._data_dict)
                
        except Exception as e:
            LOGGER.info("Error:", e)
        finally:
            client_socket.close()

    def _modbusTcp_write(self,address,value):
        try:
            client = ModbusTcpClient(host=self._converter_addr, port=self._converter_port)
            if client.connect():
                #client.transaction_id = self._transaction_id
                #response = client.read_input_registers(address=address, count=count, unit=unit)
                response = client.write_register(address= address,value = value)
                #response = client.write_coil(address= 0x01,value = True, unit=7)
                
                #response = client.write_register(address= 0x07, value= 9, unit=7)
                
                #response = client.execute(request)
                # if response.isError():
                #     LOGGER.info("Holding Register에 데이터를 쓰는데 실패했습니다.")
                # else:
                #     LOGGER.info("Holding Register에 데이터를 성공적으로 썼습니다.")
            else:
                LOGGER.info("Unable to connect to Modbus server")
        except Exception as e:
            LOGGER.info("Error:", e)
        finally:
            client.close()


if __name__ == '__main__':
    a = OmniVentBase()
    #a._modbusTcp_write()
    a._modbusTcp_read()
    a._modbusUdp_read()
    print(a._data_list)
    print(a._data_dict)
    
