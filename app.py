# 파일명: app.py
import streamlit as st
import json

st.set_page_config(page_title="방구석 소설 뷰어", layout="centered")

# CSS: 미색 테마, 드래그/우클릭 금지 및 좌상단 닫기 버튼 고정 스타일
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
    .novel-title-text {
        font-size: 16px;
        font-weight: bold;
        line-height: 2.2;
        color: #333333;
    }
    /* 👑 좌상단 고정 닫기 버튼 스타일 */
    .fixed-close-container {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 999992;
    }
    .fixed-close-btn {
        padding: 8px 14px;
        background-color: rgba(43, 43, 43, 0.9);
        color: #F9F5EA;
        border: 1px solid #F9F5EA;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        font-size: 14px;
        transition: all 0.2s;
    }
    .fixed-close-btn:hover {
        background-color: #f44336;
        color: white;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
""", unsafe_allow_html=True)

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 파이썬 세션 상태 데이터 저장 공간 초기화
if 'server_library' not in st.session_state:
    st.session_state['server_library'] = {}
if 'current_novel' not in st.session_state:
    st.session_state['current_novel'] = None

# 🤝 [영구 저장 다리] 폰에서 긁어온 데이터를 파이썬 서버 메모리로 복원하는 통로
js_to_py_bridge = st.text_input("bridge_v14", label_visibility="collapsed", key="bridge_v14_input")

if js_to_py_bridge:
    try:
        data_pack = json.loads(js_to_py_bridge)
        if data_pack.get("db"):
            st.session_state['server_library'] = data_pack["db"]
        if st.session_state['current_novel'] is None and data_pack.get("current"):
            st.session_state['current_novel'] = data_pack["current"]
    except:
        pass

# 1. 파일 업로드 기능 (업로드 즉시 백엔드 및 프론트 동시 귀속)
uploaded_file = st.file_uploader("여기에 txt 파일을 올리면 책장에 등록됩니다.", type="txt", key="novel_uploader")

if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    # 1단계: 파이썬 서버 메모리에 우선 귀속
    st.session_state['server_library'][file_name] = content
    st.session_state['current_novel'] = file_name
    
    # 2단계: 스마트폰 하드웨어 디스크(localStorage)에 다이렉트 영구 박기
    escaped_content = content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    st.markdown(f"""
        <script>
        (function() {{
            const win = window.top || window;
            let list = JSON.parse(localStorage.getItem("final_list_v14")) || [];
            if (!list.includes("{file_name}")) {{
                list.push("{file_name}");
                localStorage.setItem("final_list_v14", JSON.stringify(list));
            }}
            localStorage.setItem("final_file_" + "{file_name}", `{escaped_content}`);
            localStorage.setItem("final_cur_v14", "{file_name}");
            localStorage.setItem("final_scroll_" + "{file_name}", "0");
            win.location.reload();
        }})();
        </script>
    """, unsafe_allow_html=True)
    
    del st.session_state["novel_uploader"]
    st.rerun()


# 2. 나의 소설 목록 UI 그리기
st.write("### 📖 나의 소설 목록")
books = st.session_state['server_library']
current = st.session_state['current_title'] = st.session_state['current_novel']

if not books:
    st.info("책장이 비어 있습니다. 위의 업로드 칸에 소설을 올려 채워보세요!")
else:
    for title in list(books.keys()):
        col1, col2, col3 = st.columns([5, 2, 1])
        
        # A. 소설제목 (누를 수 없는 깔끔한 일반 텍스트)
        is_active = (title == current)
        display_title = f"▶ {title}" if is_active else f"📄 {title}"
        col1.markdown(f'<div class="novel-title-text">{display_title}</div>', unsafe_allow_html=True)
        
        # B. [▶ 이어 읽기] 버튼
        if col2.button("▶ 이어 읽기", key=f"go_{title}"):
            st.session_state['current_novel'] = title
            st.markdown(f"""
                <script>
                localStorage.setItem("final_cur_v14", "{title}");
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
            
        # C. [❌] 영구 삭제 버튼
        if col3.button("❌", key=f"del_{title}"):
            del st.session_state['server_library'][title]
            if st.session_state['current_novel'] == title:
                st.session_state['current_novel'] = None
            
            # 폰 데이터 동시 폭파
            st.markdown(f"""
                <script>
                const win = window.top || window;
                let list = JSON.parse(localStorage.getItem("final_list_v14")) || [];
                list = list.filter(t => t !== "{title}");
                localStorage.setItem("final_list_v14", JSON.stringify(list));
                localStorage.removeItem("final_file_" + "{title}");
                localStorage.removeItem("final_scroll_" + "{title}");
                if(localStorage.getItem("final_cur_v14") === "{title}") {{
                    localStorage.removeItem("final_cur_v14");
                }}
                win.location.reload();
                </script>
            """, unsafe_allow_html=True)
            st.rerun()

st.write("---")


# 3. 소설 본문 노출 구역 및 상시 추적 제어 엔진 (r""" 생략 우회 구조)
if current and current in books:
    # 👑 [요구사항 5번] 언제 어디서든 터치할 수 있는 화면 좌상단 절대 고정 닫기 버튼 배치
    st.markdown("""
        <div class="fixed-close-container">
            <button class="fixed-close-btn" onclick="triggerClose()">🙈 닫기</button>
        </div>
        <script>
        function triggerClose() {
            localStorage.removeItem("final_cur_v14");
            const btns = parent.document.querySelectorAll('button');
            for (let b of btns) {
                if (b.innerText.includes("❌닫기백엔드")) { b.click(); break; }
            }
        }
        </script>
    """, unsafe_allow_html=True)
    
    # 파이썬 백엔드 소통용 숨겨진 버튼
    if st.button("❌닫기백엔드", key="hidden_close_trigger"):
        st.session_state['current_novel'] = None
        st.rerun()
        
    st.write(f"#### 📖 현재 읽는 중: {current}")
    novel_content = books[current]
    
    # 소설 텍스트 밀어넣기
    st.markdown(f'<div id="novel-real-view" class="novel-text" style="font-size: {font_size}px;">{novel_content}</div>', unsafe_allow_html=True)
    
    # 스크롤 정밀 트래킹 및 차원 복원 기하학 스크립트
    st.markdown(r"""
        <script>
        (function() {
            const win = window.top || window;
            const curTitle = localStorage.getItem("final_cur_v14");
            if(!curTitle) return;

            const scrollKey = "final_scroll_" + curTitle;
            
            // 0.15초 뒤 독서 기록 지점으로 화면 강제 다이렉트 텔레포트
            setTimeout(() => {
                const savedY = localStorage.getItem(scrollKey);
                if (savedY && parseInt(savedY) > 0) {
                    win.scrollTo(0, parseInt(savedY));
                } else {
                    win.scrollTo(0, 0);
                }
            }, 150);

            // 사용자가 화면을 슬라이드 할 때마다 실시간 영구 기록
            win.addEventListener('scroll', () => {
                if (localStorage.getItem("final_cur_v14") === curTitle) {
                    localStorage.setItem(scrollKey, win.scrollY);
                }
            }, { passive: true });
        })();
        </script>
    """, unsafe_allow_html=True)
else:
    st.write("<div style='text-align:center; color:#999; margin-top:30px;'>책장에서 읽을 소설의 [▶ 이어 읽기]를 터치해 주세요.</div>", unsafe_allow_html=True)


# 4. 🔗 [종합 자동 동기화 엔진] 앱을 끄거나 폰을 재부팅해도 자동 감지하여 목록을 실시간 부활시키는 다리
st.markdown(r"""
    <script>
    (function() {
        const win = window.top || window;
        const list = JSON.parse(localStorage.getItem("final_list_v14")) || [];
        const currentSelected = localStorage.getItem("final_cur_v14") || "";
        
        if (list.length > 0) {
            let localDb = {};
            list.forEach(title => {
                localDb[title] = localStorage.getItem("final_file_" + title) || "";
            });
            
            setTimeout(() => {
                const bridge = parent.document.querySelector('input[aria-label="bridge_v14"]');
                // 파이썬 메모리가 비어있거나 싱크가 안 맞을 때 자동으로 밀어넣음
                if (bridge && !bridge.value) {
                    bridge.value = JSON.stringify({ db: localDb, current: currentSelected });
                    bridge.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }, 100);
        }
    })();
    </script>
""", unsafe_allow_html=True)
