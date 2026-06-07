# 파일명: app.py
import streamlit as st
import json

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

# 🌟 [치명적 버그 해결] 폰 저장소(localStorage)에 보관된 소설 목록을 안전하게 파이썬으로 복원하는 다리
# 브라우저의 보안 필터를 우회하기 위해 주소창(쿼리 파라미터)을 통해 최초 1회만 조용히 데이터를 실어 나릅니다.
restore_data = st.query_params.get("restore", None)
if restore_data:
    try:
        parsed = json.loads(restore_data)
        st.session_state['library_db'] = parsed.get('db', {})
        st.session_state['current_title'] = parsed.get('current', None)
        st.query_params.clear() # 주소창 청소 후 화면 갱신
        st.rerun()
    except:
        pass

# 파이썬 책장이 비어있을 때만 스마트폰 하드웨어에서 데이터를 긁어오도록 자바스크립트 명령 발동
if not st.session_state['library_db']:
    st.markdown("""
        <script>
        (function() {
            const win = window.top || window;
            const localDb = win.localStorage.getItem("final_perfect_db_v11");
            const localCur = win.localStorage.getItem("final_perfect_cur_v11");
            if (localDb && Object.keys(JSON.parse(localDb)).length > 0) {
                const payload = JSON.stringify({ db: JSON.parse(localDb), current: localCur || "" });
                const url = new URL(win.location.href);
                url.searchParams.set("restore", payload);
                win.location.href = url.href;
            }
        })();
        </script>
    """, unsafe_allow_html=True)

# 1. 파일 업로드 칸 (상시 노출 및 연속 추가 가능)
uploaded_file = st.file_uploader("여기에 txt 파일을 올리면 책장에 등록됩니다.", type="txt", key="novel_uploader")

if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    st.session_state['library_db'][file_name] = content
    
    # 폰 내부 저장소(localStorage)에 파일명과 본문 영구 보관 처리
    escaped_content = content.replace("`", "\\`").replace("$", "\\$")
    st.markdown(f"""
        <script>
        (function() {{
            const win = window.top || window;
            let db = JSON.parse(win.localStorage.getItem("final_perfect_db_v11")) || {{}};
            db["{file_name}"] = `{escaped_content}`;
            win.localStorage.setItem("final_perfect_db_v11", JSON.stringify(db));
            win.localStorage.setItem("final_perfect_cur_v11", "{file_name}");
            win.localStorage.setItem("final_perfect_scroll_" + "{file_name}", "0");
        }})();
        </script>
    """, unsafe_allow_html=True)
    
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
        col1, col2, col3, col4 = st.columns([3.5, 2, 1, 1])
        
        # A. 소설 제목 (일반 텍스트)
        is_active = (title == current)
        display_title = f"▶ {title}" if is_active else f"📄 {title}"
        col1.markdown(f'<div class="novel-title-text">{display_title}</div>', unsafe_allow_html=True)
            
        # B. [▶ 이어 읽기] 버튼
        if col2.button("▶ 이어 읽기", key=f"resume_{title}"):
            st.session_state['current_title'] = title
            st.markdown(f"""
                <script>
                (window.top || window).localStorage.setItem("final_perfect_cur_v11", "{title}");
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
            
        # C. [🙈 닫기] 버튼 (목록 구역)
        if is_active:
            if col3.button("🙈 닫기", key=f"close_{title}"):
                st.session_state['current_title'] = None
                st.markdown("""
                    <script>
                    (window.top || window).localStorage.removeItem("final_perfect_cur_v11");
                    </script>
                """, unsafe_allow_html=True)
                st.rerun()
        else:
            col3.write("")
            
        # D. [❌] 삭제 버튼
        if col4.button("❌", key=f"kill_{title}"):
            del st.session_state['library_db'][title]
            if st.session_state['current_title'] == title:
                st.session_state['current_title'] = None
            
            # 폰 하드웨어 데이터도 동시 삭제
            db_json = json.dumps(st.session_state['library_db']).replace("`", "\\`").replace("$", "\\$")
            st.markdown(f"""
                <script>
                const win = window.top || window;
                win.localStorage.setItem("final_perfect_db_v11", `{db_json}`);
                if(win.localStorage.getItem("final_perfect_cur_v11") === "{title}") {{
                    win.localStorage.removeItem("final_perfect_cur_v11");
                }}
                window.location.reload();
                </script>
            """, unsafe_allow_html=True)
            st.rerun()

st.write("---")

# 3. 소설 본문 출력 및 스크롤 자동 제어 구역
if current and current in books:
    # 👑 [기능 추가] 읽는 도중 언제든 편하게 닫을 수 있도록 상단에 현재 상태 표기 및 우측에 닫기 버튼 배치
    v_col1, v_col2 = st.columns([5, 2])
    v_col1.write(f"#### 📖 현재 읽는 중: {current}")
    
    # 👑 [핵심 요청 반영] 본문 읽는 도중에 즉시 화면을 닫아버릴 수 있는 본문 전용 닫기 버튼
    if v_col2.button("🙈 독서 종료 (닫기)", key="body_close_btn"):
        st.session_state['current_title'] = None
        st.markdown("""
            <script>
            (window.top || window).localStorage.removeItem("final_perfect_cur_v11");
            </script>
        """, unsafe_allow_html=True)
        st.rerun()
        
    novel_content = books[current]
    
    # 본문 텍스트 화면 출력 (드래그 완벽 금지)
    st.markdown(f'<div id="novel-body-area" class="novel-text" style="font-size: {font_size}px;">{novel_content}</div>', unsafe_allow_html=True)
    
    # 스마트폰 자체 저장소에 스크롤 위치를 기록하고 복원하는 실시간 엔진
    js_scroll_script = f"""
    <script>
    (function() {{
        const scrollKey = "final_perfect_scroll_" + "{current}";
        const win = window.top || window;

        // 소설이 열리면 무조건 기억된 위치로 순간 이동
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
