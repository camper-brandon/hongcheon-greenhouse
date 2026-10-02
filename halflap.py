# -*- coding: utf-8 -*-
"""R28 반턱 이음 · 폴리카 홈 묻힘 — 3D 보기 전용 형상 (사이트 · 영상 공용).
   모델(gen.py)은 맞댄 모양 · 재단 길이는 pn.LAP/PCW 가 정본이다.  여기서는 그 결과를 실제 모양으로 보인다.
     · 가로살(방충망은 세로살)이 선틀 폭만큼 안쪽 반 두께로 뻗어 들어가고, 선틀은 그 자리에서 바깥 반만 남는다.
     · 폴리카는 면 안 두 방향으로 PCIN 씩 커져 살 홈에 묻힌다.
   apply(D) → {부재이름: [상자(x0,x1,y0,y1,z0,z1), ...]}  (바뀐 부재만)"""
import re

AX = ('x', 'y', 'z')


def _box(r):
    return [r['x0'], r['x1'], r['y0'], r['y1'], r['z0'], r['z1']]


def _sub(b, c):
    """상자 b 에서 c 를 뺀 상자들"""
    if any(min(b[2 * i + 1], c[2 * i + 1]) - max(b[2 * i], c[2 * i]) <= 1e-6 for i in range(3)):
        return [b]
    out, cur = [], list(b)
    for i in range(3):
        lo, hi = 2 * i, 2 * i + 1
        if cur[lo] < c[lo]:
            nb = list(cur); nb[hi] = c[lo]; out.append(nb); cur[lo] = c[lo]
        if cur[hi] > c[hi]:
            nb = list(cur); nb[lo] = c[hi]; out.append(nb); cur[hi] = c[hi]
    return out


def _frame(n):
    m = re.match(r'^(창짝\d[앞뒤]|프로젝트창[LR]|배기창-좌|문짝[AB]|방충망틀-(?:좌[ab]|우))-(.+)$', n)
    return (m.group(1), m.group(2)) if m else (None, None)


def apply(D, L, W, PCIN):
    fr = {}
    for n in D:
        f, s = _frame(n)
        if f:
            fr.setdefault(f, {})[s] = n
    res = {}
    for f, mem in fr.items():
        scr = f.startswith('방충망틀')
        rails = [mem[k] for k in ('상', '하', '중간') if k in mem]
        stiles = [mem[k] for k in ('좌', '우', '선틀L', '선틀R') if k in mem]
        P, Cs = (stiles, rails) if scr else (rails, stiles)       # P = 뻗어 들어가는 살 · C = 끊기지 않는 살
        bx = {n: [_box(D[n])] for n in P + Cs}
        b0 = _box(D[Cs[0]])
        t = min(range(3), key=lambda i: b0[2 * i + 1] - b0[2 * i])        # 두께 축
        cen = (b0[2 * t] + b0[2 * t + 1]) / 2
        out_lo = cen < ((L if t == 0 else W) / 2)                          # 바깥이 작은 쪽
        for p in P:
            pb = _box(D[p])
            la = max((i for i in range(3) if i != t), key=lambda i: pb[2 * i + 1] - pb[2 * i])   # 살 길이 축
            oa = 3 - t - la
            for c in Cs:
                cb = _box(D[c])
                touch = abs(pb[2 * la] - cb[2 * la + 1]) < 1.0 or abs(pb[2 * la + 1] - cb[2 * la]) < 1.0
                inside = cb[2 * oa] - 0.5 <= pb[2 * oa] and pb[2 * oa + 1] <= cb[2 * oa + 1] + 0.5
                if not (touch and inside):
                    continue
                j = [0.0] * 6
                j[2 * la], j[2 * la + 1] = cb[2 * la], cb[2 * la + 1]
                j[2 * oa], j[2 * oa + 1] = pb[2 * oa], pb[2 * oa + 1]
                mid = (cb[2 * t] + cb[2 * t + 1]) / 2
                j[2 * t], j[2 * t + 1] = (mid, cb[2 * t + 1]) if out_lo else (cb[2 * t], mid)   # 안쪽 반
                bx[c] = [q for b in bx[c] for q in _sub(b, j)]
                bx[p].append(j)
        for n in P + Cs:
            res[n] = bx[n]
        if '폴리' in mem:
            b = _box(D[mem['폴리']])
            for i in range(3):
                if i != t:
                    b[2 * i] -= PCIN; b[2 * i + 1] += PCIN
            res[mem['폴리']] = [b]
    return res


def boxverts(b):
    x0, x1, y0, y1, z0, z1 = b
    return [[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]]
