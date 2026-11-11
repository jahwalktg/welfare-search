# -*- coding: utf-8 -*-
"""본문 추출 txt(쪽 경계 \f) → data/*.json  (사회복지 지침 찾기)
사용: python -X utf8 tools/make_books.py          (아래 BOOKS 전부)
      python -X utf8 tools/make_books.py siseol   (하나만)
책을 더하려면: ① 원문 PDF를 pdf/ 에 ② tools/pdf2txt.cjs 로 source/ 에 txt ③ 아래 BOOKS 에 한 줄 ④ index.html 의 BOOKS 에 한 줄.
  off   = pdf쪽 − 인쇄쪽 (인쇄 1쪽이 pdf 13쪽이면 12)
  noise = 쪽마다 되풀이되는 머리말 줄(그 줄과 똑같으면 지움)
  nre   = 지울 줄의 정규식(줄 전체가 맞으면 지움)
  pageno= True 면 쪽 번호만 있는 첫 줄을 지움
자활 지침 찾기(jahwal-search)의 tools/make_data.py 를 책 목록 방식으로 바꾼 것.
"""
import sys, json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
HEAD = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII',
        'II. 사회복지시설 공통적용사항', 'III. 사회복지시설 업무의 전자화 시책', 'IV. 사회복지시설의 안전관리',
        'VI. 부 록', 'MINISTRY OF HEALTH AND WELFARE', 'Ministry of Health and Welfare']
BOOKS = {
  'siseol': dict(txt='2026-사회복지시설관리안내-본문추출.txt', title='2026년 사회복지시설 관리안내', pub='보건복지부, 2026', off=12,
      noise=HEAD + ['2026년 사회복지시설 관리안내', '설', '사', 'V. 사회복지법인 및 사회복지시설 재무·회계규칙', '재무·회계규칙',
             '회복지법인 및사회복지시', '사회복지시설공통적용사항', '전자화 시책', '사회복지시설업무의', '부록VI', '사회복지시설종사자',
             '인건비 가이드라인', 'VII. 사회복지시설 종사자 인건비 가이드라인', '사회복지시설의', '안전관리'],
      nre=[r'[∣|]\s*[ivxlcdm\d]+\s*[∣|]']),
  'siseol-2025': dict(txt='2025-사회복지시설관리안내-본문추출.txt', title='2025년 사회복지시설 관리안내', pub='보건복지부, 2025', off=12,
      noise=HEAD + ['2025 사회복지시설관리안내', 'V. 사회복지법인 및 사회복지시설 재무･회계규칙'],
      nre=[r'[∣|]\s*[ivxlcdm\d]+\s*[∣|]']),
  'bokjigwan': dict(txt='2026-사회복지관업무처리안내-본문추출.txt', title='2026년 사회복지관 운영관련 업무처리 안내', pub='보건복지부, 2026', off=4,
      noise=['2026 사회복지관 운영관련 업무처리 안내', 'CHAPTER', '사', '회', '복', '지', '관', '업', '설', '치', '운', '영', '의', '･'],
      nre=[r'\d{1,3} 보건복지부', r'보건복지부 \d{1,3}', r'www\.mohw\.go\.kr \d{1,3}', r'\d{1,3} www\.mohw\.go\.kr']),
  'seoul': dict(txt='2026-서울시처우개선계획-본문추출.txt', title='2026년 서울시 사회복지시설 종사자 처우개선 계획', pub='서울특별시, 2026 (공개용)', off=0,
      noise=[], nre=[r'\d{1,3}- \d{1,3} -'], pageno=True),
}
def roman(n):
    out = ''
    for v, s in [(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n >= v: out += s; n -= v
    return out
def make(key):
    c = BOOKS[key]
    noise = set(c.get('noise', [])); nre = [re.compile(x) for x in c.get('nre', [])]
    raw = open(os.path.join(ROOT, 'source', c['txt']), encoding='utf-8').read().replace('\xa0', ' ').split('\f')
    pages = []
    for i, p in enumerate(raw):
        n = i + 1; lines = []; first = True
        for l in p.split('\n'):
            s = re.sub(r'[ \t　]{2,}', ' ', l.strip())
            if not s: continue
            if c.get('pageno') and first and s == str(n): first = False; continue
            first = False
            if s in noise: continue
            if any(r.fullmatch(s) for r in nre): continue
            lines.append(s)
        t = '\n'.join(lines).strip()
        if not t: continue
        pr = n - c['off']
        lab = str(pr) if pr >= 1 else (roman(n - 1) if n - 1 >= 1 else '앞')
        if pr < 1 and n <= 2: lab = '앞'
        pages.append({'n': n, 'p': lab, 't': t})
    out = {'key': key, 'title': c['title'], 'pub': c['pub'], 'off': c['off'], 'pages': pages}
    dst = os.path.join(ROOT, 'data', key + '.json')
    with open(dst, 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, separators=(',', ':'))
    print(key, len(pages), '쪽', os.path.getsize(dst), 'bytes', '| 인쇄쪽', pages[0]['p'], '…', pages[-1]['p'])
for k in (sys.argv[1:] or list(BOOKS)):
    make(k)
