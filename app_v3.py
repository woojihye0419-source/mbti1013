import io
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title='나에게 맞는 금융 직무 찾기', page_icon='💼', layout='centered')

ROLES = {
    '기업금융': {'desc':'기업의 자금 수요와 사업을 이해하고 금융 솔루션을 제안하는 업무', 'skills':'기업분석, 재무제표 이해, 고객 소통', 'cert':'신용분석사, 투자자산운용사'},
    '여신심사': {'desc':'기업의 상환능력과 제출 자료를 검토하고 여신 판단을 지원하는 업무', 'skills':'재무분석, 근거 검증, 꼼꼼함', 'cert':'신용분석사, 재경관리사'},
    '리스크관리': {'desc':'금융회사의 다양한 위험을 측정하고 모니터링하는 업무', 'skills':'통계, 위험지표, 분석적 사고', 'cert':'FRM, 신용분석사, ADsP'},
    '디지털금융': {'desc':'고객 문제를 디지털 서비스와 데이터로 개선하는 업무', 'skills':'데이터 활용, 서비스 기획, 협업', 'cert':'ADsP, SQLD'},
    '개인금융': {'desc':'개인 고객의 금융 목표를 파악하고 적합한 상품과 서비스를 안내하는 업무', 'skills':'고객 상담, 금융상품 이해, 공감', 'cert':'AFPK, 투자자산운용사'},
}

QUESTIONS = [
    ('새로운 업무를 맡으면 먼저 하고 싶은 일은?', ('고객이 무엇을 필요로 하는지 듣기', ['기업금융','개인금융']), ('관련 자료를 살펴 핵심 수치 찾기', ['여신심사','리스크관리'])),
    ('더 흥미로운 과제는?', ('기업의 사업 구조와 자금 흐름 분석', ['기업금융','여신심사']), ('앱 사용 과정을 더 편리하게 개선', ['디지털금융','개인금융'])),
    ('오류를 발견했을 때 나는?', ('원인과 근거를 끝까지 확인한다', ['여신심사','리스크관리']), ('사용자에게 미칠 영향부터 살핀다', ['디지털금융','개인금융'])),
    ('어떤 성과가 더 뿌듯할까?', ('기업이 필요한 자금을 적시에 확보', ['기업금융','여신심사']), ('고객의 금융 불편을 해결', ['개인금융','디지털금융'])),
    ('선호하는 작업 방식은?', ('사람과 대화하며 해결책 도출', ['기업금융','개인금융']), ('데이터를 분석해 패턴 발견', ['리스크관리','디지털금융'])),
    ('보고서에서 먼저 확인할 것은?', ('숫자의 변화와 이상 징후', ['리스크관리','여신심사']), ('고객에게 필요한 다음 행동', ['개인금융','기업금융'])),
    ('배우고 싶은 기술은?', ('SQL·Python을 활용한 분석 자동화', ['디지털금융','리스크관리']), ('재무제표와 기업 신용분석', ['여신심사','기업금융'])),
    ('회의에서 맡고 싶은 역할은?', ('다양한 이해관계자의 요구 조율', ['기업금융','개인금융']), ('판단 기준과 위험 요소 점검', ['여신심사','리스크관리'])),
    ('더 재미있어 보이는 데이터는?', ('고객의 앱 이용 행동 데이터', ['디지털금융','개인금융']), ('기업의 재무비율과 현금흐름', ['여신심사','기업금융'])),
    ('업무에서 더 중요하게 생각하는 것은?', ('위험을 미리 감지하는 체계', ['리스크관리','여신심사']), ('고객에게 이해하기 쉽게 설명', ['개인금융','기업금융'])),
    ('개선 아이디어가 떠오르면?', ('간단한 프로토타입으로 실험', ['디지털금융','리스크관리']), ('현장 의견을 듣고 적용 가능성 확인', ['기업금융','개인금융'])),
    ('가장 해보고 싶은 업무는?', ('기업 자료의 타당성을 교차 검증', ['여신심사','리스크관리']), ('금융 서비스의 고객 경험 설계', ['디지털금융','개인금융'])),
]



def supporting_answers(role):
    matches = []
    for i in sorted(st.session_state.answers):
        chosen = st.session_state.answers[i]
        question, *options = QUESTIONS[i]
        answer, linked_roles = options[chosen]
        if role in linked_roles:
            matches.append((question, answer))
    return matches


