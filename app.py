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

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 1. 파일 추가 확장 레이아웃
with st.expander("➕ 여기에 새 소설 파일 추가하기 (터치)", expanded=True):
    uploaded_file = st.file_uploader("텍스트(.txt) 파일을 선택하세요", type="txt", key="uploader")

# 자바스크립트로 전달할 파일 데이터 준비
file_name = ""
content = ""
if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")

# 2. 소설 목록과 본문이 그려질 HTML 뼈대 미리 생성 (파이썬 세션 간섭 배제)
list_placeholder = st.empty()
body_placeholder = st.empty()

# 👑 [스마트폰 본체 영구 결속형 자바스크립트 엔진]
# 파이썬을 거치지 않고 오직 폰 내부 데이터(localStorage)로만 구동하여 앱 종료 충돌을 원천 봉쇄합니다.
js_engine = f"""
<script>
(function() {{
    const dbKey = "novel_library_permanent_db";
    const currentKey = "novel_current_selected_title";
    const scrollPrefix = "novel_scroll_pos_";
    const targetWindow = window.top || window;

    // A. [새 파일 저장 프로세스]
    const upTitle = "{file_name}";
    const upContent = `{content}`;
    
    if (upTitle && upContent.trim() !== "") {{
        let db = JSON.parse(targetWindow.localStorage.getItem(dbKey)) || {{}};
        db[upTitle] = upContent;
        targetWindow.localStorage.setItem(dbKey, JSON.stringify(db));
        targetWindow.localStorage.setItem(currentKey, upTitle);
        targetWindow.localStorage.setItem(scrollPrefix + upTitle, "0");
    }}

    // B. [목록 클릭 & 삭제 함수 글로벌 등록]
    window.selectNovel = function(title) {{
        targetWindow.localStorage.setItem(currentKey, title);
        window.location.reload(); 
    }};

    window.deleteNovel = function(title) {{
        if(confirm("이 소설을 책장에서 삭제할까요?")) {{
            let db = JSON.parse(targetWindow.localStorage.getItem(dbKey)) || {{}};
            delete db[title];
            targetWindow.localStorage.setItem(dbKey, JSON.stringify(db));
            if(targetWindow.localStorage.getItem(currentKey) === title) {{
                targetWindow.localStorage.removeItem(currentKey);
            }}
            window.location.reload();
        }}
    }};

    // C. [화면에 책장 목록 UI 출력]
    const db = JSON.parse(targetWindow.localStorage.getItem(dbKey)) || {{}};
    const current = targetWindow.localStorage.getItem(currentKey);
    const titles = Object.keys(db);

    let listHtml = "<h3>📖 나의 소설 목록</h3>";
    if (titles.length === 0) {{
        listHtml += "<p style='color:#888; font-size:14px;'>책장이 비어 있습니다. 소설 파일을 올려주세요.</p>";
    }} else {{
        listHtml += "<div style='margin-bottom:20px;'>";
        titles.forEach(t => {{
            const isActive = (t === current);
            const btnStyle = isActive 
                ? "width:80%; text-align:left; padding:12px; font-size:15px; border-radius:6px; background:#8B5A2B; color:white; font-weight:bold; border:none; cursor:pointer;" 
                : "width:80%; text-align:left; padding:12px; font-size:15px; border-radius:6px; background:#EFE9D9; color:#333; border:1px solid #D1C9B7; cursor:pointer;";
            
            listHtml += `
                <div style="display:flex; justify-content:between; align-items:center; margin-bottom:8px;">
                    <button onclick="window.selectNovel('${{t}}')" style="${{btnStyle}}">
                        ${{isActive ? '▶ ' : '📄 '}}${{t}}
                    </button>
                    <button onclick="window.deleteNovel('${{t}}')" style="width:18%; margin-left:2%; background:#E57373; color:white; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold;">❌</button>
                </div>
            `;
        }});
        listHtml += "</div>";
    }}
    
    const listDiv = parent.document.getElementById("novel-list-ui");
    if (listDiv) listDiv.innerHTML = listHtml;

    // D. [본문 주입 및 이어읽기 스크롤 작동]
    if (current && db[current]) {{
        const bodyDiv = parent.document.getElementById("novel-text-ui");
        if (bodyDiv) {{
            bodyDiv.innerText = db[current];
            bodyDiv.style.fontSize = "{font_size}px";
            
            // 본문이 노출된 직후 예전 스크롤 위치 복원
            setTimeout(() => {{
                const savedScroll = targetWindow.localStorage.getItem(scrollPrefix + current);
                if (savedScroll) {{
                    targetWindow.scrollTo(0, parseInt(savedScroll));
                }}
            }}, 200);
        }}
    }}

    // E. [실시간 스크롤 트래킹]
    targetWindow.addEventListener('scroll', () => {{
        const activeTitle = targetWindow.localStorage.getItem(currentKey);
        if (activeTitle) {{
            targetWindow.localStorage.setItem(scrollPrefix + activeTitle, targetWindow.scrollY);
        }}
    }}, {{ passive: true }});

}})();
</script>
"""

# 화면 구역 설정 및 자바스크립트 엔진 강제 주입
list_placeholder.markdown('<div id="novel-list-ui">목록 로딩 중...</div>', unsafe_allow_html=True)
st.write("---")
body_placeholder.markdown('<div id="novel-text-ui" class="novel-text" style="text-align:center; color:#999; margin-top:20px;">읽을 소설을 선택해 주세요.</div>', unsafe_allow_html=True)
st.markdown(js_engine, unsafe_allow_html=True)
