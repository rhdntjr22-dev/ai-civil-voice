# AI 민원 음성상담

모바일 브라우저에서 음성으로 질문하고 Gemini가 답변한 뒤,
브라우저 음성으로 답변을 읽어주는 Flask 웹페이지입니다.

## 1. Python 설치 확인

명령 프롬프트에서 다음을 입력합니다.

```bash
python --version
```

## 2. 프로젝트 폴더로 이동

```bash
cd ai_civil_voice
```

## 3. 라이브러리 설치

```bash
pip install -r requirements.txt
```

## 4. 환경변수 파일 만들기

`.env.example` 파일을 복사하여 이름을 `.env`로 변경합니다.

`.env` 안의 값을 본인의 Gemini API 키로 바꿉니다.

```env
GEMINI_API_KEY=본인의_API_키
GEMINI_MODEL=gemini-2.5-flash-lite
```

## 5. 실행

```bash
python app.py
```

PC 브라우저에서 아래 주소를 엽니다.

```text
http://127.0.0.1:5000
```

## 모바일 테스트 시 주의

PC의 `127.0.0.1` 주소는 휴대전화에서 바로 열리지 않습니다.
처음에는 PC에서 Gemini 연결을 확인하고, 이후 Render에 배포하여
HTTPS 주소로 모바일 마이크 기능을 테스트하는 것이 가장 쉽습니다.

브라우저 음성 인식은 Android Chrome에서 비교적 잘 작동합니다.
iPhone Safari에서는 기기 및 iOS 버전에 따라 지원 방식이 다를 수 있어
직접 입력 기능도 함께 제공됩니다.

## Render 시작 명령

```bash
gunicorn app:app
```

## 주요 주소

- `/` : 웹페이지
- `/chat` : Gemini 답변 생성 API
- `/health` : API 키 설정 및 모델 확인
