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
                 '벽블로킹', '창헤더', '문헤더', '문헤더세움', '문헤더덮개', '창턱', '박공가로재', '위깔도리', '겹깔도리',
                 '배기잭스터드', '배기헤더', '개구턱', '환풍채움', '무릎바', '끼움가새', '이음받침', '문옆가로바', '무릎받이', '가새받침')),
    ('박공 삼각부', ('박공상부', '마룻대받침')),
    ('지붕 골조', ('마룻대', '서까래', '칼라타이', '지붕블로킹', '처마막이')),
    ('가새', ('가새',)),
    ('쫄대', ('지붕쫄대', '벽쫄대', '박공쫄대', '박공모서리쫄대', '창옆쫄대')),
    ('무릎벽 외장', ('외장합판', '하우스랩', '가로쫄대', '세로쫄대', '세로사이딩', '모서리마감', '문옆마감', 'Z물끊기', '무릎벽방충망')),
    ('폴리카 · 판', ('지붕판', '벽판', '박공판')),
    ('창 · 문 · 방충망', ('창짝', '프로젝트창', '문짝', '문스토퍼', '배기창', '방충망', '창멈춤', '창턱', '물끊기')),
    ('용마루 캡 · 박공 마감', ('용마루', '폼밀폐', '박공마감판', '박공덮개')),
    ('철물', ('아이볼트', '앵커')),
    ('참고 · 난로 (가정)', ('참고',)),
]

#  조립 단계 — WI 공정 번호에 맞춘다 (1 각관 · 2 앵커 · 3 토대·밑깔도리 · 4 측벽 골조 · 6 박공 · 7 겹깔도리 · 8 가새 · 9 마룻대 · 10 서까래 · 11 칼라타이)
#  12 이후는 아직 WI 가 없다 — 쫄대 · 판 · 창호 · 철물 순으로 둔다
STEP = [
    ('1', '각관 프레임 (모서리 결속)', ('각관',)),
    ('2', '앵커 — 각관 윗면 접근구멍 28φ · 밑면 장공 32×14 · 케미칼 앙카볼트 M12 (125 로 자름 · 콘크리트 매입 70) · 너트는 각관 안에서', ('앵커',)),
    ('3', '방습재 · 토대 (각관에 나사)', ('토대',)),
    ('4', '측벽 판 눕혀 짜기 — 밑깔도리 + 스터드·킹·잭·창밑 + 블로킹 + 창헤더 + 위깔도리 (앞 · 뒤)', ('밑깔도리-앞', '밑깔도리-뒤', '측벽스터드', '킹스터드-앞', '킹스터드-뒤', '잭스터드-앞', '잭스터드-뒤', '창밑스터드', '벽블로킹', '창헤더-앞', '창헤더-뒤', '위깔도리-앞', '위깔도리-뒤', '무릎바-앞', '무릎바-뒤', '끼움가새-앞', '끼움가새-뒤', '이음받침-앞', '이음받침-뒤', '무릎받이-앞', '무릎받이-뒤')),
    ('5', '측벽 세우기 — 밑깔도리를 토대에 못 · 임시 버팀대 (말뚝)', ()),
    ('6', '박공벽 판 짜기 → 안쪽에서 들어 세우기 (밑깔도리 · 문헤더 · 배기헤더 · 마룻대받침 포함) · 끝스터드를 모서리 스터드에 면으로', ('밑깔도리-좌', '밑깔도리-우', '박공스터드', '박공끝스터드', '박공가로재', '킹스터드-좌', '잭스터드-좌', '문헤더', '문헤더세움', '문헤더덮개', '창헤더-우', '위깔도리-좌', '위깔도리-우', '박공상부', '배기잭스터드', '배기헤더', '개구턱', '환풍채움', '마룻대받침', '무릎바', '끼움가새', '이음받침', '문옆가로바', '무릎받이', '가새받침')),
    ('7', '겹깔도리 — 모서리 직교 겹침 · 이음 3,250', ('겹깔도리',)),
    ('8', '무릎벽 외장 — 합판 12T · 요철 하우스랩 · 가로 쫄대 · 세로 사이딩 · 마감 · Z 물끊기', ('외장합판', '하우스랩', '가로쫄대', '세로쫄대', '무릎벽방충망', '모서리마감', '문옆마감', '세로사이딩', 'Z물끊기')),
    ('9', '마룻대 두 토막 — 양쪽 받침 위에 · 서까래 R5 · R6 사이 이음에 덧댐판 2×4 양옆', ('마룻대-좌', '마룻대-우', '마룻대덧댐')),
    ('10', '서까래 — 양 끝 쌍부터 · 버드마우스는 겹깔도리에 · 마룻대에서 못은 좌우 엇갈려', ('서까래',)),
    ('11a', '처마막이 (2×4 세움 · 직각 472 · 깔도리 위 서까래 사이)', ('처마막이',)),
    ('11b', '지붕블로킹 (2×6 · 지붕면 직각 · 서까래 사이)', ('지붕블로킹',)),
    ('11c', '칼라타이 — 블로킹에 얹고 서까래 옆면에 나사', ('칼라타이',)),
    ('12', '벽판 · 박공판 (판 먼저 · 임시 고정)', ('벽판', '박공판')),
    ('13', '벽쫄대 · 박공쫄대 · 창옆쫄대 (판을 누른다)', ('벽쫄대', '박공쫄대', '박공모서리쫄대', '창옆쫄대')),
    ('14', '지붕판 10T (처마→마룻대 한 장 · 벽판 위를 덮는다)', ('지붕판',)),
    ('15', '지붕쫄대 · 박공판 → 용마루 캡 → 박공 덮개 · 아이볼트', ('지붕쫄대', '박공마감판', '박공덮개', '아이볼트', '폼밀폐', '용마루')),
    ('16', '창짝 · 프로젝트창 · 배기창 · 방충망 · 창 멈춤대', ('창짝', '프로젝트창', '배기창', '방충망', '창멈춤', '창턱', '물끊기')),
    ('17', '문짝 → 문스토퍼', ('문짝', '문스토퍼')),
    ('18', '참고 (난로 · 단 · 연통 80φ)', ('참고',)),
]


