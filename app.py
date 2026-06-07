# 파일명: app.py
import streamlit as st

# 웹 페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="방구석 텍스트 뷰어", layout="centered")

# 웹소설 감성의 스타일 지정 (가독성 높은 서체와 줄간격)
st.markdown("""
    <style>
    .novel-text {
        line-height: 1.8;
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        padding: 15px;
        white-space: pre-wrap; /* 줄바꿈 유지 */
    }
    /* 스마트폰에서 보기 편하도록 배경색을 살짝 아늑한 미색으로 지정 */
    .stApp {
        background-color: #F9F5EA;
        color: #2B2B2B;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📚 방구석 아늑한 책장")
st.write("스마트폰에서도 편하게 읽을 수 있는 조그마한 책장입니다.")

# 파일 업로드 컴포넌트 (스마트폰에서도 터치하면 파일 선택창이 뜹니다)
uploaded_file = st.file_uploader("텍스트(.txt) 파일을 선택하세요", type="txt")

# 글자 크기 조절 슬라이더 (기본값 16pt 설정)
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)

st.write("---")

if uploaded_file is not None:
    # 한글 깨짐 방지를 위한 디코딩 처리
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    # 본문 출력 (선택한 글자 크기 반영)
    st.markdown(f'<div class="novel-text" style="font-size: {font_size}px;">{content}</div>', unsafe_allow_html=True)
else:
    st.info("텍스트 파일을 업로드하면 이곳에 본문이 나타납니다.")
