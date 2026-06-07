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
st.write("스크롤 이어읽기가 보완된 버전입니다.")

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
    
    # 🔥 [개선된 이어읽기 자바스크립트]
    # parent.window를 사용하여 Streamlit창이 아닌 휴대폰 진짜 화면 스크롤을 제어합니다.
    js_scroll_script = f"""
    <script>
    (function() {{
        const storageKey = "scroll_pos_" + "{file_name}";
        
        // 1) 휴대폰 진짜 화면(parent)의 스크롤 감지 및 저장
        parent.window.addEventListener('scroll', () => {{
            parent.localStorage.setItem(storageKey, parent.window.scrollY);
        }});

        // 2) 0.1초마다 본문이 다 준비되었는지 체크하면서 저장된 위치로 강제 이동 (최대 3초간 시도)
        let attempts = 0;
        const restoreScroll = setInterval(() => {{
            const savedPos = parent.localStorage.getItem(storageKey);
            attempts++;
            
            if (savedPos && parseInt(savedPos) > 0) {{
                parent.window.scrollTo(0, parseInt(savedPos));
                
                // 실제로 스크롤이 잘 내려갔거나 너무 오래 시도했으면 체크 종료
                if (parent.window.scrollY >= parseInt(savedPos) - 10 || attempts > 30) {{
                    clearInterval(restoreScroll);
                }}
            }} else {{
                // 저장된 위치가 없으면 즉시 종료
                clearInterval(restoreScroll);
            }}
        }}, 100);
    }})();
    </script>
    """
    st.markdown(js_scroll_script, unsafe_allow_html=True)

else:
    st.info("텍스트 파일을 업로드하면 이곳에 소설 본문이 나타납니다.")
