# 한국환경공단_에어코리아_대기오염정보 조회 서비스 API Asyncio 라이브러리
# https://data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15073861
from .base import PubAirAPIBase
from aiohttp import ClientSession


class AirPoll_Information(PubAirAPIBase):
    def __init__(
        self,
        auth_key,
        session: ClientSession = None,
    ):
        """Initialize the Air Pollution Information Inquire API Class"""
        self._base_url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc"
        super().__init__(auth_key, self._base_url, session)

    async def get_msrstn_accto_rltm_measure_dnsty(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        stationName: 측정소명
        dataTerm: 요청 데이터기간 (DAILY, MONTH, 3MONTH)
        ver: 버전별 상세 결과
        ※ 버전(ver) 항목설명
            - 버전을 포함하지 않고 호출할 경우 : PM2.5 데이터가 포함되지 않은 원래 오퍼레이션 결과 표출.
            - 버전 1.0을 호출할 경우 : PM2.5 데이터가 포함된 결과 표출.
            - 버전 1.1을 호출할 경우 : PM10, PM2.5 24시간 예측이동 평균데이터가 포함된 결과 표출.
            - 버전 1.2을 호출할 경우 : 측정망 정보 데이터가 포함된 결과 표출.
            - 버전 1.3을 호출할 경우 : PM10, PM2.5 1시간 등급 자료가 포함된 결과 표출

        """

        end_url = self._base_url + "/getMsrstnAcctoRltmMesureDnsty"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "stationName": params["stationName"],
            "dataTerm": params["dataTerm"],
            "ver": params["ver"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_unity_air_envrn_index_bad_list(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        """

        end_url = self._base_url + "/getUnityAirEnvrnIdexSnstiveAboveMsrstnList"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_ctprvn_rltm_measure_dnsty(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        sidoName: 시도 이름
        ver: 버전별 상세 결과
        ※ 버전(ver) 항목설명
            - 버전을 포함하지 않고 호출할 경우 : PM2.5 데이터가 포함되지 않은 원래 오퍼레이션 결과 표출.
            - 버전 1.0을 호출할 경우 : PM2.5 데이터가 포함된 결과 표출.
            - 버전 1.1을 호출할 경우 : PM10, PM2.5 24시간 예측이동 평균데이터가 포함된 결과 표출.
            - 버전 1.2을 호출할 경우 : 측정망 정보 데이터가 포함된 결과 표출.
            - 버전 1.3을 호출할 경우 : PM10, PM2.5 1시간 등급 자료가 포함된 결과 표출

        """
        end_url = self._base_url + "/getCtprvnRltmMesureDnsty"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "sidoName": params["sidoName"],
            "ver": params["ver"],
        }

        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_minu_dust_frcst_dspth(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        searchDate: 통보시간 검색
        InformCode: 통보코드검색 (PM10, PM25, O3)
        """
        end_url = self._base_url + "/getMinuDustFrcstDspth"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "searchDate": params["searchDate"],
            "InformCode": params["InformCode"],
        }

        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_minu_dust_week_frcst_dspth(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        searchDate: 통보시간검색
        """
        end_url = self._base_url + "/getMinuDustWeekFrcstDspth"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "searchDate": params["searchDate"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response