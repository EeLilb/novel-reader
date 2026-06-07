# 파일명: app.py
import streamlit as st

st.set_page_config(page_title="방구석 소설 뷰어", layout="centered")

# CSS 및 드래그 방지
st.markdown("""
    <style>
    .novel-text {
        line-height: 1.8;
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        padding: 15px;
        white-space: pre-wrap;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
    .stApp {
        background-color: #F9F5EA;
        color: #2B2B2B;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
""", unsafe_allow_html=True)

st.title("📚 방구석 웹소설 뷰어")
st.write("가상 앱 환경 스크롤 복원 버전입니다.")

uploaded_file = st.file_uploader("소설 텍스트(.txt) 파일을 선택하세요", type="txt")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)

st.write("---")

if uploaded_file is not None:
    file_name = uploaded_file.name
    
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    # 본문 출력
    st.markdown(f'<div class="novel-text" style="font-size: {font_size}px;">{content}</div>', unsafe_allow_html=True)
    
    # 👑 [가상 앱 환경 전용 스크롤 엔진]
    # iframe 구조와 상관없이 브라우저 최상단 객체(window.top)를 찾아 강제로 저장하고 복원합니다.
    js_scroll_script = f"""
    <script>
    (function() {{
        const storageKey = "scroll_pos_" + "{file_name}";
        const targetWindow = window.top || window; // 가상 앱 최고 존엄 창 찾기

        // 1) 스크롤 감지 및 즉시 저장
        targetWindow.addEventListener('scroll', () => {{
            targetWindow.localStorage.setItem(storageKey, targetWindow.scrollY);
        }}, {{ passive: true }});

        // 2) 앱을 껐다 켰을 때도 강제로 계속 시도하여 스크롤 복원
        let attempts = 0;
        const checkAndScroll = setInterval(() => {{
            const savedPos = targetWindow.localStorage.getItem(storageKey);
            attempts++;

            if (savedPos && parseInt(savedPos) > 0) {{
                targetWindow.scrollTo(0, parseInt(savedPos));
                
                // 성공했거나 너무 오래 걸리면 종료 (정상 작동 보장)
                if (Math.abs(targetWindow.scrollY - parseInt(savedPos)) < 5 || attempts > 50) {{
                    clearInterval(checkAndScroll);
                }}
            }} else {{
                clearInterval(checkAndScroll);
            }}
        }}, 80); // 0.08초마다 무한 체크
    }})();
    </script>
    """
    st.markdown(js_scroll_script, unsafe_allow_html=True)

else:
    st.info("텍스트 파일을 업로드하면 이곳에 소설 본문이 나타납니다.")
