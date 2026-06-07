# 파일명: app.py
import streamlit as st

# 웹 페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="방구석 소설 뷰어", layout="centered")

# 1. CSS를 이용한 미색 테마 및 드래그(드래그/복사/우클릭) 금지 설정
st.markdown("""
    <style>
    /* 소설 본문 스타일 및 드래그 방지 */
    .novel-text {
        line-height: 1.8;
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        padding: 15px;
        white-space: pre-wrap; /* 줄바꿈 유지 */
        
        /* 드래그 및 블록 지정 금지 */
        -webkit-user-select: none; /* Safari */
        -moz-user-select: none;    /* Firefox */
        -ms-user-select: none;     /* IE/Edge */
        user-select: none;         /* Standard */
    }
    /* 스마트폰에서 보기 편하도록 배경색을 살짝 아늑한 미색으로 지정 */
    .stApp {
        background-color: #F9F5EA;
        color: #2B2B2B;
    }
    </style>
    
    <script>
    /* 마우스 우클릭 방지 */
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
""", unsafe_allow_html=True)

st.title("📚 방구석 웹소설 뷰어")
st.write("txt 파일을 읽을 수 있는, 이어읽기 기능이 포함된 개인 뷰어입니다.")

# 파일 업로드 컴포넌트
uploaded_file = st.file_uploader("소설 텍스트(.txt) 파일을 선택하세요", type="txt")

# 글자 크기 조절 슬라이더 (기본값 16pt 설정)
font_size = st.slider("글자 크기 조절 (pt)", min_value=14, max_value=30, value=16, step=1)

st.write("---")

if uploaded_file is not None:
    # 파일 이름에 맞게 각각 스크롤 위치를 따로 저장하기 위해 파일명 추출
    file_name = uploaded_file.name
    
    # 한글 깨짐 방지를 위한 디코딩 처리
    try:
        bytes_data = uploaded_file.getvalue()
        content = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        content = bytes_data.decode("cp949", errors="ignore")
    
    # 본문 출력 (선택한 글자 크기 반영)
    st.markdown(f'<div id="novel-container" class="novel-text" style="font-size: {font_size}px;">{content}</div>', unsafe_allow_html=True)
    
    # 2. 자바스크립트를 활용한 스크롤 위치 기억 및 자동 복원 시스템
    # 파일별로 읽던 위치를 기억하도록 브라우저 스토리지에 세팅합니다.
    js_scroll_script = f"""
    <script>
    const storageKey = "scroll_pos_" + "{file_name}";
    
    // 1) 저장된 스크롤 위치가 있다면 해당 위치로 화면을 강제 이동
    setTimeout(() => {{
        const savedPos = localStorage.getItem(storageKey);
        if (savedPos) {{
            window.scrollTo({{
                top: parseInt(savedPos),
                behavior: 'smooth'
            }});
        }}
    }}, 500); // 본문이 로드되는 시간을 벌기 위해 0.5초 딜레이를 줍니다.

    // 2) 사용자가 스크롤을 움직일 때마다 실시간으로 위치 저장
    window.addEventListener('scroll', () => {{
        localStorage.setItem(storageKey, window.scrollY);
    }});
    </script>
    """
    st.markdown(js_scroll_script, unsafe_allow_html=True)

else:
    st.info("텍스트 파일을 업로드하면 이곳에 소설 본문이 나타납니다.")
