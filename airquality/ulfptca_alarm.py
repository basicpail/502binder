# 한국환경공단_에어코리아_미세먼지 경보 발령 현황 API Asyncio 라이브러리
# https://data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15073885
from .base import PubAirAPIBase
from aiohttp import ClientSession


class Ulfptca_Alarm(PubAirAPIBase):
    def __init__(
        self,
        auth_key,
        session: ClientSession = None,
    ):
        """Initialize the Ulfptca Alarm Inquire Service API Class"""
        self._base_url = "http://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc"
        super().__init__(auth_key, self._base_url, session)

    async def get_ulfptca_alarm_info(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        year: 측정 연도
        itemCode: 미세먼지 항목 구분
                (PM10, PM25)
                PM10, PM25 모두 조회할 경우 파라미터 생략

        """
        end_url = self._base_url + "/getUlfptcaAlarmInfo"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "addr": params["addr"],
            "stationName": params["stationName"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response