#API_KEY = "CfwM7iEPusvqhaOfJk7DXGzX2nCnoSvIixVtFZTFb8SHewh2PsMjJBUJBv8NcZM7g0dQlRkYAae9VUiEOLPHuA%3D%3D" #ssg2
API_KEY = "FQluMAe6eAL4MzWLBY3E1q5XsEtrQ9NWHhAw5cA0VQUCQa26FgbFMkVwy%2FM6MBa6ls%2BszXV6hbEaSFZDMjEWcQ%3D%3D"
ST_API_KEY="55c5450b-62c3-40ac-8b44-9882c220bcbd"
ST_BASE_URL="https://api.smartthings.com/v1/devices/a06bcc7c-7b61-4fea-54a5-7990b5706702"
PLC_REQUEST_PACKET = b'\x4b\x44\x54\x5f\x50\x4c\x43\x5f\x4d\x77\x52\x00\x00\x0a\x44\x30\x30\x30\x30\x30\x30\x30\x00\x32\x05\x66' 


REGISTER_MAP = {
    'READ_HOLDING_REGISTER':[
        {'run_mode':1,'isfloat':0},
        {'run_step':2,'isfloat':0},
        {'temp_set':4,'isfloat':0},
    ],
    'READ_INPUT_REGISTER':[
        {'pm25_in':5,'isfloat':0},
        {'co2_in':6,'isfloat':0},
        {'temp_out':19,'isfloat':1}, #외기온도
        {'temp_discharge':20,'isfloat':1}, #토출온도
        {'temp_suction':21,'isfloat':1}, #흡입온도
        {'temp_cond':22,'isfloat':1}, #응축온도
        {'temp_in':23,'isfloat':1}, #실내온도
        {'temp_eva':24,'isfloat':1}, #증발온도
        {'temp_ipm':27,'isfloat':1} #IPM온도
    ],
    'READ_UDP_REGISTER':[
        {'ahu_supply':10,'isfloat':0},
        {'ahu_vent':11,'isfloat':0},
        {'supply':0,'isfloat':0},#living1
        {'vent':6,'isfloat':0},
        {'supply':1,'isfloat':0},#living2
        {'vent':7,'isfloat':0},
        {'supply':5,'isfloat':0},#bedroom1
        {'vent':4,'isfloat':0},
        {'spply':2,'isfloat':0},#bedroom2
        {'vent':8,'isfloat':0},
        {'spply':3,'isfloat':0},#bedroom3
        {'vent':9,'isfloat':0}

    ]
}

"""
REGISTER_MAP = {
    'READ_HOLDING_REGISTER':[
        {'runmode':1,'isfloat':0},
        {'step':2,'isfloat':0},
        {'setTemp':4,'isfloat':0},
        {'auto':5,'isfloat':0}
    ],
    'READ_INPUT_REGISTER':[
        {'pm25':5,'isfloat':0},
        {'co2':6,'isfloat':0},
        {'mode':12,'isfloat':0},
        {'tempOut':19,'isfloat':1}, #외기온도
        {'tempDischarge':20,'isfloat':1}, #토출온도
        {'tempSuction':21,'isfloat':1}, #흡입온도
        {'tempCond':22,'isfloat':1}, #응축온도
        {'tempRoom':23,'isfloat':1}, #실내온도
        {'TempEva':24,'isfloat':1}, #증발온도
        {'tempIpm':27,'isfloat':1} #IPM온도
    ],
    'READ_UDP_REGISTER':[
        {'AHUSupply':10,'isfloat':0},
        {'AHUVent':11,'isfloat':0},
        {'supplyLiving1':0,'isfloat':0},
        {'ventLiving1':6,'isfloat':0},
        {'supplyLiving2':1,'isfloat':0},
        {'ventLiving2':7,'isfloat':0},
        {'supplyBedroom1':5,'isfloat':0},
        {'ventBedroom1':4,'isfloat':0},
        {'supplyBedroom2':2,'isfloat':0},
        {'ventBedroom2':8,'isfloat':0},
        {'supplyBedroom3':3,'isfloat':0},
        {'ventBedroom3':9,'isfloat':0}

    ]
}
"""


REGISTER_PUB_TOPIC = "/REGISTER/T3110457/TKT/TB08/normal"
REGISTER_PUB_TOPIC = "/REGISTER/T3110457/TKT/TB08/normal"
CONTROL_SUB_TOPIC = "/CONTROL/C3110457KT/CB08/CF04"
RESPONSE_PUB_TOPIC = "/RESPONSE/R3110457KT/RB08/CF04"



if __name__ == '__main__':
    a = REGISTER_MAP['READ_HOLDING_REGISTER']
    for dict_value in a:
        print(f"{list(dict_value.keys())[0]} : {list(dict_value.values())[0]}")
        #print(list(dict_value.keys())[0])
        #print(list(dict_value.values())[0])



