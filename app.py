# 파일명: app.py
import streamlit as st

st.set_page_config(page_title="방구석 소설 뷰어", layout="centered")

# CSS: 미색 테마 및 드래그/복사/우클릭 완벽 금지
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
        user-select: none; /* 드래그 금지 */
    }
    .stApp {
        background-color: #F9F5EA;
        color: #2B2B2B;
    }
    .novel-title-text {
        font-size: 16px;
        font-weight: bold;
        line-height: 2.2;
        color: #333333;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault()); /* 우클릭 금지 */
    </script>
""", unsafe_allow_html=True)

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 앱 내부 저장 공간 초기화
if 'library_db' not in st.session_state:
    st.session_state['library_db'] = {}
if 'current_title' not in st.session_state:
    st.session_state['current_title'] = None

# 1. 파일 업로드 칸 (상시 노출 및 연속 추가 가능)
uploaded_file = st.file_uploader("여기에 txt 파일을 올리면 책장에 등록됩니다.", type="txt", key="novel_uploader")

if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    # 책장에 소설 저장 (목록에만 추가)
    st.session_state['library_db'][file_name] = content
    
    # 업로드 칸 리셋 후 새로고침
    del st.session_state["novel_uploader"]
    st.rerun()

# 2. 나의 소설 목록 UI 그리기
st.write("### 📖 나의 소설 목록")
books = st.session_state['library_db']
current = st.session_state['current_title']

if not books:
    st.info("책장이 비어 있습니다. 위의 업로드 칸에 소설을 올려 채워보세요!")
else:
    for title in list(books.keys()):
        # 한 줄에 [소설제목(텍스트) / 이어읽기 / 닫기 / 삭제] 배열
        col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
        
        # A. 소설 제목 (버튼이 아닌 일반 텍스트)
        is_active = (title == current)
        display_title = f"▶ {title}" if is_active else f"📄 {title}"
        col1.markdown(f'<div class="novel-title-text">{display_title}</div>', unsafe_allow_html=True)
            
        # B. [▶ 이어 읽기] 버튼 (처음이면 처음부터, 읽은 적 있으면 읽던 곳부터)
        if col2.button("▶ 이어 읽기", key=f"resume_{title}"):
            st.session_state['current_title'] = title
            st.rerun()
            
        # C. [🙈 닫기] 버튼 (현재 펼쳐진 소설에만 표시)
        if is_active:
            if col3.button("🙈 닫기", key=f"close_{title}"):
                st.session_state['current_title'] = None
                st.rerun()
        else:
            col3.write("")
            
        # D. [❌] 삭제 버튼
        if col4.button("❌", key=f"kill_{title}"):
            del st.session_state['library_db'][title]
            if st.session_state['current_title'] == title:
                st.session_state['current_title'] = None
            st.rerun()

st.write("---")

# 3. 소설 본문 출력 및 스크롤 자동 제어 구역
if current and current in books:
    st.write(f"#### 📖 현재 읽는 중: {current}")
    novel_content = books[current]
    
    # 본문 텍스트 화면 출력
    st.markdown(f'<div id="novel-body-area" class="novel-text" style="font-size: {font_size}px;">{novel_content}</div>', unsafe_allow_html=True)
    
    # 스마트폰 자체 저장소에 스크롤 위치를 기록하고 복원하는 실시간 엔진
    js_scroll_script = f"""
    <script>
    (function() {{
        const scrollKey = "pwa_scroll_v10_" + "{current}";
        const win = window.top || window;

        // 소설이 열리면 무조건 기억된 위치로 순간 이동 (없으면 0 지점 즉, 처음부터)
        setTimeout(() => {{
            const savedY = win.localStorage.getItem(scrollKey);
            if (savedY && parseInt(savedY) > 0) {{
                win.scrollTo(0, parseInt(savedY));
            }} else {{
                win.scrollTo(0, 0);
            }}
        }}, 150);

        // 스크롤 할 때마다 실시간 위치 저장
        win.addEventListener('scroll', () => {{
            if ("{current}" === "{st.session_state['current_title']}") {{
                win.localStorage.setItem(scrollKey, win.scrollY);
            }}
        }}, {{ passive: true }});
    }})();
    </script>
    """
    st.markdown(js_scroll_script, unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>책장에서 읽을 소설의 [▶ 이어 읽기]를 터치해 주세요.</div>", unsafe_allow_html=True)