def layer_of(n):
    for i, (_lab, pfx) in enumerate(LAYER):
        if n.startswith(pfx):
            return i
    return -1


def step_of(n):
    for i, (_no, _lab, pfx) in enumerate(STEP):
        if pfx and n.startswith(pfx):
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
    if '시멘트 사이딩' in m:
        return '세로 시멘트 사이딩 14T (제품 확인)'
    if '내수합판' in m:
        return '외장 내수합판 12T'
    if '하우스랩' in m:
        return '요철 하우스랩'
    if '물끊기' in m:
        return '절곡 0.5T'
    if '시멘트' in m:
        return '시멘트보드 9T'
    return m


def boxv(x0, x1, y0, y1, z0, z1):
    """상자 꼭짓점 — x 방향으로 뽑은 기둥 (앞 절반 x0 면, 뒤 절반 x1 면)"""
    a = [[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]]
    b = [[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]]
    return a + b


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import halflap as HL
HLB = HL.apply(G.D, G.D['각관-우']['x1'], G.D['각관-뒤']['y1'], pn.PCIN)     # R28 반턱 · 홈 묻힘 (보기 전용)
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
    L_ = pn.cutlen(p) if p in pn.LAP or p in pn.PCW else L_             # R28 반턱 · 홈 포함 길이
    for VV in ([HL.boxverts(b) for b in HLB[n]] if n in HLB else [V]):
        parts.append(dict(n=n, p=p, L=L_, m=r['m'], s=size_of(r), l=li, st=step_of(n), k=len(VV) // 2,
                          v=[[round(a, 1), round(b, 1), round(c, 1)] for a, b, c in VV]))

L = G.D['각관-우']['x1']
W = G.D['각관-뒤']['y1']
D = 89.0
GL = G.GL

