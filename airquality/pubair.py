import aiohttp
import asyncio

from .msr_stn import Measurement_Station
from .pltn_info_inqrsvc import AirPoll_Information


class PubAir:
    def __init__(
        self,
        auth_key: str = None,
        umdName: str = None,
        client_session: aiohttp.ClientSession = None,
    ):
        self._auth_key = auth_key
        self._umdName = umdName
        self._session = client_session

        self.msr_stn = Measurement_Station(self._auth_key, self._session)
        self._tmx = None
        self._tmy = None
        self._sggName = None
        self._sidoName = None
        self._closest_station = None
        self._stationName = None
        self._distanceToStation = None
        self._addr = None
        self._deep_station_information = None

        self.pltn_info = AirPoll_Information(self._auth_key, self._session)
        self._data = None

    async def fetching_data(self):
        async def _get_umdName_coordinates(self):
            params = {
                "numOfRows": "10",
                "pageNo": "1",
                "umdName": self._umdName,
            }

            res = await self.msr_stn.get_tm_stdr_crdnt(params)

            item = res["response"]["body"]["items"][0]
            self._tmX = item["tmX"]
            self._tmY = item["tmY"]
            self._sggName = item["sggName"]
            self._sidoName = item["sidoName"]

        async def _get_closest_msr_stn(self):
            params = {
                "tmX": self._tmX,
                "tmY": self._tmY,
            }

            res = await self.msr_stn.get_nearby_msr_stn_list(params)
            item = res["response"]["body"]["items"]
            self._closest_station = item[0]

        await _get_umdName_coordinates(self)
        await _get_closest_msr_stn(self)

        self._stationName = self._closest_station["stationName"]
        self._distanceToStation = self._closest_station["tm"]
        self._addr = self._closest_station["addr"]

        async def _get_stn_information(self):
            params = {
                "numOfRows": "100",
                "pageNo": "1",
                "stationName": self._stationName,
            }

            res = await self.msr_stn.get_msr_stn_list(params)
            item = res["response"]["body"]["items"]
            self._deep_station_information = item[0]

        await _get_stn_information(self)

        params = {
            "numOfRows": "100",
            "pageNo": "1",
            "stationName": self._stationName,
            "dataTerm": "DAILY",
            "ver": "1.3",
        }

        response = await self.pltn_info.get_msrstn_accto_rltm_measure_dnsty(params)
        self._data = response

    def get_station_information(self):
        return self._deep_station_information

    def get_current_airpollution(self):
        return self._data
