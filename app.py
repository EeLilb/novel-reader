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

# 👑 [전면 개정] 파이썬 격리 벽을 깨부수고, 모든 처리를 스마트폰 본체 내부에서 처리하는 단일 엔진
st.markdown("""
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
    
    // 1. 파일 업로드 직접 처리 (파이썬 무시하고 폰에 다이렉트 저장)
    window.handleFileUpload = function(input) {
        const file = input.files[0];
        if (!file) return;
        
        const label = document.getElementById("upload-label");
        label.innerText = "⚡ 소설 분석 및 책장 등록 중...";
        
        const reader = new FileReader();
        
        // 인코딩 자동 감지 기능 탑재 (UTF-8 및 한국어 기동)
        reader.onload = function(e) {
            let text = e.target.result;
            const fileName = file.name;
