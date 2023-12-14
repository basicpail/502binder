# 한국환경공단_에어코리아_대기오염통계 현황 API Asyncio 라이브러리
# https://data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15073855
from .base import PubAirAPIBase
from aiohttp import ClientSession


class AirPoll_Stats(PubAirAPIBase):
    def __init__(
        self,
        auth_key,
        session: ClientSession = None,
    ):
        """Initialize the Air Pollution Statistics API Class"""
        self._base_url = "http://apis.data.go.kr/B552584/ArpltnStatsSvc"
        super().__init__(auth_key, self._base_url, session)

    async def get_ctprvn_measure_list(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        itemCode: 측정항목 구분(SO2, CO, O3, NO2, PM10, PM25)
        dataGubun: 요청 자료 구분(시간평균 : HOUR, 일평균 : DAILY)
        searchCondition: 요청 데이터기간 (일주일 : WEEK, 한달 : MONTH)
        """

        end_url = self._base_url + "/getCtprvnMesureLIst"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "itemCode": params["itemCode"],
            "dataGubun": params["dataGubun"],
            "searchCondition": params["searchCondition"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_ctprvn_measure_sido_list(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        sidoName: 시도 이름(서울, 부산, 대구, 인천, 광주, 대전, 울산, 경기, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주, 세종)
        searchCondition: 요청 데이터기간(시간 : HOUR, 하루 : DAILY)
        """

        end_url = self._base_url + "/getCtprvnMesureSidoLIst"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "sidoName": params["sidoName"],
            "searchCondition": params["searchCondition"],
        }
        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_msrstn_acc_to_rdyrg(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        inqBginDt: 조회시작일자
        inqEndDt: 조회종료일자
        msrstnName: 측정소명
        """
        end_url = self._base_url + "/getMsrstnAcctoRDyrg"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "inqBginDt": params["inqBginDt"],
            "inqEndDt": params["inqEndDt"],
            "msrstnName": params["msrstnName"],
        }

        response = await self._request(method="get", url=end_url, params=query_params)
        return response

    async def get_msrstn_acc_to_rmmrg(self, params):
        """
        [Parameter List]
        serviceKey: 서비스키
        returnType: json
        numOfRows: 한 페이지 결과 수
        pageNo: 페이지 번호
        inqBginMm: 조회시작월
        inqEndMm: 조회종료월
        msrstnName: 측정소명
        """
        end_url = self._base_url + "/getMsrstnAcctoRMmrg"
        query_params = {
            "serviceKey": self._auth_key,
            "returnType": self._return_type,
            "numOfRows": params["numOfRows"],
            "pageNo": params["pageNo"],
            "inqBginMm": params["inqBginMm"],
            "inqEndMm": params["inqEndMm"],
            "msrstnName": params["msrstnName"],
        }

        response = await self._request(method="get", url=end_url, params=query_params)
        return response