def recommendation_reason(role):
    evidence = supporting_answers(role)
    if not evidence:
        return '이번 응답에서 직접 연결된 선택지는 없었어요. 다른 직무의 근거도 살펴보세요.'
    samples = ' / '.join(f'「{answer}」' for _, answer in evidence[:2])
    return f'{samples} 등의 선택이 {role} 직무에 연결되었어요. {ROLES[role]["desc"]}에 관심이 있을 가능성을 보여줍니다.'


def find_korean_font(size):
    paths = [
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf',
        'C:/Windows/Fonts/malgun.ttf',
        '/System/Library/Fonts/AppleSDGothicNeo.ttc',
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def make_result_card(ranking):
    image = Image.new('RGB', (1080, 1350), '#f5f4ff')
    draw = ImageDraw.Draw(image)
    title_font = find_korean_font(61)
    large_font = find_korean_font(49)
    medium_font = find_korean_font(34)
    small_font = find_korean_font(27)
    draw.rounded_rectangle((65, 65, 1015, 1285), radius=45, fill='white')
    draw.text((120, 132), '나에게 맞는 금융 직무', font=title_font, fill='#222047')
    draw.text((120, 220), '12개 응답으로 살펴본 관심 직무 TOP 3', font=small_font, fill='#69667e')
    draw.rounded_rectangle((115, 295, 965, 510), radius=30, fill='#ede9fe')
    draw.text((155, 330), 'MY TOP ROLE', font=small_font, fill='#6652b7')
    draw.text((155, 392), ranking[0][0], font=large_font, fill='#33267d')
    draw.text((790, 400), f'{ranking[0][1]}점', font=medium_font, fill='#33267d')
    draw.text((120, 560), '관심 직무 순위', font=medium_font, fill='#222047')
    for rank, (role, score) in enumerate(ranking[:3], 1):
        y = 635 + (rank - 1) * 120
        draw.text((125, y), f'{rank}. {role}', font=medium_font, fill='#302d45')
        draw.text((825, y), f'{score}점', font=medium_font, fill='#6b55ba')
        draw.rounded_rectangle((125, y+60, 940, y+76), radius=8, fill='#e8e5f1')
        if score:
            draw.rounded_rectangle((125, y+60, 125 + int(815 * score / 12), y+76), radius=8, fill='#8b70dc')
    draw.text((120, 1040), '내가 선택한 대표 응답', font=medium_font, fill='#222047')
    evidence = supporting_answers(ranking[0][0])
    answer = evidence[0][1] if evidence else '선택한 응답 없음'
    # Split by character count to fit within the card width.
    for idx, line in enumerate(textwrap.wrap(answer, width=24)[:2]):
        draw.text((130, 1105 + idx * 42), line, font=small_font, fill='#554b78')
    draw.text((120, 1225), '비공식 관심사 탐색 · 적성 및 채용 가능성 진단 아님', font=small_font, fill='#79768a')
    output = io.BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()

st.markdown("""<style>
.block-container{max-width:1080px;padding-top:2rem;padding-bottom:4rem}
.stApp{background:linear-gradient(125deg,#f4f7ff 0%,#fffafd 70%,#fff9ef 100%)}
h1,h2,h3{color:#17284e;letter-spacing:-.7px}
div.stButton>button{border-radius:16px;min-height:56px;white-space:normal}
.hero{padding:24px 28px;background:white;border-radius:24px;box-shadow:0 10px 36px #263b6810;margin-bottom:20px}
.role-card{border-radius:23px;padding:19px 18px 22px;min-height:275px;box-shadow:0 7px 22px #293a5910}
.role-card .art{font-size:66px;text-align:center;padding:13px 0 9px;background:#ffffff90;border-radius:18px;margin-bottom:13px}
.role-card .rank{font-size:13px;font-weight:700;color:#4c5d76}
.role-card .name{font-size:24px;font-weight:800;color:#1d3157;margin:6px 0}
.role-card .score{font-size:20px;font-weight:800;color:#23375e}
.role-card .desc{font-size:14px;color:#4b5870;line-height:1.65;margin-top:11px}
.reason{background:#fff;border:1px solid #e5eafa;border-radius:16px;padding:14px 17px;margin:9px 0;color:#34435e}
.small-note{color:#66748c;font-size:13px}
</style>""", unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = 0
if 'answers' not in st.session_state: st.session_state.answers = {}

st.title('🧭 나에게 맞는 금융 직무 찾기')
st.caption('12문항 · 약 3분 · 관심사 기반 직무 탐색 (공식 적성검사 아님)')

if st.session_state.step < len(QUESTIONS):
    i = st.session_state.step
    question, *options = QUESTIONS[i]
    st.progress(i / len(QUESTIONS), text=f'질문 {i+1} / {len(QUESTIONS)}')
    st.subheader(question)
    for idx, (label, _) in enumerate(options):
        if st.button(('✓ ' if st.session_state.answers.get(i) == idx else '') + label, key=f'opt_{i}_{idx}', use_container_width=True, type='primary' if st.session_state.answers.get(i)==idx else 'secondary'):
            st.session_state.answers[i] = idx
            st.session_state.step = i + 1
            st.rerun()
    if i > 0 and st.button('← 이전 질문'):
        st.session_state.step -= 1
        st.rerun()
else:
    from html import escape
    scores = {role: 0 for role in ROLES}
    for i, selected in st.session_state.answers.items():
        for role in QUESTIONS[i][selected+1][1]:
            scores[role] += 1
    ranking = sorted(scores.items(), key=lambda x: (-x[1], list(ROLES).index(x[0])))
    st.markdown('<div class="hero"><div style="font-size:14px;color:#63718e">🎉 테스트 완료!</div><h2 style="margin:7px 0">당신에게 잘 맞는 금융 직무를 찾았어요.</h2><div style="color:#61708a">선택한 답변을 바탕으로 관심 직무와 추천 이유를 확인해 보세요.</div></div>',unsafe_allow_html=True)
    st.subheader('🏆 추천 직무 TOP 3')
    palette = ['#fff0cf','#e4f1ff','#ffe9e9']
    icons = {'기업금융':'🤝','여신심사':'📋','리스크관리':'🛡️','디지털금융':'💻','개인금융':'💬'}
    cols = st.columns(3, gap='medium')
    for j, ((role,score),col) in enumerate(zip(ranking[:3],cols)):
        with col:
            st.markdown(f'<div class="role-card" style="background:{palette[j]}"><div class="rank">TOP {j+1}</div><div class="art">{icons[role]}</div><div class="name">{escape(role)}</div><div class="score">{score}점 <span style="font-size:12px;font-weight:400">/ 응답 연결 횟수</span></div><div class="desc">{escape(ROLES[role]["desc"])}</div></div>',unsafe_allow_html=True)
    st.caption('점수는 해당 직무와 연결된 답변 수입니다. 적합도 확률이나 채용 가능성을 뜻하지 않습니다. 동점 시 고정 순서로 표시합니다.')
    st.subheader('🎯 이렇게 추천했어요')
    for rank,(role,score) in enumerate(ranking[:3],1):
        evidence=supporting_answers(role)
        with st.container(border=True):
            st.markdown(f'**{icons[role]} {rank}위 · {role}**')
            st.write(recommendation_reason(role))
            for q,a in evidence[:3]:
                st.markdown(f'<div class="reason"><span class="small-note">{escape(q)}</span><div><b>↳ {escape(a)}</b></div></div>',unsafe_allow_html=True)
            if len(evidence)>3:
                with st.expander(f'나머지 연결 응답 {len(evidence)-3}개'):
                    for q,a in evidence[3:]: st.markdown(f'- **{q}** → {a}')
    st.subheader('💼 직무 자세히 보기')
    tabs=st.tabs([f'{icons[r]} {r}' for r,_ in ranking[:3]])
    for tab,(role,score) in zip(tabs,ranking[:3]):
        with tab:
            st.markdown(f'### {role}')
            st.write(ROLES[role]['desc'])
            st.markdown(f'**필요 역량**  \n{ROLES[role]["skills"]}')
            st.markdown(f'**관련 학습·자격증 예시**  \n{ROLES[role]["cert"]}')
    st.subheader('📸 결과 카드 저장하기')
    st.write('TOP 3와 대표 응답을 이미지로 저장해 메신저나 SNS에 공유할 수 있어요.')
    card_png=make_result_card(ranking)
    st.image(card_png,caption='공유용 결과 카드 미리보기',width=390)
    st.download_button('⬇️ 결과 카드 PNG 저장',data=card_png,file_name='finance_career_result.png',mime='image/png',use_container_width=True)
    st.info('비공식 자기 탐색 활동이며, 실제 직무 수행 능력이나 적성을 진단하지 않습니다.')
    if st.button('🔄 처음부터 다시 하기',use_container_width=True):
        st.session_state.step=0
        st.session_state.answers={}
        st.rerun()
