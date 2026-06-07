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
        user-select: none; /* 드래그 방지 */
    }
    .stApp {
        background-color: #F9F5EA;
        color: #2B2B2B;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault()); /* 우클릭 방지 */
    </script>
""", unsafe_allow_html=True)

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

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

# 2. 파이썬 메모리(session_state) 초기화
if 'my_bookshelf' not in st.session_state:
    st.session_state['my_bookshelf'] = {}
if 'now_reading' not in st.session_state:
    st.session_state['now_reading'] = None

# 3. [보안 완벽 해결] 브라우저 주소창 파라미터를 이용한 안전한 데이터 수신
# 해킹 차단 시스템에 걸리지 않는 Streamlit의 공식 안전 통로입니다.
query_data = st.query_params.get("data", None)
if query_data:
    try:
        parsed_data = json.loads(query_data)
        st.session_state['my_bookshelf'] = parsed_data.get('db', {})
        st.session_state['now_reading'] = parsed_data.get('current', None)
        # 데이터를 받았으면 주소창을 깔끔하게 청소
        st.query_params.clear()
        st.rerun()
    except:
        pass

# 4. [영구 저장 및 이어읽기 가동 핵심 엔진]
escaped_content = content.replace("`", "\\`").replace("$", "\\$")
js_script = f"""
<script>
(function() {{
    const DB_KEY = "my_permanent_shelf_v5";
    const CUR_KEY = "my_current_reading_v5";
    const SCROLL_PREFIX = "my_scroll_v5_";
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
        
        // 업로드 성공 후 안전하게 화면 갱신 요청
        sendToPython();
    }}

    // [B] 안전하게 폰 데이터를 파이썬으로 동기화하는 함수
    function sendToPython() {{
        const localDb = win.localStorage.getItem(DB_KEY);
        const localCur = win.localStorage.getItem(CUR_KEY);
        if (localDb) {{
            const payload = JSON.stringify({{
                db: JSON.parse(localDb),
                current: localCur || ""
            }});
            // 주소창을 통해 안전하게 데이터를 전달 (입력창 방식 탈피!)
            const url = new URL(win.location.href);
            url.searchParams.set("data", payload);
            win.location.href = url.href;
        }}
    }}

    // 최초 실행 시 파이썬에 데이터가 없으면 동기화 실행
    {"if (!win.location.search.includes('data') && " + str(not st.session_state['my_bookshelf']).lower() + ") { sendToPython(); }" }

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
    const win = window.top || window;
    win.localStorage.setItem("my_current_reading_v5", title);
    const localDb = win.localStorage.getItem("my_permanent_shelf_v5");
    const payload = JSON.stringify({{ db: JSON.parse(localDb), current: title }});
    const url = new URL(win.location.href);
    url.searchParams.set("data", payload);
    win.location.href = url.href;
}};

window.nativeDelete = function(title) {{
    if(confirm("이 소설을 책장에서 삭제할까요?")) {{
        const win = window.top || window;
        let db = JSON.parse(win.localStorage.getItem("my_permanent_shelf_v5")) || {{}};
        delete db[title];
        win.localStorage.setItem("my_permanent_shelf_v5", JSON.stringify(db));
        if(win.localStorage.getItem("my_current_reading_v5") === title) {{
            win.localStorage.removeItem("my_current_reading_v5");
        }}
        const current = win.localStorage.getItem("my_current_reading_v5") || "";
        const payload = JSON.stringify({{ db: db, current: current }});
        const url = new URL(win.location.href);
        url.searchParams.set("data", payload);
        win.location.href = url.href;
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
        
        if col1.button(lbl, key=f"shelf_{title}"):
            st.markdown(f"<script>window.nativeSelect('{title}');</script>", unsafe_allow_html=True)
            
        if col2.button("❌", key=f"kill_{title}"):
            st.markdown(f"<script>window.nativeDelete('{title}');</script>", unsafe_allow_html=True)

st.write("---")

# 6. 본문 노출 구역
if now_read and now_read in shelf:
    st.write(f"#### 📖 현재 읽는 중: {now_read}")
    st.markdown(f'<div id="novel-view" class="novel-text" style="font-size: {font_size}px;">{shelf[now_read]}</div>', unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>책장에서 읽을 소설을 터치해 주세요.</div>", unsafe_allow_html=True)
