# 파일명: app.py
import streamlit as st

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
    div[data-testid="stColumn"] {
        display: flex;
        align-items: center;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault()); /* 우클릭 금지 */
    </script>
""", unsafe_allow_html=True)

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 1. 파일 업로드 칸 (상시 노출 및 연속 추가 가능)
uploaded_file = st.file_uploader("여기에 txt 파일을 올리면 책장에 등록됩니다.", type="txt", key="novel_uploader")

if uploaded_file is not None:
    file_name = uploaded_file.name
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    # 🌟 [서버 귀속 탈피] 서버가 아닌 폰 하드웨어 영구 기억 장치에 즉시 박아버립니다.
    escaped_content = content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    st.markdown(f"""
        <script>
        (function() {{
            const win = window.top || window;
            localStorage.setItem("novel_file_" + "{file_name}", `{escaped_content}`);
            
            // 파일 목록 리스트 업데이트
            let list = JSON.parse(localStorage.getItem("novel_list_v12")) || [];
            if (!list.includes("{file_name}")) {{
                list.push("{file_name}");
                localStorage.setItem("novel_list_v12", JSON.stringify(list));
            }}
            
            // 새로고침하여 목록에 즉시 반영
            win.location.reload();
        }})();
        </script>
    """, unsafe_allow_html=True)

st.write("### 📖 나의 소설 목록")

# 2. 👑 [핵심] 서버 메모리를 쓰지 않고, 폰 저장소에서 실시간으로 목록과 본문을 제어하는 자바스크립트 엔진
# 이 방식을 쓰면 서버가 꺼지든 켜지든 내 폰이 기억장치가 되므로 절대 데이터가 안 지워집니다.
st.markdown("""
<div id="bookshelf-container">목록을 불러오는 중입니다...</div>
<div id="novel-display-section" style="display:none; margin-top:30px;">
    <hr>
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <h4 id="reading-title" style="margin:0;">📖 현재 읽는 중</h4>
        <button onclick="closeNovel()" style="padding:6px 12px; background:#e0e0e0; border:none; border-radius:4px; cursor:pointer;">🙈 독서 종료 (닫기)</button>
    </div>
    <div id="novel-body-text" class="novel-text"></div>
</div>

<script>
(function() {
    const win = window.top || window;
    
    // 화면 그리기 함수
    window.renderBookshelf = function() {
        const list = JSON.parse(localStorage.getItem("novel_list_v12")) || [];
        const container = document.getElementById("bookshelf-container");
        
        if (list.length === 0) {
            container.innerHTML = '<div style="color:#888; text-align:center; padding:20px;">책장이 비어 있습니다. 위의 업로드 칸에 소설을 올려 채워보세요!</div>';
            return;
        }
        
        let html = '<table style="width:100%; border-collapse:collapse;">';
        list.forEach((title, idx) => {
            html += `
            <tr style="border-bottom:1px solid #ddd;">
                <td style="padding:10px 0;" class="novel-title-text">📄 ${title}</td>
                <td style="text-align:right; padding:10px 0;">
                    <button onclick="loadNovel('${title}')" style="padding:6px 12px; background:#4CAF50; color:white; border:none; border-radius:4px; margin-right:5px; cursor:pointer;">▶ 이어 읽기</button>
                    <button onclick="deleteNovel('${title}')" style="padding:6px 10px; background:#f44336; color:white; border:none; border-radius:4px; cursor:pointer;">❌</button>
                </td>
            </tr>`;
        });
        html += '</table>';
        container.innerHTML = html;
    };

    // 소설 본문 불러오기 및 스크롤 복원
    window.loadNovel = function(title) {
        const content = localStorage.getItem("novel_file_" + title);
        if (!content) return;
        
        localStorage.setItem("novel_current_v12", title);
        
        document.getElementById("reading-title").innerText = "📖 현재 읽는 중: " + title;
        const bodyArea = document.getElementById("novel-body-text");
        bodyArea.innerText = content;
        
        // 글자 크기 실시간 동기화 적용
        const slider = parent.document.querySelector('div[data-testid="stSlider"] input');
        if(slider) {
            bodyArea.style.fontSize = parent.document.querySelector('.stSlider').innerText.match(/\\d+pt/)?.[0] || "16px";
        }
        
        document.getElementById("novel-display-section").style.display = "block";
        
        // 읽던 위치로 자동 스크롤 점프
        setTimeout(() => {
            const savedY = localStorage.getItem("novel_scroll_" + title);
            if (savedY) win.scrollTo(0, parseInt(savedY));
        }, 100);
    };

    // 닫기 기능
    window.closeNovel = function() {
        localStorage.removeItem("novel_current_v12");
        document.getElementById("novel-display-section").style.display = "none";
        win.scrollTo(0, 0);
    };

    // 삭제 기능
    window.deleteNovel = function(title) {
        if (confirm("이 소설을 책장에서 삭제할까요?")) {
            let list = JSON.parse(localStorage.getItem("novel_list_v12")) || [];
            list = list.filter(t => t !== title);
            localStorage.setItem("novel_list_v12", JSON.stringify(list));
            localStorage.removeItem("novel_file_" + title);
            localStorage.removeItem("novel_scroll_" + title);
            
            if (localStorage.getItem("novel_current_v12") === title) {
                localStorage.removeItem("novel_current_v12");
                document.getElementById("novel-display-section").style.display = "none";
            }
            renderBookshelf();
        }
    };

    // 스크롤 할 때마다 실시간 위치를 폰에 기억
    win.addEventListener('scroll', () => {
        const currentTitle = localStorage.getItem("novel_current_v12");
        if (currentTitle) {
            localStorage.setItem("novel_scroll_" + currentTitle, win.scrollY);
        }
    }, { passive: true });

    // 실행 시 목록 렌더링 및 읽던 소설 자동 복원
    setTimeout(() => {
        renderBookshelf();
        const cur = localStorage.getItem("novel_current_v12");
        if (cur) loadNovel(cur);
    }, 200);

})();
</script>
""", unsafe_allow_html=True)
