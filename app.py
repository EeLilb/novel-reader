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
        color: #333333;
    }
    /* 커스텀 업로드 버튼 스타일 */
    .custom-upload-btn {
        display: block;
        width: 100%;
        padding: 15px;
        background-color: #ffffff;
        border: 2px dashed #bdc3c7;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        font-weight: bold;
        margin-bottom: 20px;
        color: #555;
    }
    .custom-upload-btn:hover {
        background-color: #f8f9fa;
        border-color: #3498db;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault()); /* 우클릭 금지 */
    </script>
""", unsafe_allow_html=True)

st.title("📚 내 방구석 비밀 책장")
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)
st.write("---")

# 👑 파이썬과 자바스크립트 문자열 충돌을 해결하기 위해 r"""을 사용하여 안전하게 감싸줌
st.markdown(r"""
<label for="hidden-uploader" class="custom-upload-btn" id="upload-label">
    📁 여기에 txt 파일을 올리면 책장에 등록됩니다 (연속 가능)
</label>
<input type="file" id="hidden-uploader" accept=".txt" style="display:none;" onchange="handleFileUpload(this)">

<style>
.close-btn {
    padding: 6px 12px;
    background-color: #e0e0e0;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}
.resume-btn {
    padding: 6px 12px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    margin-right: 5px;
    cursor: pointer;
}
.del-btn {
    padding: 6px 10px;
    background-color: #f44336;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style>

<div id="bookshelf-container">목록을 불러오는 중입니다...</div>

<div id="novel-display-section" style="display:none; margin-top:30px;">
    <hr>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
        <h4 id="reading-title" style="margin:0;">📖 현재 읽는 중</h4>
        <button onclick="closeNovel()" class="close-btn">🙈 독서 종료 (닫기)</button>
    </div>
    <div id="novel-body-text" class="novel-text"></div>
</div>

<script>
(function() {
    const win = window.top || window;
    
    // 1. 파일 업로드 직접 처리 (폰에 다이렉트 저장)
    window.handleFileUpload = function(input) {
        const file = input.files[0];
        if (!file) return;
        
        const label = document.getElementById("upload-label");
        label.innerText = "⚡ 소설 분석 및 책장 등록 중...";
        
        const reader = new FileReader();
        
        reader.onload = function(e) {
            let text = e.target.result;
            const fileName = file.name;
            
            // 스마트폰 로컬 저장소에 다이렉트 영구 저장
            localStorage.setItem("novel_file_" + fileName, text);
            
            let list = JSON.parse(localStorage.getItem("novel_list_v13")) || [];
            if (!list.includes(fileName)) {
                list.push(fileName);
                localStorage.setItem("novel_list_v13", JSON.stringify(list));
            }
            
            input.value = "";
            label.innerText = "📁 여기에 txt 파일을 올리면 책장에 등록됩니다 (연속 가능)";
            
            renderBookshelf();
        };
        
        reader.readAsText(file, "UTF-8");
    };

    // 2. 책장 목록 화면에 그리기
    window.renderBookshelf = function() {
        const list = JSON.parse(localStorage.getItem("novel_list_v13")) || [];
        const container = document.getElementById("bookshelf-container");
        
        if (list.length === 0) {
            container.innerHTML = '<div style="color:#888; text-align:center; padding:20px; border:1px dashed #ddd; border-radius:6px;">책장이 비어 있습니다. 위의 업로드 칸에 소설을 올려 채워보세요!</div>';
            return;
        }
        
        let html = '<table style="width:100%; border-collapse:collapse; margin-top:10px;">';
        list.forEach((title) => {
            html += `
            <tr style="border-bottom:1px solid #eef0f2;">
                <td style="padding:12px 5px;" class="novel-title-text">📄 ${title}</td>
                <td style="text-align:right; padding:12px 5px; white-space:nowrap;">
                    <button onclick="loadNovel('${title}')" class="resume-btn">▶ 이어 읽기</button>
                    <button onclick="deleteNovel('${title}')" class="del-btn">❌</button>
                </td>
            </tr>`;
        });
        html += '</table>';
        container.innerHTML = html;
    };

    // 3. 소설 본문 열기 및 스크롤 자동 복원
    window.loadNovel = function(title) {
        const content = localStorage.getItem("novel_file_" + title);
        if (!content) return;
        
        localStorage.setItem("novel_current_v13", title);
        
        document.getElementById("reading-title").innerText = "📖 현재 읽는 중: " + title;
        const bodyArea = document.getElementById("novel-body-text");
        bodyArea.innerText = content;
        
        // 슬라이더 바 값 추출하여 실시간 폰트 크기 변경
        try {
            const sliderText = parent.document.querySelector('.stSlider').innerText;
            const match = sliderText.match(/\d+/);
            if(match) bodyArea.style.fontSize = match[0] + "px";
        } catch(e) {
            bodyArea.style.fontSize = "16px";
        }
        
        document.getElementById("novel-display-section").style.display = "block";
        
        // 읽던 스크롤 좌표로 자동 차원 이동
        setTimeout(() => {
            const savedY = localStorage.getItem("novel_scroll_" + title);
            if (savedY) win.scrollTo(0, parseInt(savedY));
        }, 80);
    };

    // 4. 본문 닫기
    window.closeNovel = function() {
        localStorage.removeItem("novel_current_v13");
        document.getElementById("novel-display-section").style.display = "none";
        win.scrollTo(0, 0);
    };

    // 5. 책장에서 제거
    window.deleteNovel = function(title) {
        if (confirm("이 소설을 책장에서 영구히 삭제할까요?")) {
            let list = JSON.parse(localStorage.getItem("novel_list_v13")) || [];
            list = list.filter(t => t !== title);
            localStorage.setItem("novel_list_v13", JSON.stringify(list));
            localStorage.removeItem("novel_file_" + title);
            localStorage.removeItem("novel_scroll_" + title);
            
            if (localStorage.getItem("novel_current_v13") === title) {
                localStorage.removeItem("novel_current_v13");
                document.getElementById("novel-display-section").style.display = "none";
            }
            renderBookshelf();
        }
    };

    // 6. 사용자가 읽으면서 내리는 스크롤 실시간 위치 기억
    win.addEventListener('scroll', () => {
        const currentTitle = localStorage.getItem("novel_current_v13");
        if (currentTitle) {
            localStorage.setItem("novel_scroll_" + currentTitle, win.scrollY);
        }
    }, { passive: true });

    // 처음 앱 실행 시 세팅 구동
    setTimeout(() => {
        render
