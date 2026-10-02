# -*- coding: utf-8 -*-
"""조립 순서 — WI 공정 1~17 차례로 부재 하나하나 (영상과 3D 사이트가 같이 쓴다).
   build() → dict(L, W, gl, dur, steps, walls, cams, parts).  __main__ 이면 영상 프로젝트의 seq.json 으로 쓴다.
   벽 넷은 밖에 눕혀 짠 뒤 세운다 (영상에서만 회전 · 사이트는 제자리에 놓는다).  임시 가새·버팀대 없음."""
import sys, os, json, re
SP = r'D:\Doc\박수민\텃밭_화단\온실_도면_R12_단층쫄대\_생성스크립트'
if SP not in sys.path:
    sys.path.insert(0, SP)
_cwd = os.getcwd(); os.chdir(SP)
import geo as G
import pn
os.chdir(_cwd)

D, V = G.D, G.V
L = D['각관-우']['x1']; W = D['각관-뒤']['y1']; GL = G.GL


def fam(n):
    return n.split('-')[0]


def num(n):
    m = re.search(r'(\d+)', n.split('-', 1)[1] if '-' in n else '')
    return int(m.group(1)) if m else 0


def size_of(m):
    return {'갈색방부목 2x4': '2×4', '갈색방부목 2x6': '2×6', '갈색방부목 2x8': '2×8', '각관강재': '각관 50×50', '케미컬앵커 M12x160': '케미컬 앵커',
            '갈색방부목 창호재': '창호재', '폴리카': '폴리카 4.5T', '폴리카 10T복층': '폴리카 10T 복층', '방부 쫄대 15x38': '쫄대 15×38',
            '아연도 스트랩 30x1.2T': '스트랩 30×1.2T', '아이볼트 M8 스테인리스': '아이볼트 M8', '방충망 (알루미늄 망)': '방충망'}.get(m, m or '')


NAME = {'각관': '각관 프레임', '앵커': '케미칼 앙카볼트 M12 × 160 → 125 · 콘크리트 매입 70', '토대': '토대 2×4 눕힘', '밑깔도리': '밑깔도리', '위깔도리': '위깔도리',
        '측벽스터드': '측벽스터드', '킹스터드': '킹스터드', '잭스터드': '잭스터드', '창밑스터드': '창밑스터드', '창헤더': '창헤더 (눕힘)', '벽블로킹': '벽블로킹',
        '박공끝스터드': '박공 끝스터드', '박공스터드': '박공 스터드', '배기잭스터드': '배기창 잭스터드', '문헤더': '문헤더 밑판 (눕힘)', '문헤더세움': '문헤더 세움',
        '문헤더덮개': '문헤더 덮개', '박공가로재': '박공 가로재', '개구턱': '개구턱', '환풍채움': '환풍 채움', '박공상부': '박공 상부재', '배기헤더': '배기창 헤더',
        '마룻대받침': '마룻대 받침', '겹깔도리': '겹깔도리 (모서리 직교 겹침)', '가새': '가새 스트랩 (스터드 안쪽 면)', '무릎바': '무릎벽 가로바', '무릎받이': '폴리카 밑 받이 38×38', '가새받침': 'V 꼭짓점 받침', '세로쫄대': '문 쪽 세로 쫄대', '끼움가새': '끼움 가새 2×4', '이음받침': '합판 이음 받침', '문옆가로바': '문 옆 가운데 가로바', '외장합판': '외장 내수합판 12T', '하우스랩': '요철 하우스랩', '가로쫄대': '가로 쫄대 15×38', '세로사이딩': '세로 시멘트 사이딩', '모서리마감': '모서리 마감 19×89/70', '문옆마감': '문 옆 마감 19×89', 'Z물끊기': 'Z 물끊기 0.5T', 'Z물끊기코너': 'Z 물끊기 접은 코너', '무릎벽방충망': '무릎벽 아래 방충망', '마룻대': '마룻대', '서까래': '서까래 2×6 (버드마우스는 겹깔도리에)',
        '처마막이': '처마막이 2×4 세움 (직각 472)', '지붕블로킹': '지붕블로킹 2×6 (지붕면 직각)', '칼라타이': '칼라타이 (블로킹에 얹어 서까래 옆면에)', '벽판': '벽판', '박공판': '박공판',
        '벽쫄대': '벽쫄대', '박공쫄대': '박공쫄대', '박공모서리쫄대': '박공 모서리쫄대', '창옆쫄대': '창옆쫄대', '지붕판': '지붕판 10T (처마→마룻대 한 장)',
        '지붕쫄대': '지붕쫄대 (홀수 서까래)', '아이볼트': '아이볼트 M8', '창짝1앞': '앞 창짝 1', '창짝2앞': '앞 창짝 2', '창짝1뒤': '뒤 창짝 1', '창짝2뒤': '뒤 창짝 2',
        '프로젝트창L': '북쪽 프로젝트창 L (90°)', '프로젝트창R': '북쪽 프로젝트창 R (90°)', '배기창': '배기창', '방충망틀': '방충망 틀', '방충망': '방충망', '창멈춤': '창 멈춤대 20×45', '창턱': '창턱 경사재', '물끊기': '머리 물끊기 절곡 0.5T', '마룻대덧댐': '마룻대 덧댐판 2×4',
        '문짝A': '문짝 A', '문짝B': '문짝 B', '문스토퍼': '문스토퍼 2×4'}
