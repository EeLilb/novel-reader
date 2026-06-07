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

# 파이썬 세션 공간 초기화
if 'my_bookshelf' not in st.session_state:
    st.session_state['my_bookshelf'] = {}
if 'now_reading' not in st.session_state:
    st.session_state['now_reading'] = None

# 1. 고정된 업로드 칸 (무조건 최상단 노출)
uploaded_file = st.file_uploader("여기에 txt 파일을 올리면 책장에 등록됩니다.", type="txt", key="novel_uploader")

file_name = ""
content = ""
if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    st.session_state['my_bookshelf'][file_name] = content
    
    # 폰 내부 저장소(localStorage)에 영구 보관
    escaped_content = content.replace("`", "\\`").replace("$", "\\$")
    st.markdown(f"""
        <script>
        (function() {{
            const win = window.top || window;
            let db = JSON.parse(win.localStorage.getItem("v8_shelf_db")) || {{}};
            db["{file_name}"] = `{escaped_content}`;
            win.localStorage.setItem("v8_shelf_db", JSON.stringify(db));
            win.localStorage.setItem("v8_scroll_" + "{file_name}", "0");
        }})();
        </script>
    """, unsafe_allow_html=True)
    
    del st.session_state["novel_uploader"]
    st.rerun()

# 2. 안전 데이터 전송 백엔드 브릿지
js_receiver = st.text_input("bridge_v8", label_visibility="collapsed", key="bridge_v8_input")

if js_receiver:
    try:
        parsed_data = json.loads(js_receiver)
        st.session_state['my_bookshelf'] = parsed_data.get('db', {})
        if st.session_state['now_reading'] is None:
            st.session_state['now_reading'] = parsed_data.get('current', None)
    except:
        pass

st.markdown("""
    <script>
    (function() {
        const win = window.top || window;
        const localDb = win.localStorage.getItem("v8_shelf_db");
        const localCur = win.localStorage.getItem("v8_current_read");
        
        setTimeout(() => {
            const bridge = parent.document.querySelector('input[aria-label="bridge_v8"]');
            if (bridge && !bridge.value && localDb) {
                bridge.value = JSON.stringify({
                    db: JSON.parse(localDb),
                    current: localCur || ""
                });
                bridge.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }, 150);
    })();
    </script>
""", unsafe_allow_html=True)


# 3. [구조 업데이트] 책장 목록 칸 나누기 UI (소설이름 / 이어 읽기 / 닫기 및 삭제)
st.write("### 📖 나의 소설 목록")
shelf = st.session_state['my_bookshelf']
now_read = st.session_state['now_reading']

if not shelf:
    st.info("책장이 비어 있습니다. 위의 업로드 칸에 소설을 올려 채워보세요!")
else:
    for title in list(shelf.keys()):
        # 가로 칸을 나누어 기능 배치
        col1, col2, col3, col4 = st.columns([3.5, 2, 1, 1])
        
        # [📄 소설이름] 버튼
        is_active = (title == now_read)
        lbl = f"▶ {title}" if is_active else f"📄 {title}"
        if col1.button(lbl, key=f"title_{title}"):
            st.session_state['now_reading'] = title
            st.markdown(f"""
                <script>
                (window.top || window).localStorage.setItem("v8_current_read", "{title}");
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
            
        # [⚡ 이어 읽기] 버튼
        if col2.button("⚡ 이어 읽기", key=f"resume_{title}"):
            st.session_state['now_reading'] = title
            st.markdown(f"""
                <script>
                (window.top || window).localStorage.setItem("v8_current_read", "{title}");
                setTimeout(() => {{
                    const win = window.top || window;
                    const savedY = win.localStorage.getItem("v8_scroll_{title}");
                    if (savedY) win.scrollTo(0, parseInt(savedY));
                }}, 100);
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
            
        # 👑 [수정] 현재 읽고 있는 소설일 때만 [접기(닫기)] 버튼 노출, 아니면 빈칸
        if is_active:
            if col3.button("🙈 닫기", key=f"close_{title}"):
                st.session_state['now_reading'] = None
                st.markdown(f"""
                    <script>
                    (window.top || window).localStorage.removeItem("v8_current_read");
                    </script>
                """, unsafe_allow_html=True)
                st.rerun()
        else:
            col3.write("") # 빈 공간 유지

        # [❌ 삭제] 버튼
        if col4.button("❌", key=f"kill_{title}"):
            del st.session_state['my_bookshelf'][title]
            if st.session_state['now_reading'] == title:
                st.session_state['now_reading'] = None
            
            db_json = json.dumps(st.session_state['my_bookshelf']).replace("`", "\\`").replace("$", "\\$")
            st.markdown(f"""
                <script>
                const win = window.top || window;
                win.localStorage.setItem("v8_shelf_db", `{db_json}`);
                if(win.localStorage.getItem("v8_current_read") === "{title}") {{
                    win.localStorage.removeItem("v8_current_read");
                }}
                window.location.reload();
                </script>
            """, unsafe_allow_html=True)
            st.rerun()

st.write("---")

# 4. 소설 본문 노출 구역 (선택하기 전이나 [닫기]를 누르면 절대 뜨지 않음)
if now_read and now_read in shelf:
    st.write(f"#### 📖 현재 읽는 중: {now_read}")
    st.markdown(f'<div id="novel-view" class="novel-text" style="font-size: {font_size}px;">{shelf[now_read]}</div>', unsafe_allow_html=True)
    
    # 실시간 스크롤 트래킹 및 백업 엔진
    js_scroll = f"""
    <script>
    (function() {{
        const scrollKey = "v8_scroll_" + "{now_read}";
        const win = window.top || window;

        // 본문이 새로 열렸을 때 스크롤 복원
        setTimeout(() => {{
            const savedY = win.localStorage.getItem(scrollKey);
            if (savedY && parseInt(savedY) > 0) {{
                win.scrollTo(0, parseInt(savedY));
            }}
        }}, 250);

        // 사용자가 스크롤 할 때마다 위치 기억
        win.addEventListener('scroll', () => {{
            win.localStorage.setItem(scrollKey, win.scrollY);
        }}, {{ passive: true }});
    }})();
    </script>
    """
    st.markdown(js_scroll, unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>책장에서 읽을 소설의 제목이나 [이어 읽기]를 터치해 주세요.</div>", unsafe_allow_html=True)
