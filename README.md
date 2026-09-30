# 홍천 목조 온실 · 골조 3D

`index.html` 한 장짜리 three.js 뷰어. 부재 데이터(`model3d.json`)는 도면 생성 스크립트(`gen.py` → `geo.py`)에서 `export3d.py` 로 뽑아 HTML 안에 넣는다.

- 만들기: `python export3d.py` → `viewer_tpl.html` 의 `__MODEL__` 자리에 JSON 을 넣어 `index.html` 로 저장
- 조작: 드래그 회전 · 휠 확대 · 우클릭/Shift 드래그 이동 · 부재 클릭 = 고정 표시 · 두 번 클릭 = 그 부재로 중심
- 층 켜고 끄기 · 조립 순서 슬라이더 · x/y 단면 자르기 · 부재 이름/번호 검색 · 직교 투영 · 전체 치수
