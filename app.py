# 파일명: app.py
import streamlit as st

st.set_page_config(page_title="방구석 소설 뷰어", layout="centered")

# CSS 및 드래그 방지 설정
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

# 1. 서버 내부 영구 저장 공간 초기화
if 'library_db' not in st.session_state:
    st.session_state['library_db'] = {}
if 'current_title' not in st.session_state:
    st.session_state['current_title'] = None

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 2. [수정됨] 파일 추가 섹션 - 타이밍 버그 방지를 위해 독립적으로 작동
with st.expander("➕ 여기에 새 소설 파일 추가하기 (터치)", expanded=True):
    # 파일이 들어오면 파이썬 내부 저장소에 즉시 안전하게 백업
    uploaded_file = st.file_uploader("텍스트(.txt) 파일을 선택하세요", type="txt", key="novel_uploader")
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        if file_name not in st.session_state['library_db']:
            try:
                bytes_data = uploaded_file.getvalue()
                content = bytes_data.decode("utf-8")
            except UnicodeDecodeError:
                content = bytes_data.decode("cp949", errors="ignore")
            
            # 무조건 안전하게 선저장
            st.session_state['library_db'][file_name] = content
            st.session_state['current_title'] = file_name
            st.toast(f"'{file_name}' 책장에 추가 완료!") # 알림창 띄우기

# 3. 책장 목록 디자인 구성
st.write("### 📖 나의 소설 목록")

if not st.session_state['library_db']:
    st.info("책장이 비어 있습니다. 위의 추가 버튼을 눌러 소설 파일을 올려주세요.")
else:
    # 딕셔너리가 도중에 바뀌어 에러 나는 것을 막기 위해 list로 복사해서 사용
    for title in list(st.session_state['library_db'].keys()):
        col1, col2 = st.columns([6, 1])
        
        # 현재 읽는 소설 강조 표시
        is_active = (title == st.session_state['current_title'])
        button_label = f"▶ {title}" if is_active else f"📄 {title}"
        
        if col1.button(button_label, key=f"btn_{title}"):
            st.session_state['current_title'] = title
            st.rerun()
            
        if col2.button("❌", key=f"del_{title}"):
            del st.session_state['library_db'][title]
            if st.session_state['current_title'] == title:
                st.session_state['current_title'] = None if not st.session_state['library_db'] else list(st.session_state['library_db'].keys())[0]
            st.rerun()

st.write("---")

# 4. 소설 본문 표시 및 이어읽기 자바스크립트 가동
current_title = st.session_state['current_title']

if current_title and current_title in st.session_state['library_db']:
    st.write(f"#### 📖 현재 읽는 중: {current_title}")
    novel_content = st.session_state['library_db'][current_title]
    
    # 본문 텍스트 화면 출력
    st.markdown(f'<div id="novel-body-area" class="novel-text" style="font-size: {font_size}px;">{novel_content}</div>', unsafe_allow_html=True)
    
    # 스크롤 위치 제어 자바스크립트
    js_scroll_script = f"""
    <script>
    (function() {{
        const scrollKey = "scroll_pos_" + "{current_title}";
        const targetWindow = window.top || window;

        // 저장된 위치로 부드럽게 스크롤 이동
        setTimeout(() => {{
            const savedPos = targetWindow.localStorage.getItem(scrollKey);
            if (savedPos && parseInt(savedPos) > 0) {{
                targetWindow.scrollTo(0, parseInt(savedPos));
            }}
        }}, 350);

        // 실시간 스크롤 위치 감지 및 저장
        targetWindow.addEventListener('scroll', () => {{
            targetWindow.localStorage.setItem(scrollKey, targetWindow.scrollY);
        }}, {{ passive: true }});
    }})();
    </script>
    """
    st.markdown(js_scroll_script, unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>목록에서 읽을 소설을 선택해 주세요.</div>", unsafe_allow_html=True)
