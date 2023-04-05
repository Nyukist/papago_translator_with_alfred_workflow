import json
import sys
import urllib.parse
import urllib.request


class PapagoTranslate:
    def __init__(self):
        self.client_id, self.client_secret = self._get_credentials()
        self.host = 'https://openapi.naver.com/v1/papago/'
        self.result = {"items": [{
            'title': '',
            'subtitle': "[Enter] 를 누르면 결과를 클립보드로 복사합니다.",
            'icon': {'path': 'icon.png'},
            'arg': ''
        }]}
        self.available_language_codes: dict = self._get_available_language_codes()

    def run(self, query) -> None:
        output_json, input_language = self._get_translated_data(str(query))
        translated_text: str = output_json['message']['result']['translatedText']

        self._update_show_message(
            text=translated_text,
            is_result=True,
            input_language=input_language
        )
        self._show_message()

    def _get_credentials(self) -> tuple[str, str]:
        # 네이버 개발자 센터에서 발급받은 client id, secret 이 있는 파일을 찾아 id, secret 반환
        try:
            with open('client_key.json', 'r') as f:
                data = json.load(f)

        except:
            error_text = 'client_key.json 을 찾을 수 없습니다'
            self._update_show_message(text=error_text)
            self._show_message()

        if 'client_id' not in data or 'client_secret' not in data:
            error_text = 'client_id 또는 client_secret 설정해주세요 : pconf'
            self._update_show_message(text=error_text)
            self._show_message()

        if not data['client_id'] or not data['client_secret']:
            error_text = 'client_id 또는 client_secret 설정해주세요 : pconf'
            self._update_show_message(text=error_text)
            self._show_message()

        return data['client_id'], data['client_secret']

    def _get_available_language_codes(self) -> dict:
        # 언어코드 파일을 찾아 dict 반환
        try:
            with open('available_language_codes.json') as f:
                datas = json.load(f)
        except:
            error_text = 'available_language_codes.json 을 찾을 수 없습니다'
            self._update_show_message(text=error_text)
            self._show_message()

        return datas

    def _update_show_message(self, text, is_result=False, input_language=None) -> None:
        # 검색 창에 보여줄 내용을 수정
        self.result['items'][0]['arg'] = text

        if is_result:
            self.result['items'][0]['title'] = text

            # 외국어 입력 시 입력된 언어를 표시하되, 한글 입력 시에는 미표시
            if not input_language == '한국어':
                self.result['items'][0]['subtitle'] = self.result['items'][0]['subtitle'] + f' (입력 언어: {input_language})'
        else:
            self.result['items'][0]['subtitle'] = text

    def _update_request(self, url: str) -> urllib.request.Request:
        # 요청할 Request의 header를 수정
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        return request

    def _get_language_code(self, query: str) -> str:
        # 입력된 텍스트의 언어코드를 반환
        url = self.host + 'detectLangs'
        request: urllib.request.Request = self._update_request(url)

        encoded_query = urllib.parse.quote(query.encode('utf-8'))
        data = "query=" + encoded_query

        dt: str = self._request(request=request, data=data)
        lang_code: dict = json.loads(dt)
        return lang_code['langCode']

    def _get_translated_data(self, query) -> tuple[dict, str]:
        # 번역 결과와 검색한 언어 반환
        text: str = urllib.parse.quote(query.encode('utf-8'))

        # 텍스트에서 언어코드 추출
        lang_code: str = self._get_language_code(query)

        if lang_code not in self.available_language_codes or lang_code == 'unk':
            self._update_show_message(text='번역 가능한 언어가 아닙니다.')
            self._show_message()

        # 한글로 입력할 시 영어로 번역
        elif lang_code == 'ko':
            data = "source=ko&target=en&text=" + text

        # 외국어로 입력 시 한글로 번역
        else:
            data = f'source={lang_code}&target=ko&text={text}'

        url = self.host + "n2mt"
        request: urllib.request.Request = self._update_request(url)

        dt: str = self._request(request=request, data=data)

        # 검색한 텍스트의 언어
        lang_code_value: str = self.available_language_codes.get(lang_code)

        return json.loads(dt), lang_code_value

    def _show_message(self):
        # 검색 창에 표시
        print(json.dumps(self.result))
        sys.stdout.flush()

        # 검색 창에 표시될 때 스크립트 종료
        exit()

    def _request(self, request, data) -> str:
        encoded_data = data.encode('utf-8')
        response = urllib.request.urlopen(request, data=encoded_data)
        status_code: int = response.status

        if status_code == 200:
            response_body = response.read()
            dt = response_body.decode('utf-8')
        else:
            dt = "error code:" + str(status_code)
        return dt


service = PapagoTranslate()

# input text
input_text = sys.argv[1]

# run translator
service.run(query=input_text)
