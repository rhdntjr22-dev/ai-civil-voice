import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()

client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """
당신은 민원인의 문의를 듣고 직접 안내하는 친절한 민원상담사입니다.

답변 원칙:
1. 민원인에게 직접 말하듯 자연스럽고 정중한 한국어로 답변하세요.
2. 질문을 그대로 반복하거나 분석 과정을 설명하지 말고, 첫 문장부터 핵심 안내를 시작하세요.
3. 딱딱한 보고서, 검색 결과, 법률 문서처럼 말하지 마세요.
4. 전문 용어는 쉬운 말로 풀어 설명하세요.
5. 민원인이 다음에 무엇을 확인하고 어떻게 행동하면 되는지 자연스럽게 안내하세요.
6. 확인되지 않은 법령, 규정, 기관명, 전화번호, 금액, 기간, 서류 또는 처리 결과를 만들지 마세요.
7. 정보가 부족하면 추측하지 말고, 정확한 안내를 위해 무엇을 추가로 확인해야 하는지 알려주세요.
8. 실제 민원 처리 결과를 보장하거나 확정적으로 약속하지 마세요.
9. 기관마다 기준이 달라질 수 있는 내용은 담당 부서나 해당 기관에 확인하도록 안내하세요.
10. 답변은 모바일 화면에서 읽기 편하도록 3~6문장으로 작성하세요.
11. 마크다운 제목, 표, 번호 목록, 별표 목록은 사용하지 마세요.
12. 'AI로서', '제공된 정보에 따르면', '일반적으로', '문의하셨군요' 같은 기계적인 표현은 피하세요.
13. 답변 끝마다 '더 궁금한 점이 있으면 말씀해 주세요'를 반복하지 마세요.
14. 현재는 기관별 내부 상담 스크립트가 연결되지 않은 시험 서비스이므로, 확실하지 않은 업무 기준은 반드시 확인이 필요하다고 안내하세요.

좋은 답변 예시:
"주소 변경은 본인 확인 후 신청하실 수 있습니다. 먼저 해당 기관 홈페이지에서 주소 변경이나 개인정보 변경 메뉴를 확인해 주세요. 온라인 처리가 어렵다면 신분증을 준비해 담당 창구나 고객센터에 문의하시면 됩니다. 기관마다 필요한 서류가 다를 수 있으니 접수 전에 확인하시는 것이 좋습니다."
"""


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(
        {
            "ok": True,
            "api_key_configured": bool(API_KEY),
            "model": MODEL_NAME,
        }
    )


@app.post("/chat")
def chat():
    if client is None:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Gemini API 키가 설정되지 않았습니다. Render 환경변수 또는 .env 파일을 확인해주세요.",
                }
            ),
            500,
        )

    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"ok": False, "error": "문의 내용을 입력해주세요."}), 400

    if len(question) > 1000:
        return jsonify({"ok": False, "error": "문의 내용은 1,000자 이내로 입력해주세요."}), 400

    prompt = f"""
민원인이 말한 문의 내용:
{question}

위 문의에 민원상담사가 직접 답변하는 것처럼 안내하세요.
확실하지 않은 정보는 임의로 만들지 말고, 필요한 확인 사항을 자연스럽게 알려주세요.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
                max_output_tokens=650,
            ),
        )

        answer = (response.text or "").strip()
        if not answer:
            raise ValueError("Gemini가 빈 답변을 반환했습니다.")

        return jsonify({"ok": True, "answer": answer})

    except Exception as exc:
        print(f"[Gemini error] {type(exc).__name__}: {exc}")
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "상담 답변을 준비하지 못했습니다. 잠시 후 다시 시도해주세요.",
                    "detail": str(exc) if app.debug else "",
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=True,
    )