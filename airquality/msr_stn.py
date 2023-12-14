# 한국환경공단_에어코리아_측정소정보 API Asyncio 라이브러리
# https://data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15073877
from .base import PubAirAPIBase
from aiohttp import ClientSession


class Measurement_Station(PubAirAPIBase):
    def __init__(
        self,
        auth_key,
        session: ClientSession = None,
    ):
        """Initialize the Measure Station API Class"""
        self._base_url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc"
        super().__init__(auth_key, self._base_url, session)

    async def get_msr_stn_list(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        addr: 주소
        stationName: 측정소명
        """
        end_url = self._base_url + "/getMsrstnList"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            # "addr": params["addr"], 필수가 아님으로 제거
            "stationName": params["stationName"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_nearby_msr_stn_list(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        tmX: TM 측정방식 X 좌표
        tmY: TM 측정방식 Y 좌표
        ver: 1.0호출 경우 도로명 주소 검색 API가 제공하는 API의 X,Y 좌표로 가까운 측정소를 표출
        """
        end_url = self._base_url + "/getNearbyMsrstnList"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "tmX": params["tmX"],
            "tmY": params["tmY"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_tm_stdr_crdnt(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        umdNAme: 읍면동면
        """
        end_url = self._base_url + "/getTMStdrCrdnt"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "umdName": params["umdName"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response