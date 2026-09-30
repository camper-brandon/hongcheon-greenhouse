# -*- coding: utf-8 -*-
"""모델 → 3D 뷰어용 JSON.  부재마다 이름 · 부재번호 · 재료 · 층 · 조립 단계 · 단면 꼭짓점 (앞 절반 / 뒤 절반)
   + 참고 부재 (난로 · 단 · 연통 · 내부 방화판) — 모델에 없는 가정값.  이름에 (가정) 을 붙인다."""
import sys, os, json
SP = r'D:\Doc\박수민\텃밭_화단\온실_도면_R12_단층쫄대\_생성스크립트'
sys.path.insert(0, SP)
os.chdir(SP)
sys.stdout.reconfigure(encoding='utf-8')
import geo as G
import pn
import cad as C

LAYER = [
    ('기초 각관', ('각관',)),
    ('토대 · 밑깔도리', ('토대', '밑깔도리')),
    ('벽 골조', ('측벽스터드', '킹스터드', '잭스터드', '창밑스터드', '박공스터드', '박공끝스터드',
                 '벽블로킹', '창헤더', '문헤더', '문헤더덮개', '창턱', '박공가로재', '위깔도리', '겹깔도리',
                 '배기잭스터드', '배기헤더', '개구턱', '환풍채움')),
    ('박공 삼각부', ('박공상부', '마룻대받침')),
    ('지붕 골조', ('마룻대', '서까래', '칼라타이', '지붕블로킹', '처마막이')),
    ('가새', ('가새',)),
    ('쫄대', ('지붕쫄대', '벽쫄대', '박공쫄대', '박공모서리쫄대', '창옆쫄대')),
    ('폴리카 · 판', ('지붕판', '벽판', '박공판')),
    ('창 · 문 · 방충망', ('창짝', '프로젝트창', '문짝', '배기창', '방충망')),
    ('철물', ('아이볼트', '앵커')),
    ('참고 · 난로 (가정)', ('참고',)),
]

#  조립 단계 — WI 공정 번호에 맞춘다 (1 각관 · 2 앵커 · 3 토대·밑깔도리 · 4 측벽 골조 · 6 박공 · 7 겹깔도리 · 8 가새 · 9 마룻대 · 10 서까래 · 11 칼라타이)
#  12 이후는 아직 WI 가 없다 — 쫄대 · 판 · 창호 · 철물 순으로 둔다
STEP = [
    (1, '각관 프레임', ('각관',)),
    (2, '앵커', ('앵커',)),
    (3, '토대 · 밑깔도리', ('토대', '밑깔도리')),
    (4, '측벽 골조 (앞 · 뒤)', ('측벽스터드', '킹스터드-앞', '킹스터드-뒤', '잭스터드-앞', '잭스터드-뒤', '창밑스터드', '벽블로킹',
                               '창헤더-앞', '창헤더-뒤', '위깔도리-앞', '위깔도리-뒤')),
    (6, '박공벽 (문 · 창)', ('박공스터드', '박공끝스터드', '박공가로재', '킹스터드-좌', '잭스터드-좌', '문헤더', '문헤더덮개',
                            '창헤더-우', '위깔도리-좌', '위깔도리-우', '박공상부', '배기잭스터드', '배기헤더', '개구턱', '환풍채움', '마룻대받침')),
    (7, '겹깔도리 (2겹)', ('겹깔도리',)),
    (8, '가새 (스트랩)', ('가새',)),
    (9, '마룻대', ('마룻대-좌', '마룻대-우')),
    (10, '서까래', ('서까래',)),
    (11, '칼라타이 · 지붕블로킹 · 처마막이', ('칼라타이', '지붕블로킹', '처마막이')),
    (12, '폴리카 · 시멘트보드 (판 먼저)', ('지붕판', '벽판', '박공판')),
    (13, '쫄대 (판을 누른다)', ('지붕쫄대', '벽쫄대', '박공쫄대', '박공모서리쫄대', '창옆쫄대')),
    (14, '창 · 문 · 방충망 · 아이볼트', ('창짝', '프로젝트창', '문짝', '배기창', '방충망', '아이볼트')),
    (15, '참고 (난로 · 단)', ('참고',)),
]


def layer_of(n):
    for i, (_lab, pfx) in enumerate(LAYER):
        if n.startswith(pfx):
            return i
    return -1


def step_of(n):
    for i, (_no, _lab, pfx) in enumerate(STEP):
        if n.startswith(pfx):
            return i
    return len(STEP) - 1


