import streamlit as st
from openai import OpenAI
import os

# ==========================================
# 1. 화면 설정 (블랙월 스타일)
# ==========================================
st.set_page_config(page_title="Blackwall Bar", page_icon="🍸")

st.title("🍸 심야의 바 '블랙월'")
st.caption("당신의 이야기를 들어주는, 조금 시니컬한 AI 바텐더")

# API 키 설정 (스트림릿 클라우드 시크릿에서 가져옴)
# 로컬 테스트용: 만약 시크릿이 없으면 환경변수나 직접 입력 사용
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

if not api_key:
    st.info("API 키를 입력해야 입장이 가능합니다.")
    st.stop()

client = OpenAI(api_key=api_key)

# ==========================================
# 2. 페르소나 설정 (V10 후킹 마스터 버전)
# ==========================================
prompt_chat = """
당신은 심야의 바 '블랙월'의 바텐더입니다.
성격: 시크하고 무심한 척하지만, 손님의 '감정'을 기가 막히게 캐치하는 **통찰력 있는 츤데레**.

[★★★ 대화의 기술 (Hooking) ★★★]:
손님이 음악, 날씨, 취미 같은 **'딴소리(Small Talk)'**를 하면, 그 소재를 이용해서 **'심리 상태'**를 물어보세요.

[절대 금지 사항]:
1. **거짓말 금지:** 가수 이름, 노래 제목 지어내지 말고 '장르'나 '분위기'로 추천하세요.
2. **숫자 리스트 금지:** 1, 2, 3 번호 매기지 마세요. 그냥 친구랑 대화하듯 줄글로 하세요.
3. **오프닝:** 손님이 말하기 전까지 넘겨짚지 마세요.
"""

prompt_cocktail = """
당신은 바텐더입니다. 손님의 사연을 듣고 [은유적 칵테일]을 한 잔 만들어주세요.
실제 술 이름 말고, 감정을 재료로 쓴 창작 칵테일을 주세요.
(예: '새벽 2시의 고독' - 재료: 한숨 1온스...)
"""

# ==========================================
# 3. 대화 기록 관리 (세션 스테이트)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": prompt_chat},
        {"role": "assistant", "content": "(잔을 닦으며 무심하게) ...왔냐? 주문은?"}
    ]

# 화면에 이전 대화 출력
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ==========================================
# 4. 사용자 입력 처리
# ==========================================
if prompt := st.chat_input("하고 싶은 말을 입력하세요..."):
    # 사용자 메시지 화면 표시 & 저장
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # 칵테일 요청인지 확인
        if any(keyword in prompt for keyword in ["칵테일", "술", "한잔"]):
            sys_msg = prompt_cocktail
            user_msg_content = f"이 손님에게 은유적 칵테일 처방:\n{st.session_state.messages}"
            temp_messages = [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg_content}
            ]
        else:
            temp_messages = st.session_state.messages

        # API 호출
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=temp_messages,
                stream=True, # 타자 치듯 나오게 하는 효과
                temperature=0.7
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")

    # AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})