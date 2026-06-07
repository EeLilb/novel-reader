# 파일명: app.py
import streamlit as st
import json

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

# 1. 파이썬 메모리(session_state) 초기화
if 'library' not in st.session_state:
    st.session_state['library'] = {}
if 'current' not in st.session_state:
    st.session_state['current'] = None
if 'loaded_from_js' not in st.session_state:
    st.session_state['loaded_from_js'] = False

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 2. 스마트폰 내부 저장소(localStorage)와 파이썬 간의 데이터 연동 브릿지
# 브라우저 보안에 안 걸리는 안전한 컴포넌트를 사용하여 데이터를 파이썬으로 동기화합니다.
js_bridge = """
<script>
(function() {
    const dbKey = "novel_permanent_v3";
    const currentKey = "novel_curr_title_v3";
    const targetWindow = window.top || window;
    
    // 스마트폰 폰에 저장된 책장 데이터를 가져옴
    const localDb = targetWindow.localStorage.getItem(dbKey);
    const localCurrent = targetWindow.localStorage.getItem(currentKey);
    
    // Streamlit 파이썬 서버에 데이터 전송 통로 마련
    const sendToStreamlit = (data) => {
        const input = parent.document.querySelector('input[aria-label="js_data_receiver"]');
        if (input) {
            input.value = JSON.stringify(data);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };

    // 최초 1회 혹은 스크롤 발생 시 데이터 동기화 요청
    setTimeout(() => {
        sendToStreamlit({
            db: localDb ? JSON.parse(localDb) : {},
            current: localCurrent || ""
        });
    }, 300);
})();
</script>
"""

# 파이썬이 자바스크립트로부터 데이터를 안전하게 받기 위한 숨겨진 인풋창
js_data = st.text_input("js_data_receiver", label_visibility="collapsed", key="js_receiver")

# 자바스크립트가 보내온 폰 내부 데이터를 파이썬 메모리에 강제 주입
if js_data and not st.session_state['loaded_from_js']:
    try:
        parsed = json.loads(js_data)
        st.session_state['library'] = parsed.get('db', {})
        st.session_state['current'] = parsed.get('current', None)
        st.session_state['loaded_from_js'] = True
        st.rerun()
    except:
        pass

# 3. 새 파일 추가 섹션
with st.expander("➕ 여기에 새 소설 파일 추가하기 (터치)", expanded=True):
    uploaded_file = st.file_uploader("텍스트(.txt) 파일을 선택하세요", type="txt")
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        if file_name not in st.session_state['library']:
            try:
                bytes_data = uploaded_file.getvalue()
                content = bytes_data.decode("utf-8")
            except UnicodeDecodeError:
                content = bytes_data.decode("cp949", errors="ignore")
            
            # 파이썬 메모리에 저장
            st.session_state['library'][file_name] = content
            st.session_state['current'] = file_name
            
            # 폰 하드웨어 저장소에도 영구 기록되도록 스크립트 실행
            escaped_content = content.replace("`", "\\`").replace("$", "\\$")
            st.markdown(f"""
                <script>
                (function() {{
                    const dbKey = "novel_permanent_v3";
                    const currentKey = "novel_curr_title_v3";
                    const targetWindow = window.top || window;
                    
                    let db = JSON.parse(targetWindow.localStorage.getItem(dbKey)) || {{}};
                    db["{file_name}"] = `{escaped_content}`;
                    targetWindow.localStorage.setItem(dbKey, JSON.stringify(db));
                    targetWindow.localStorage.setItem(currentKey, "{file_name}");
                }})();
                </script>
            """, unsafe_allow_html=True)
            st.success(f"'{file_name}' 추가 완료!")
            st.rerun()

# 4. 소설 목록 UI 그리기 (보안 걱정 없는 순수 파이썬 방식)
st.write("### 📖 나의 소설 목록")

if not st.session_state['library']:
    st.info("책장이 비어 있습니다. 소설 파일을 추가해 주세요.")
else:
    for title in list(st.session_state['library'].keys()):
        col1, col2 = st.columns([6, 1])
        
        is_active = (title == st.session_state['current'])
        btn_label = f"▶ {title}" if is_active else f"📄 {title}"
        
        if col1.button(btn_label, key=f"select_{title}"):
            st.session_state['current'] = title
            st.markdown(f"""
                <script>
                (window.top || window).localStorage.setItem("novel_curr_title_v3", "{title}");
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
            
        if col2.button("❌", key=f"del_{title}"):
            del st.session_state['library'][title]
            if st.session_state['current'] == title:
                st.session_state['current'] = None if not st.session_state['library'] else list(st.session_state['library'].keys())[0]
            
            # 폰 저장소에서도 지우기
            db_json = json.dumps(st.session_state['library']).replace("`", "\\`").replace("$", "\\$")
            st.markdown(f"""
                <script>
                (window.top || window).localStorage.setItem("novel_permanent_v3", `{db_json}`);
                (window.top || window).localStorage.setItem("novel_curr_title_v3", "{st.session_state['current'] or ''}");
                </script>
            """, unsafe_allow_html=True)
            st.rerun()

st.write("---")

# 5. 본문 표시 및 스마트 이어읽기 가동
current_title = st.session_state['current']

if current_title and current_title in st.session_state['library']:
    st.write(f"#### 📖 현재 읽는 중: {current_title}")
    novel_content = st.session_state['library'][current_title]
    
    st.markdown(f'<div id="novel-display" class="novel-text" style="font-size: {font_size}px;">{novel_content}</div>', unsafe_allow_html=True)
    
    # 안전한 스크롤 이어읽기 자바스크립트
    js_scroll = f"""
    <script>
    (function() {{
        const scrollKey = "novel_scroll_v3_" + "{current_title}";
        const targetWindow = window.top || window;

        // 저장된 위치 복원
        setTimeout(() => {{
            const savedPos = targetWindow.localStorage.getItem(scrollKey);
            if (savedPos && parseInt(savedPos) > 0) {{
                targetWindow.scrollTo(0, parseInt(savedPos));
            }}
        }}, 350);

        // 스크롤 위치 영구 실시간 저장
        targetWindow.addEventListener('scroll', () => {{
            targetWindow.localStorage.setItem(scrollKey, targetWindow.scrollY);
        }}, {{ passive: true }});
    }})();
    </script>
    """
    st.markdown(js_scroll, unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>목록에서 읽을 소설을 선택해 주세요.</div>", unsafe_allow_html=True)

# 백포그라운드 동기화 엔진 가동
st.markdown(js_bridge, unsafe_allow_html=True)
