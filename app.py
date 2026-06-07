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

# 1. 고정된 업로드 칸 (무조건 최상단 노출)
uploaded_file = st.file_uploader("여기에 txt 파일을 올리면 책장에 등록됩니다.", type="txt", key="novel_uploader")

# 자바스크립트로 보낼 변수 초기화
file_name = ""
content = ""
if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")

# 2. 파이썬과 폰 저장소(localStorage)를 연결하는 보이지 않는 다리
js_receiver = st.text_input("data_bridge", label_visibility="collapsed", key="bridge_input")

# 3. 폰에서 불러온 데이터를 파이썬 메모리에 안착
if 'my_bookshelf' not in st.session_state:
    st.session_state['my_bookshelf'] = {}
if 'now_reading' not in st.session_state:
    st.session_state['now_reading'] = None

if js_receiver:
    try:
        parsed_data = json.loads(js_receiver)
        st.session_state['my_bookshelf'] = parsed_data.get('db', {})
        st.session_state['now_reading'] = parsed_data.get('current', None)
    except:
        pass

# 4. [영구 저장 및 이어읽기 가동 핵심 엔진]
# 폰이 꺼져도 폰 자체 기억장치(localStorage)에 소설 목록, 본문, 스크롤 위치를 싹 다 때려 박습니다.
escaped_content = content.replace("`", "\\`").replace("$", "\\$")
js_script = f"""
<script>
(function() {{
    const DB_KEY = "my_permanent_shelf_v4";
    const CUR_KEY = "my_current_reading_v4";
    const SCROLL_PREFIX = "my_scroll_v4_";
    const win = window.top || window;

    // [A] 새 파일 업로드 감지 시 즉시 폰 저장소에 영구 박기
    const newTitle = "{file_name}";
    const newText = `{escaped_content}`;
    if (newTitle && newText.trim() !== "") {{
        let db = JSON.parse(win.localStorage.getItem(DB_KEY)) || {{}};
        db[newTitle] = newText;
        win.localStorage.setItem(DB_KEY, JSON.stringify(db));
        win.localStorage.setItem(CUR_KEY, newTitle);
        win.localStorage.setItem(SCROLL_PREFIX + newTitle, "0");
    }}

    // [B] 파이썬 서버로 현재 폰에 저장된 데이터 역전송 (새로고침, 껐다 켰을 때 복원용)
    const localDb = win.localStorage.getItem(DB_KEY);
    const localCur = win.localStorage.getItem(CUR_KEY);
    
    setTimeout(() => {{
        const bridge = parent.document.querySelector('input[aria-label="data_bridge"]');
        if (bridge && !bridge.value) {{
            bridge.value = JSON.stringify({{
                db: localDb ? JSON.parse(localDb) : {{}},
                current: localCur || ""
            }});
            bridge.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }}, 200);

    // [C] 이어읽기 위치 스크롤 자동 이동
    const activeTitle = win.localStorage.getItem(CUR_KEY);
    if (activeTitle) {{
        setTimeout(() => {{
            const savedY = win.localStorage.getItem(SCROLL_PREFIX + activeTitle);
            if (savedY && parseInt(savedY) > 0) {{
                win.scrollTo(0, parseInt(savedY));
            }}
        }}, 350);
    }}

    // [D] 실시간 스크롤 위치 폰에 영구 기록
    win.addEventListener('scroll', () => {{
        const cur = win.localStorage.getItem(CUR_KEY);
        if (cur) {{
            win.localStorage.setItem(SCROLL_PREFIX + cur, win.scrollY);
        }}
    }}, {{ passive: true }});
}})();

// 목록 변경 시 폰 저장소 원격 제어 함수
window.nativeSelect = function(title) {{
    (window.top || window).localStorage.setItem("my_current_reading_v4", title);
}};
window.nativeDelete = function(title) {{
    if(confirm("이 소설을 책장에서 삭제할까요?")) {{
        const win = window.top || window;
        let db = JSON.parse(win.localStorage.getItem("my_permanent_shelf_v4")) || {{}};
        delete db[title];
        win.localStorage.setItem("my_permanent_shelf_v4", JSON.stringify(db));
        if(win.localStorage.getItem("my_current_reading_v4") === title) {{
            win.localStorage.removeItem("my_current_reading_v4");
        }}
        window.location.reload();
    }}
}};
</script>
"""
st.markdown(js_script, unsafe_allow_html=True)

# 5. 책장 목록 화면에 그리기
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
        
        # 버튼 누르면 즉시 타겟 지정 및 강제 동기화
        if col1.button(lbl, key=f"shelf_{title}"):
            st.markdown(f"<script>window.nativeSelect('{title}');</script>", unsafe_allow_html=True)
            st.session_state['now_reading'] = title
            st.rerun()
            
        if col2.button("❌", key=f"kill_{title}"):
            st.markdown(f"<script>window.nativeDelete('{title}');</script>", unsafe_allow_html=True)

st.write("---")

# 6. 본문 노출 구역
if now_read and now_read in shelf:
    st.write(f"#### 📖 현재 읽는 중: {now_read}")
    st.markdown(f'<div id="novel-view" class="novel-text" style="font-size: {font_size}px;">{shelf[now_read]}</div>', unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>책장에서 읽을 소설을 터치해 주세요.</div>", unsafe_allow_html=True)