SIZED = ('밑깔도리', '위깔도리', '측벽스터드', '킹스터드', '잭스터드', '창밑스터드', '벽블로킹', '박공끝스터드', '박공스터드', '배기잭스터드', '박공가로재', '박공상부', '마룻대받침', '마룻대')


def build():
    seq, steps, walls, cams = [], [], {}, []
    st = {'t': 1.2}

    def piece(n, grp, cap, dur):
        r = D[n]; p = pn.OF.get(n) or None
        Lm = pn.TYP[p]['L'] if p and p in pn.TYP else None
        seq.append(dict(n=n, p=p, L=Lm, m=r['m'], s=size_of(r['m']), k=len(V[n]) // 2, t=round(st['t'], 3), d=dur, g=grp, cap=cap,
                        name=NAME.get(fam(n), fam(n)) + ((' ' + size_of(r['m'])) if fam(n) in SIZED else ''),
                        v=[[round(a, 1), round(b, 1), round(c, 1)] for a, b, c in V[n]]))

    def step(cap, cam, site_cam=None):
        """공정 시작: 자막 · 카메라 (three 좌표 pos/tgt · x=길이, y=높이, z=앞이 +).  site_cam = 사이트 슬라이드용 (없으면 cam)"""
        st['t'] += 0.7
        steps.append(dict(t=round(st['t'], 3), cap=cap, site=site_cam or cam))
        cams.append(dict(t=round(st['t'], 3), pos=cam[0], tgt=cam[1]))

    def run(names, grp, cap, dt):
        for n in names:
            if n not in V or len(V[n]) < 6:
                continue
            piece(n, grp, cap, max(0.3, dt * 1.1)); st['t'] += dt

    def by(prefix, side=None, key=None):
        ns = [n for n in D if n.startswith(prefix + '-') and (side is None or n.split('-', 1)[1].startswith(side))]
        return sorted(ns, key=key or (lambda n: (num(n), n)))

    def raise_wall(g, pivot, lay, cap, cam):
        st['t'] += 0.5
        cams.append(dict(t=round(st['t'] - 0.3, 3), pos=cam[0], tgt=cam[1]))
        steps.append(dict(t=round(st['t'], 3), cap=cap, site=None))          # 사이트에는 슬라이드 없음 (제자리에 놓인다)
        walls[g] = dict(t0=round(st['t'], 3), dur=2.4, pivot=pivot, lay=lay, cap=cap)
        st['t'] += 2.4 + 0.6

    # ── 1 각관 · 2 앵커 · 3 토대
    step('공정 1 · 각관 프레임 — 모서리 결속', ([-6200, 5000, 7400], [-300, 100, 200]))
    run(['각관-앞', '각관-뒤', '각관-좌', '각관-우'], 'base', '공정 1 · 각관 프레임', 0.55)
    for q in seq[-4:]:
        q['L'] = round(max(D[q['n']]['x1'] - D[q['n']]['x0'], D[q['n']]['y1'] - D[q['n']]['y0'])); q['p'] = 'ST'
    step('공정 2 · 케미칼 앵커 M12 — 너트는 각관 안에서', ([-3900, 1500, 3400], [-2300, -60, 1500]))
    run(by('앵커', '앞') + by('앵커', '우') + by('앵커', '뒤') + by('앵커', '좌'), 'base', '공정 2 · 앵커', 0.12)
    for q in seq:
        if q['n'].startswith('앵커'): q['p'] = 'AN'; q['L'] = 160
    step('공정 3 · 방습재 · 토대 — 각관에 나사', ([-5600, 4600, 7200], [0, 0, 200]))
    run(['토대-앞a', '토대-앞b', '토대-뒤a', '토대-뒤b', '토대-좌', '토대-우'], 'base', '공정 3 · 토대', 0.42)

    # ── 4·5 측벽 (앞 → 뒤): 밖에 눕혀 짜기 → 세우기
    def side_wall(side, g, pivot, lay, cam_frame, cam_raise, no):
        step('공정 %s · %s 측벽 판 — 밖에 눕혀서 짠다' % (no, side), cam_frame, cam_raise)
        order = by('밑깔도리', side) + by('측벽스터드', side, key=lambda n: D[n]['x0']) + by('킹스터드', side, key=lambda n: D[n]['x0']) \
            + by('잭스터드', side, key=lambda n: D[n]['x0']) + by('창밑스터드', side, key=lambda n: D[n]['x0']) + by('창헤더', side, key=lambda n: D[n]['x0']) \
            + by('벽블로킹', side, key=lambda n: D[n]['x0']) + by('무릎바', side, key=lambda n: D[n]['x0']) + by('무릎받이', side, key=lambda n: D[n]['x0']) + by('이음받침', side) \
            + by('끼움가새', side) + by('위깔도리', side)
        run(order, g, '공정 %s · %s 측벽 판' % (no, side), 0.34)
        raise_wall(g, pivot, lay, '공정 %s · %s 측벽 세우기 — 밑깔도리를 토대에 못' % (no, side), cam_raise)

    side_wall('앞', 'wallF', [0, 0, 0], 'F', ([-3400, 5000, 7800], [-200, 0, 2400]), ([-6400, 2200, 6400], [0, 500, 1200]), '4')
    side_wall('뒤', 'wallB', [0, W, 0], 'B', ([3400, 5000, -7800], [200, 0, -2400]), ([6400, 2200, -6400], [0, 500, -1200]), '5')

    # ── 6 박공 (좌 → 우): 밖에 눕혀 짜기 → 세우기
    GABLE = ('밑깔도리', '박공끝스터드', '박공스터드', '킹스터드', '잭스터드', '배기잭스터드', '문헤더세움', '문헤더', '문헤더덮개', '창헤더', '배기헤더',
             '박공가로재', '무릎바', '무릎받이', '문옆가로바', '이음받침', '가새받침', '끼움가새', '개구턱', '환풍채움', '위깔도리', '박공상부', '마룻대받침')

    def gable(side, g, pivot, lay, cam_frame, cam_raise, no):
        lo, hi = (0, L / 2) if side == '좌' else (L / 2, L)
        names = []
        for f in GABLE:
            ns = [n for n in D if fam(n) == f and lo <= (D[n]['x0'] + D[n]['x1']) / 2 < hi and n in V]
            if f in ('밑깔도리', '위깔도리', '창헤더', '킹스터드', '잭스터드', '무릎바', '무릎받이', '이음받침', '끼움가새', '문옆가로바', '가새받침'):
                ns = [n for n in ns if n.split('-', 1)[1].startswith(side)]
            names += sorted(ns, key=lambda n: (D[n]['z0'], D[n]['y0']))
        step('공정 %s · %s 박공벽 판 — 밖에 눕혀서 짠다' % (no, side), cam_frame, cam_raise)
        run(names, g, '공정 %s · %s 박공벽 판' % (no, side), 0.34)
        raise_wall(g, pivot, lay, '공정 %s · %s 박공벽 세우기 — 끝스터드를 모서리 스터드에' % (no, side), cam_raise)

    gable('좌', 'wallL', [0, 0, 0], 'L', ([-8400, 5200, 4600], [-4300, 0, 0]), ([-7800, 2600, 5400], [-2400, 900, 0]), '6')
    gable('우', 'wallR', [L, 0, 0], 'R', ([8400, 5200, 4600], [4300, 0, 0]), ([7800, 2600, 5400], [2400, 900, 0]), '6')

    # ── 7 겹깔도리 · 8 가새 스트랩 · 9 마룻대 · 10 서까래
    step('공정 7 · 겹깔도리 — 모서리 직교 겹침', ([-6200, 5200, 6400], [0, 1500, 0]))
    run(['겹깔도리-좌a', '겹깔도리-좌b', '겹깔도리-우', '겹깔도리-앞a', '겹깔도리-앞b', '겹깔도리-뒤a', '겹깔도리-뒤b'], 'base', '공정 7 · 겹깔도리', 0.5)
    step('공정 8 · 무릎벽 외장 — 합판 · 요철 하우스랩 · 가로 쫄대 → 세로 사이딩 · 마감 · Z 물끊기', ([6200, 2400, 6400], [0, 300, 0]))
    run(by('외장합판') + by('하우스랩') + by('가로쫄대') + by('세로쫄대') + by('무릎벽방충망') + by('모서리마감') + by('문옆마감') + by('세로사이딩') + by('Z물끊기') + by('Z물끊기코너'), 'base', '공정 8 · 무릎벽 외장', 0.08)
    step('공정 9 · 마룻대 두 토막 — 양쪽 받침 위에 · 서까래 R5 · R6 사이 이음에 덧댐판 2×4', ([-6200, 5600, 5200], [0, 2600, 0]))
    run(['마룻대-좌', '마룻대-우', '마룻대덧댐-앞', '마룻대덧댐-뒤'], 'base', '공정 9 · 마룻대', 0.7)
    step('공정 10 · 서까래 — 양 끝 쌍부터', ([6400, 4800, 6400], [0, 1900, 0]))
    idx = sorted({num(n) for n in D if fam(n) == '서까래'})
    order, lo, hi = [], 0, len(idx) - 1
    while lo <= hi:
        order += [idx[lo]] + ([idx[hi]] if hi != lo else []); lo += 1; hi -= 1
    names = []
    for i in order:
        names += ['서까래-앞%d' % i, '서까래-뒤%d' % i]
    run([n for n in names if n in D], 'base', '공정 10 · 서까래', 0.36)
    # ── 11 처마막이 · 지붕블로킹 · 칼라타이 (R24b: 처마막이 2×4 세움 직각)
    step('공정 11 · 처마막이 2×4 세움 — 깔도리 위 서까래 사이 · 직각 472', ([-4200, 4200, 5200], [0, 2300, 300]))
    run(by('처마막이', '앞', key=lambda n: D[n]['x0']) + by('처마막이', '뒤', key=lambda n: D[n]['x0']), 'base', '공정 11 · 처마막이', 0.2)
    step('공정 11 · 지붕블로킹 — 지붕면에 직각 · 서까래 사이', ([-4200, 5000, 4600], [0, 2700, 200]))
    run(by('지붕블로킹', '앞', key=lambda n: D[n]['x0']) + by('지붕블로킹', '뒤', key=lambda n: D[n]['x0']), 'base', '공정 11 · 지붕블로킹', 0.2)
    step('공정 11 · 칼라타이 — 블로킹에 얹고 서까래 옆면에 나사', ([4600, 4800, 4600], [0, 2700, 0]))
    run(by('칼라타이', key=lambda n: D[n]['x0']), 'base', '공정 11 · 칼라타이', 0.36)
    # ── 12 판 · 13 쫄대 · 14 지붕판 · 15 지붕쫄대·아이볼트
    step('공정 12 · 벽판 폴리카 4.5T — 임시 고정', ([-6600, 3600, 6800], [0, 1400, 0]))
    run(by('벽판', '앞', key=lambda n: D[n]['x0']) + by('벽판', '뒤', key=lambda n: D[n]['x0']), 'base', '공정 12 · 벽판', 0.22)
    step('공정 12 · 박공판 폴리카', ([-7600, 3400, 4200], [-1800, 1700, 0]))
    run(sorted([n for n in D if fam(n) == '박공판'], key=lambda n: (n.split('-')[1][0], D[n]['z0'], D[n]['y0'])), 'base', '공정 12 · 박공판', 0.16)
    step('공정 13 · 쫄대 — 판을 누른다', ([6600, 3600, 6800], [0, 1400, 0]))
    run(by('벽쫄대', '앞', key=lambda n: D[n]['x0']) + by('벽쫄대', '뒤', key=lambda n: D[n]['x0']) + by('박공쫄대') + by('박공모서리쫄대') + by('창옆쫄대'), 'base', '공정 13 · 쫄대', 0.16)
    step('공정 14 · 지붕판 10T — 처마에서 마룻대까지 한 장', ([-5200, 6800, 5600], [0, 2400, 0]))
    run(by('지붕판', '앞', key=lambda n: D[n]['x0']) + by('지붕판', '뒤', key=lambda n: D[n]['x0']), 'base', '공정 14 · 지붕판', 0.36)
    step('공정 15 · 지붕쫄대 (짝수 서까래) · 아이볼트', ([5200, 6800, 5600], [0, 2400, 0]))
    run(by('지붕쫄대', '앞', key=lambda n: D[n]['x0']) + by('지붕쫄대', '뒤', key=lambda n: D[n]['x0']) + by('아이볼트'), 'base', '공정 15 · 지붕쫄대 · 아이볼트', 0.18)
    # ── 16 창 · 17 문
    step('공정 16 · 창 · 배기창 · 방충망', ([-1500, 2400, 7800], [0, 1100, 0]))
    run(by('창짝1앞') + by('창짝2앞') + by('창짝1뒤') + by('창짝2뒤') + by('프로젝트창L') + by('프로젝트창R') + by('배기창') + by('방충망틀') + by('방충망') + by('창멈춤') + by('창턱') + by('물끊기'), 'base', '공정 16 · 창', 0.14)
    step('공정 17 · 문짝 → 문스토퍼', ([8400, 2400, 3200], [2569, 1200, 0]))
    run(by('문짝A') + by('문짝B') + by('문스토퍼'), 'base', '공정 17 · 문', 0.16)
    # ── 끝
    st['t'] += 0.8
    cams.append(dict(t=round(st['t'], 3), pos=[-7600, 4200, 7800], tgt=[0, 1500, 0]))
    steps.append(dict(t=round(st['t'], 3), cap='완성 — 목조 온실 3.2 × 5.1 m', site=([-7600, 4200, 7800], [0, 1500, 0])))
    st['t'] += 3.5
    return dict(L=L, W=W, gl=GL, dur=round(st['t'], 2), steps=steps, walls=walls, cams=cams, parts=seq)


def slides(out):
    """사이트용: 공정 슬라이드 (자막 · 부재 범위 · 카메라).  세우기 단계는 앞 공정에 합친다"""
    parts, steps = out['parts'], out['steps']
    res = []
    for i, s in enumerate(steps):
        if s['site'] is None:
            continue
        t1 = steps[i + 1]['t'] if i + 1 < len(steps) else 1e9
        idx = [k for k, p in enumerate(parts) if s['t'] <= p['t'] < t1]
        res.append(dict(cap=s['cap'].replace(' — 밖에 눕혀서 짠다', ' — 밖에 눕혀 짜서 세운다'),
                        i0=(idx[0] if idx else (res[-1]['i1'] if res else 0)), i1=(idx[-1] + 1 if idx else (res[-1]['i1'] if res else 0)),
                        pos=s['site'][0], tgt=s['site'][1]))
    return res


if __name__ == '__main__':
    out = build()
    dst = r'D:\Doc\hf-greenhouse\full\seq.json'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for s in out['steps']:
        s.pop('site', None)
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    sys.stdout.reconfigure(encoding='utf-8')
    print('parts', len(out['parts']), 'dur', out['dur'], 'steps', len(out['steps']))
