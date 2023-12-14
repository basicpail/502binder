from pprint import pprint
from logger import LOGGER

def split_string_into_pairs(start_num, end_num, pair_length, input_str, ):
    response_hex_list = [input_str[i:i+pair_length] for i in range(start_num, end_num, pair_length)]
    return response_hex_list



def combine_third_fourth_to_decimal(arr):
    decimal_values = []
    for pair in arr:
        combined_hex = pair[2] + pair[3]
        decimal_value = int(combined_hex, 16)
        if decimal_value>60000: #if decimal_value < 0
            decimal_value = -(65536-decimal_value)
        decimal_values.append(decimal_value)
    
    return decimal_values

def list_to_dict(arr,dict):
    for item in arr:
        key, value = item.split(':')
        dict[key] = value

def interpret_control_message(data):
    device_info = data['device_info'][0]
    params = []
    
    for parameter_data in device_info.get("parameter", []):
        parameter_name = parameter_data.get("parameter_name", "")
        parameter_value = parameter_data.get("parameter_value", "")
        #
        LOGGER.info(f"parameter_data: {parameter_data}")
        if parameter_name == "ctl_mode":
            address = 0x01
            if parameter_value == "stop": value = 0
            elif parameter_value == "vent": value = 6
            elif parameter_value == "bypass" : value = 5
        elif parameter_name == "ctl_step":
            address = 0x03
            if parameter_value == "0" : value = 0
            elif parameter_value == "1" : value = 501
            elif parameter_value == "2" : value = 1001
            elif parameter_value == "3" : value = 1501
            elif parameter_value == "4" : value = 1601
        #
        params.append({'address':address,'value':value})
    #
    return params
    #

def define_payload(building_in_complex, floor_in_complex, home_in_complex, device_id, device_type, data_type, install_location, data_list):
    swap_list = []
    devices_dict = {
        "device1":
        {
            "space_class":"0",
            "complex_tag": "3110457KT",
            "building_in_complex": f"{building_in_complex}",
            "floor_in_complex": f"{floor_in_complex}",
            "home_in_complex": f"{home_in_complex}",
            "device_info": [
                {
                "device_id": f"{device_id}",
                "device_type":f"{device_type}",
                "data_type": f"{data_type}",
                "install_location": f"{install_location}",
                "msg_data": [
                ]
                }
            ]
        }
    }

    if device_id == "overv_controller_502":
        data_list = data_list[0:14]
    elif device_id == "overv_diffuser_502" and install_location == "living1":
        data_list = data_list[14:16]
    elif device_id == "overv_diffuser_502" and install_location == "living2":
        data_list = data_list[16:18]
    elif device_id == "overv_diffuser_502" and install_location == "bedroom1":
        data_list = data_list[18:20]
    elif device_id == "overv_diffuser_502" and install_location == "bedroom2":
        data_list = data_list[20:22]
    elif device_id == "overv_diffuser_502" and install_location == "bedroom3":
        data_list = data_list[22:24]
    #
    #
    #
    
    for data in data_list:
        temp = {
            "field_name": f"{data.split(':')[0]}",
            "field_value":f"{data.split(':')[1]}",
            "field_type":"string"
        }
        swap_list.append(temp)


    devices_dict["device1"]["device_info"][0]["msg_data"] = swap_list

    
    return devices_dict["device1"]


if __name__ == '__main__':
    a=['run_mode:0', 'run_step:1', 'temp_set:22', 'pm25_in:9', 'co2_in:465', 'temp_out:27.6', 'temp_discharge:27.8', 'temp_suction:26.9', 'temp_cond:27.7', 'temp_in:25.6', 'Temp_eva:25.5', 'temp_ipm:3.9', 'ahu_supply:0', 'ahu_vent:0', 'living1_supply:0', 'living1_vent:0', 'living2_supply:0', 'living2_vent:165', 'bedroom1_supply:25', 'bedroom1_vent:0', 'bedroom2_spply:24', 'bedroom2_vent:61', 'bedroom3_spply:23', 'bedroom3_vent:0']
    pprint(define_payload('overv_controller','timestamp',a ))
