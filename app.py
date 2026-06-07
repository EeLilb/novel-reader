# 파일명: app.py
import streamlit as st
import json

st.set_page_config(page_title="방구석 소설 뷰어", layout="centered")

# 1. 외부 플러그인 설치 없이 Streamlit 내부 컴포넌트 조합으로 안전하게 데이터 송수신 통로 개설
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

# 2. 고정된 업로드 칸 (무조건 최상단 노출)
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
    
    # [수정] 파일 올리면 메모리에만 넣고 '현재 읽는 소설(now_reading)'은 공백으로 둠 -> 즉시 띄우지 않음!
    st.session_state['my_bookshelf'][file_name] = content
    
    # 폰 내부 저장소에도 영구 저장 백업
    escaped_content = content.replace("`", "\\`").replace("$", "\\$")
    st.markdown(f"""
        <script>
        (function() {{
            const win = window.top || window;
            let db = JSON.parse(win.localStorage.getItem("v6_shelf_db")) || {{}};
            db["{file_name}"] = `{escaped_content}`;
            win.localStorage.setItem("v6_shelf_db", JSON.stringify(db));
            win.localStorage.setItem("v6_scroll_" + "{file_name}", "0");
        }})();
        </script>
    """, unsafe_allow_html=True)
    
    # 파일 업로더 즉시 비워주기 (연속 업로드 가능)
    del st.session_state["novel_uploader"]
    st.rerun()

# 3. [보안 돌파 최신 브릿지] 가상 앱 차단에 걸리지 않는 숨겨진 안전 데이터 전송용 입력창
# 브라우저가 일반 타이핑으로 인식하게 만들어 절대 포맷되지 않습니다.
js_receiver = st.text_input("bridge_v6", label_visibility="collapsed", key="bridge_v6_input")

if js_receiver:
    try:
        parsed_data = json.loads(js_receiver)
        st.session_state['my_bookshelf'] = parsed_data.get('db', {})
        # 껐다 켰을 때, 이전에 선택해서 읽고 있던 소설 제목이 있다면 복원
        if st.session_state['now_reading'] is None:
            st.session_state['now_reading'] = parsed_data.get('current', None)
    except:
        pass

# 폰에 저장된 목록 데이터를 안전하게 파이썬으로 밀어넣어주는 자바스크립트 엔진
st.markdown("""
    <script>
    (function() {
        const win = window.top || window;
        const localDb = win.localStorage.getItem("v6_shelf_db");
        const localCur = win.localStorage.getItem("v6_current_read");
        
        setTimeout(() => {
            const bridge = parent.document.querySelector('input[aria-label="bridge_v6"]');
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
        
        # 목록에서 소설을 직접 '터치'해야만 본문이 열리도록 설정
        if col1.button(lbl, key=f"shelf_{title}"):
            st.session_state['now_reading'] = title
            st.markdown(f"""
                <script>
                (window.top || window).localStorage.setItem("v6_current_read", "{title}");
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
            
        # 삭제 기능
        if col2.button("❌", key=f"kill_{title}"):
            del st.session_state['my_bookshelf'][title]
            if st.session_state['now_reading'] == title:
                st.session_state['now_reading'] = None
            
            db_json = json.dumps(st.session_state['my_bookshelf']).replace("`", "\\`").replace("$", "\\$")
            st.markdown(f"""
                <script>
                const win = window.top || window;
                win.localStorage.setItem("v6_shelf_db", `{db_json}`);
                if(win.localStorage.getItem("v6_current_read") === "{title}") {{
                    win.localStorage.removeItem("v6_current_read");
                }}
                window.location.reload();
                </script>
            """, unsafe_allow_html=True)
            st.rerun()

st.write("---")

# 5. 본문 노출 구역 및 이어읽기 스크롤 가동
# 사용자가 고르기 전(now_read가 None일 때)에는 본문 영역을 절대 띄우지 않고 대기합니다.
if now_read and now_read in shelf:
    st.write(f"#### 📖 현재 읽는 중: {now_read}")
    st.markdown(f'<div id="novel-view" class="novel-text" style="font-size: {font_size}px;">{shelf[now_read]}</div>', unsafe_allow_html=True)
    
    # 실시간 스크롤 트래킹 및 복원 엔진
    js_scroll = f"""
    <script>
    (function() {{
        const scrollKey = "v6_scroll_" + "{now_read}";
        const win = window.top || window;

        // 예전 위치로 화면 이동
        setTimeout(() => {{
            const savedY = win.localStorage.getItem(scrollKey);
            if (savedY && parseInt(savedY) > 0) {{
                win.scrollTo(0, parseInt(savedY));
            }}
        }}, 250);

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
