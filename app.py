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
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault()); /* 우클릭 금지 */
    </script>
""", unsafe_allow_html=True)

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 1. 폰에 저장된 목록을 불러오기 위한 임시 자바스크립트 버퍼 설정
if 'my_bookshelf' not in st.session_state:
    st.session_state['my_bookshelf'] = {}
if 'now_reading' not in st.session_state:
    st.session_state['now_reading'] = None

# 2. [핵심 수정] 연속 업로드가 가능한 파일 업로드 칸
# 파일이 들어오면 파이썬 세션에 즉시 때려박습니다.
uploaded_file = st.file_uploader("여기에 txt 파일을 올리면 책장에 등록됩니다.", type="txt", key="novel_uploader")

if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    # 파이썬 메모리 책장에 즉시 추가
    st.session_state['my_bookshelf'][file_name] = content
    st.session_state['now_reading'] = file_name
    
    # 폰 내부 저장소(localStorage)에도 즉시 영구 저장 백업 명령 실행
    escaped_content = content.replace("`", "\\`").replace("$", "\\$")
    st.markdown(f"""
        <script>
        (function() {{
            const win = window.top || window;
            let db = JSON.parse(win.localStorage.getItem("final_shelf_db")) || {{}};
            db["{file_name}"] = `{escaped_content}`;
            win.localStorage.setItem("final_shelf_db", JSON.stringify(db));
            win.localStorage.setItem("final_current_read", "{file_name}");
            win.localStorage.setItem("final_scroll_" + "{file_name}", "0");
        }})();
        </script>
    """, unsafe_allow_html=True)
    
    # 🔥 [중요] 파일을 다 받아먹었으니 업로드 세션을 초기화하여 파일창을 즉시 비워버립니다! (연속 업로드 가능)
    del st.session_state["novel_uploader"]
    st.rerun()

# 3. [영구 보존 브릿지] 앱을 새로 켰을 때 폰에 저장되어 있던 목록을 파이썬으로 복원하는 자바스크립트
# 이 스크립트는 최초에 파이썬 책장이 비어있을 때만 폰 하드웨어에서 데이터를 긁어와 채워줍니다.
if not st.session_state['my_bookshelf']:
    # 파이썬이 데이터를 넘겨받기 위한 숨겨진 통로 (쿼리 매개변수 사용)
    query_param = st.query_params.get("restore", None)
    if query_param:
        try:
            raw_data = json.loads(query_param)
            st.session_state['my_bookshelf'] = raw_data.get("db", {})
            st.session_state['now_reading'] = raw_data.get("current", None)
            st.query_params.clear()
            st.rerun()
        except:
            pass
    else:
        st.markdown("""
            <script>
            (function() {
                const win = window.top || window;
                const localDb = win.localStorage.getItem("final_shelf_db");
                const localCur = win.localStorage.getItem("final_current_read");
                if (localDb && JSON.parse(localDb)) {
                    const payload = JSON.stringify({ db: JSON.parse(localDb), current: localCur || "" });
                    const url = new URL(win.location.href);
                    url.searchParams.set("restore", payload);
                    win.location.href = url.href;
                }
            })();
            </script>
        """, unsafe_allow_html=True)

# 4. 책장 목록 화면에 그리기
st.write("### 📖 나의 책장 목록")
shelf = st.session_state['my_bookshelf']
now_read = st.session_state['now_reading']

if not shelf:
    st.info("책장이 비어 있습니다. 위의 업로드 칸에 소설을 올려 채워보세요!")
else:
    for title in list(shelf.keys()):
        col1, col2 = st.columns([6, 1])
        is_active = (title == now_read)
        lbl = f"▶ {title}" if is_active else f"📄 {title}"
        
        # 목록 누르면 소설 뷰어 작동
        if col1.button(lbl, key=f"shelf_{title}"):
            st.session_state['now_reading'] = title
            st.markdown(f"""
                <script>
                (window.top || window).localStorage.setItem("final_current_read", "{title}");
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
            
        # 삭제 버튼 (파이썬과 폰 저장소 동시에 삭제)
        if col2.button("❌", key=f"kill_{title}"):
            del st.session_state['my_bookshelf'][title]
            if st.session_state['now_reading'] == title:
                st.session_state['now_reading'] = None if not st.session_state['my_bookshelf'] else list(st.session_state['my_bookshelf'].keys())[0]
            
            db_json = json.dumps(st.session_state['my_bookshelf']).replace("`", "\\`").replace("$", "\\$")
            st.markdown(f"""
                <script>
                const win = window.top || window;
                win.localStorage.setItem("final_shelf_db", `{db_json}`);
                win.localStorage.setItem("final_current_read", "{st.session_state['now_reading'] or ''}");
                window.location.reload();
                </script>
            """, unsafe_allow_html=True)
            st.rerun()

st.write("---")

# 5. 본문 노출 구역 및 이어읽기 스크롤 가동
if now_read and now_read in shelf:
    st.write(f"#### 📖 현재 읽는 중: {now_read}")
    st.markdown(f'<div id="novel-view" class="novel-text" style="font-size: {font_size}px;">{shelf[now_read]}</div>', unsafe_allow_html=True)
    
    # 실시간 스크롤 트래킹 및 복원 엔진
    js_scroll = f"""
    <script>
    (function() {{
        const scrollKey = "final_scroll_" + "{now_read}";
        const win = window.top || window;

        // 예전 위치로 화면 이동
        setTimeout(() => {{
            const savedY = win.localStorage.getItem(scrollKey);
            if (savedY && parseInt(savedY) > 0) {{
                win.scrollTo(0, parseInt(savedY));
            }}
        }}, 200);

        // 스크롤 할 때마다 위치 기억
        win.addEventListener('scroll', () => {{
            win.localStorage.setItem(scrollKey, win.scrollY);
        }}, {{ passive: true }});
    }})();
    </script>
    """
    st.markdown(js_scroll, unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>책장에서 읽을 소설을 터치해 주세요.</div>", unsafe_allow_html=True)