# ── 참고 부재 (가정 · 모델 밖) ──────────────────────────────
#  난로 = 미니맥스 MX9 410×330×430 (무신사 등록값).  단 깊이 950 · 높이 450 (판석 위) 는 제안값.
#  난로 뒷면 ~ 벽 안면 600 (NFPA 211 식 이격 계산).  연통 지름 80 (사용자 2026-09-30 결정 · 난로 목이 75 면 레듀서).
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
ref.append(('참고 · 연통 세로 (80φ) · 벽 관통 1,800', '참고', boxv(cx - FL / 2, cx + FL / 2, cy - FL / 2, cy + FL / 2, sz0 + ST_H, FLZ + FL / 2)))
ref.append(('참고 · 연통 가로 (80φ) → 벽 밖 150', '참고', boxv(cx - FL / 2, L + 150 + FL, cy - FL / 2, cy + FL / 2, FLZ - FL / 2, FLZ + FL / 2)))
ref.append(('참고 · 연통 바깥 세로 (80φ) · 벽에서 150 띄움', '참고', boxv(L + 150, L + 150 + FL, cy - FL / 2, cy + FL / 2, FLZ - FL / 2, G.ROOFTOP + 600)))
#  벽돌 방화벽 (R23d 제안) — 스터드 안면에서 25 띄운 벽돌 90 · 3칸 폭 1,798 · 단 위 1,100 (NFPA 211 이격 914 기하 · 벽 타이로 스터드에)
ref.append(('참고 · 벽돌 방화벽 90T (스터드 안면에서 25 띄움 · 3칸 1,798 · 단 위 1,100 — 제안)', '참고', boxv(XI - 25 - 90, XI - 25, 701.0, 2499.0, sz0, sz0 + 1100.0)))
for nm, m, v in ref:
    parts.append(dict(n=nm, p='', L=None, m=m, s='참고 (가정)', l=layer_of('참고'), st=step_of('참고'), k=4, v=v))

# ── 조립 슬라이드 · 부재 타임라인 (assembly_seq.py — 영상과 같은 순서)
import assembly_seq as AS
_seq = AS.build()
#  R28: 반턱 조각(같은 이름 여러 상자)은 타임라인에서 한 부재로 센다
_un, _first, _cum = [], {}, [0]
for _q in _seq['parts']:
    if _q['n'] not in _first:
        _first[_q['n']] = len(_un); _un.append(_q)
    _cum.append(len(_un))
ORDER = dict(_first)
for _p in parts:
    _p['o'] = ORDER.get(_p['n'], -1)                      # −1 = 순서 밖 (참고 부재 · 단면선) → 맨 끝에
SLIDES = AS.slides(_seq)
for _s in SLIDES:
    _s['i0'], _s['i1'] = _cum[_s['i0']], _cum[_s['i1']]
SEQN = len(_un)
SEQ_INFO = [dict(p=p['p'], name=p['name'], L=p['L'], s=p['s'], cap=p['cap']) for p in _un]

out = dict(rev='R28 · ' + C.REV_WI, date=__import__('datetime').date.today().isoformat(),   # 화면 머리 — 모델 판 (cad.REV 는 실시도면 R24 에 묶여 있다)
            L=L, W=W, apex=G.APEX, top=G.ROOFTOP, gl=GL,
           wall=G.D['겹깔도리-앞a']['z1'], layers=[lab for lab, _ in LAYER],
           steps=[dict(no=no, lab=lab) for no, lab, _ in STEP], slides=SLIDES, seqn=SEQN, seq=SEQ_INFO, parts=parts)
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model3d.json')
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('parts', len(parts), 'bytes', os.path.getsize(dst))


# R27b — 사이트 화면(index.html) 도 같이 만든다 (전에는 model3d.json 만 갱신돼 화면이 R24c 에 멈춰 있었다)
import io as _io, json as _json
import os as _os
_H = _os.path.dirname(_os.path.abspath(__file__))
_m = _json.load(_io.open(_os.path.join(_H, 'model3d.json'), encoding='utf-8'))
_tpl = _io.open(_os.path.join(_H, 'viewer_tpl.html'), encoding='utf-8').read()
_io.open(_os.path.join(_H, 'index.html'), 'w', encoding='utf-8').write(_tpl.replace('__MODEL__', _json.dumps(_m, ensure_ascii=False, separators=(',', ':'))))
print('index.html', len(_m['parts']))
