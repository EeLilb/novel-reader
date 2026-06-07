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
    /* 책장 버튼 스타일 */
    .stButton>button {
        width: 100%;
        text-align: left;
        margin-bottom: 5px;
        background-color: #EFE9D9;
        color: #333;
        border: 1px solid #D1C9B7;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
""", unsafe_allow_html=True)

st.title("📚 내 방구석 비밀 책장")

# 글자 크기 조절 (상단 고정)
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)

st.write("---")

# 1. 사이드바 또는 상단에 '새 소설 추가하기' 섹션 생성
with st.expander("➕ 여기에 새 소설 파일 추가하기 (터치)", expanded=False):
    uploaded_file = st.file_uploader("텍스트(.txt) 파일을 선택하세요", type="txt")

# 파이썬 내부 변수 준비
content = ""
file_name = ""

if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")

st.write("### 📖 나의 소설 목록")
# 소설 목록과 현재 본문이 표시될 공간 확보
list_placeholder = st.empty()
novel_placeholder = st.empty()

# 👑 [책장 시스템 자바스크립트 엔진]
# 스마트폰 저장소에 '소설 목록 데이터베이스'를 구축하여 앱을 완전히 껐다 켜도 유지시킵니다.
js_script = f"""
<script>
(function() {{
    const listKey = "novel_library_list"; // 소설 목록 DB 키
    const currentKey = "novel_current_reading"; // 현재 읽고 있는 소설 이름 키
    const scrollPrefix = "novel_scroll_"; // 스크롤 위치 키 접두사
    const targetWindow = window.top || window;

    // 1) [새 파일 업로드 처리]
    const newTitle = "{file_name}";
    const newContent = `{content}`;
    
    if (newTitle && newContent.trim() !== "") {{
        // 기존 목록 가져오기 없으면 생성
        let library = JSON.parse(targetWindow.localStorage.getItem(listKey)) || {{}};
        // 목록에 새 소설 추가 (중복되면 덮어씀)
        library[newTitle] = newContent;
        targetWindow.localStorage.setItem(listKey, JSON.stringify(library));
        // 현재 읽는 소설을 방금 올린 소설로 지정
        targetWindow.localStorage.setItem(currentKey, newTitle);
        // 새 파일이므로 스크롤 기록은 0으로 세팅
        targetWindow.localStorage.setItem(scrollPrefix + newTitle, "0");
    }}

    // 2) [화면에 소설 목록 및 본문 그려주기]
    const library = JSON.parse(targetWindow.localStorage.getItem(listKey)) || {{}};
    const currentReading = targetWindow.localStorage.getItem(currentKey);
    
    // 사용자가 목록에서 소설을 클릭했을 때 호출될 함수 정의
    window.selectNovel = function(title) {{
        targetWindow.localStorage.setItem(currentKey, title);
        window.location.reload(); // 강제 새로고침하여 본문 교체 및 스크롤 복원 트리거
    }};

    // 사용자가 목록에서 소설을 삭제하고 싶을 때 호출될 함수
    window.deleteNovel = function(title) {{
        if(confirm("이 소설을 책장에서 삭제할까요?")) {{
            let lib = JSON.parse(targetWindow.localStorage.getItem(listKey)) || {{}};
            delete lib[title];
            targetWindow.localStorage.setItem(listKey, JSON.stringify(lib));
            if(targetWindow.localStorage.getItem(currentKey) === title) {{
                targetWindow.localStorage.removeItem(currentKey);
            }}
            window.location.reload();
        }}
    }};

    // HTML로 책장 버튼 목록 만들기
    let listHtml = '<div style="margin-bottom: 20px; padding: 10px; background: #EFE9D9; border-radius: 8px;">';
    const titles = Object.keys(library);
    if (titles.length === 0) {{
        listHtml += '<p style="color: #666; font-size:14px;">책장이 비어 있습니다. 위의 추가 버튼을 눌러 소설을 넣어주세요.</p>';
    }} else {{
        titles.forEach(title => {{
            const activeStyle = (title === currentReading) ? "font-weight: bold; border: 2px solid #8B5A2B;" : "";
            listHtml += `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <button onclick="window.selectNovel('${{title}}')" style="flex-grow: 1; text-align: left; padding: 10px; font-size:15px; border-radius: 5px; cursor: pointer; ${{activeStyle}}">
                        ${{title === currentReading ? '▶ ' : ''}}${{title}}
                    </button>
                    <button onclick="window.deleteNovel('${{title}}')" style="margin-left: 5px; background: #E57373; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer;">❌</button>
                </div>
            `;
        }});
    }}
    listHtml += '</div>';
    
    // 파이썬 영역에 HTML 목록 주입
    const listDiv = parent.document.getElementById("novel-list-area");
    if (listDiv) listDiv.innerHTML = listHtml;

    // 3) [현재 읽는 소설 본문 띄우기 및 스크롤 복원]
    if (currentReading && library[currentReading]) {{
        const textDiv = parent.document.getElementById("novel-body-area");
        if (textDiv) {{
            textDiv.innerText = library[currentReading];
            textDiv.style.fontSize = "{font_size}px";
            
            // 본문이 그려진 후 읽던 위치로 스크롤 강제 이동
            setTimeout(() => {{
                const savedPos = targetWindow.localStorage.getItem(scrollPrefix + currentReading);
                if (savedPos && parseInt(savedPos) > 0) {{
                    targetWindow.scrollTo(0, parseInt(savedPos));
                }}
            }}, 250);
        }}
    }}

    // 4) [실시간 스크롤 감지 및 개별 저장]
    targetWindow.addEventListener('scroll', () => {{
        const current = targetWindow.localStorage.getItem(currentKey);
        if (current) {{
            targetWindow.localStorage.setItem(scrollPrefix + current, targetWindow.scrollY);
        }}
    }}, {{ passive: true }});
}})();
</script>
"""

# HTML 레이아웃 배치 및 자바스크립트 엔진 가동
list_placeholder.markdown('<div id="novel-list-area">목록을 불러오는 중...</div>', unsafe_allow_html=True)
novel_placeholder.markdown('<div id="novel-body-area" class="novel-text" style="text-align: center; color: #666; margin-top: 30px;">읽을 소설을 위 목록에서 선택해 주세요.</div>', unsafe_allow_html=True)
st.markdown(js_script, unsafe_allow_html=True)
