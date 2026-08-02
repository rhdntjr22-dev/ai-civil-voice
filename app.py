import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()

client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """
당신은 공공 민원상담을 보조하는 한국어 AI입니다.

응답 원칙:
1. 사용자의 질문을 먼저 정확히 파악하세요.
2. 친절하고 정중한 상담원 말투로 답변하세요.
3. 답변은 핵심부터 말하고, 모바일 화면에서 읽기 좋게 3~6문장으로 작성하세요.
4. 확인되지 않은 법령, 규정, 금액, 기간, 전화번호, 기관명 또는 처리 결과를 만들지 마세요.
5. 정보가 부족하면 단정하지 말고, 어떤 정보의 추가 확인이 필요한지 안내하세요.
6. 실제 민원 처리 결과를 보장하지 마세요.
7. 위험하거나 긴급한 상황은 관련 기관이나 담당자에게 즉시 확인하도록 안내하세요.
8. 답변에 마크다운 제목, 표, 별표 목록은 사용하지 마세요.
9. 현재는 기관별 내부 상담 스크립트가 연결되지 않은 시험 서비스임을 고려하세요.
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
                    "error": "Gemini API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.",
                }
            ),
            500,
        )

    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"ok": False, "error": "질문을 입력해주세요."}), 400

    if len(question) > 1000:
        return jsonify({"ok": False, "error": "질문은 1,000자 이내로 입력해주세요."}), 400

    prompt = f"""
사용자 민원 질문:
{question}

위 질문에 대해 응답 원칙을 지키면서 상담용 답변을 작성하세요.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.35,
                max_output_tokens=500,
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
                    "error": "AI 답변을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
                    "detail": str(exc) if app.debug else "",
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