def size_of(r):
    m = r['m']
    if '2x4' in m:
        return '2×4'
    if '2x6' in m:
        return '2×6'
    if '각관' in m:
        return '각관 50×50'
    if '스트랩' in m:
        return '스트랩 30×1.2T'
    if '쫄대' in m:
        return '쫄대 15×38'
    if '10T' in m:
        return '복층 폴리카 10T'
    if '폴리카' in m:
        return '폴리카 4.5T'
    if '시멘트' in m:
        return '시멘트보드 9T'
    return m


def boxv(x0, x1, y0, y1, z0, z1):
    """상자 꼭짓점 — x 방향으로 뽑은 기둥 (앞 절반 x0 면, 뒤 절반 x1 면)"""
    a = [[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]]
    b = [[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]]
    return a + b


parts = []
for n, r in G.D.items():
    if not r['m'] or n not in G.V:
        continue
    li = layer_of(n)
    if li < 0:
        continue
    V = G.V[n]
    k = len(V) // 2
    p = pn.OF.get(n, '')
    L_ = pn.TYP[p]['L'] if p in pn.TYP else None
    parts.append(dict(n=n, p=p, L=L_, m=r['m'], s=size_of(r), l=li, st=step_of(n), k=k,
                      v=[[round(a, 1), round(b, 1), round(c, 1)] for a, b, c in V]))

L = G.D['각관-우']['x1']
W = G.D['각관-뒤']['y1']
D = 89.0
GL = G.GL

# ── 참고 부재 (가정 · 모델 밖) ──────────────────────────────
#  난로 = 미니맥스 MX9 410×330×430 (무신사 등록값).  단 깊이 950 · 높이 450 (판석 위) 는 제안값.
#  난로 뒷면 ~ 벽 안면 600 (NFPA 211 식 이격 계산 · 아래 대화 참조).  연통 지름 80 은 가정 (MX9 미확인).
XI = L - D                      # 북쪽 벽 안면 5,049
PL_D, PL_H = 950.0, 450.0
ST_W, ST_D, ST_H = 410.0, 330.0, 430.0
BACK = 600.0
FL = 80.0
ref = []
ref.append(('참고 · 단 (장작 칸 · 깊이 950 · 높이 450 — 제안)', '참고', boxv(XI - PL_D, XI, D, W - D, GL, GL + PL_H)))
sx1 = XI - BACK
sx0 = sx1 - ST_D
sy0, sy1 = W / 2 - ST_W / 2, W / 2 + ST_W / 2
sz0 = GL + PL_H
ref.append(('참고 · 난로 MX9 410×330×430 (무신사 등록값 · 뒷면~벽 600)', '참고', boxv(sx0, sx1, sy0, sy1, sz0, sz0 + ST_H)))
cx, cy = (sx0 + sx1) / 2, W / 2
FLZ = 1800.0
ref.append(('참고 · 연통 세로 (지름 80 가정) · 벽 관통 1,800', '참고', boxv(cx - FL / 2, cx + FL / 2, cy - FL / 2, cy + FL / 2, sz0 + ST_H, FLZ + FL / 2)))
ref.append(('참고 · 연통 가로 (지름 80 가정) → 벽 밖 150', '참고', boxv(cx - FL / 2, L + 150 + FL, cy - FL / 2, cy + FL / 2, FLZ - FL / 2, FLZ + FL / 2)))
ref.append(('참고 · 연통 바깥 세로 (가정) · 벽에서 150 띄움', '참고', boxv(L + 150, L + 150 + FL, cy - FL / 2, cy + FL / 2, FLZ - FL / 2, G.ROOFTOP + 600)))
#  내부 방화판 — 스터드 안면에서 25 띄운 시멘트보드 9T (pn 주기).  폭 = 바깥 방화판 3칸 (701~2,499)
ref.append(('참고 · 내부 방화판 9T (스터드 안면에서 25 띄움 · 3칸 1,798)', '참고', boxv(XI - 25 - 9, XI - 25, 701.0, 2499.0, sz0, 2600.0)))
for nm, m, v in ref:
    parts.append(dict(n=nm, p='', L=None, m=m, s='참고 (가정)', l=layer_of('참고'), st=step_of('참고'), k=4, v=v))

out = dict(rev=C.REV, date=C.DATE, L=L, W=W, apex=G.APEX, top=G.ROOFTOP, gl=GL,
           wall=G.D['겹깔도리-앞a']['z1'], layers=[lab for lab, _ in LAYER],
           steps=[dict(no=no, lab=lab) for no, lab, _ in STEP], parts=parts)
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model3d.json')
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('parts', len(parts), 'bytes', os.path.getsize(dst))
