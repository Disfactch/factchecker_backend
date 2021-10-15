# sdk에서 url 배포를 위해 실행시킬 경우 위 모듈을 사용
try:
    from factcode.CrawlMorpheme import crawlmorpheme
    from factcode.CrawlMorpheme import crawlbs
    from factcode import optimization

    from factcode.CrawlMorpheme import crawlmorpheme
    from factcode.PositivityCheck import positivity_test
    from factcode.StringProcess import propernoun
    from factcode import optimization
    from factcode import settingbox

    from factcode.CrawlMorpheme import crawlmorpheme
    from factcode.StringProcess import summaries
    from factcode import provocative_title
    from factcode import optimization

# 로컬 컴퓨터로 실행시킬 경우 아래 모듈을 사용
except:
    from CrawlMorpheme import crawlmorpheme
    from CrawlMorpheme import crawlbs
    import optimization

    from CrawlMorpheme import crawlmorpheme
    from PositivityCheck import positivity_test
    from StringProcess import propernoun
    import optimization
    import settingbox

    from CrawlMorpheme import crawlmorpheme
    from StringProcess import summaries
    import optimization

cm = crawlmorpheme
cb = crawlbs
op = optimization
pc = positivity_test
pn = propernoun
pt = provocative_title
sr = summaries

# ------------------------------------------------------------------------------ #


# provocative_title.py
# Written by Byeongho Hwang (황병호)

# model_factcheck.py가 전반적인 기능을 크게 구현해놓은 연결이라고 한다면,
# provocative_title.py는 그 메이저 모듈 중 하나인 자극적인 제목 감지 기능의
# 각 기능의 세부 기능과 흐름을 구현해놓은 것이다.

# SPDX-FileCopyrightText: © 2021 Byeongho Hwang <crovas@kaist.ac.kr>
# SPDX-License-Identifier: BSD-3-Clause

# (1) Provocative Title Checker
# Functions Required::
# morpheme_separation()
# causal_comparison()
# WordtoVec_exclusiveA()
# evaluation_moduleA()

# 형태소 감지기
def morpheme_separation(text):
    morpheme_array = cm.get_morpheme(text)
    return morpheme_array

# 조사 비교를 통한 자극적 도치 가능성 판별
def causal_comparison(morpheme1, morpheme2):
    relation_similarity = op.comparison(morpheme1, morpheme2)
    return relation_similarity

# 제목과 본문에서 자주 언급되어 있는 가져온 뒤, 
# 제목이 실제로 본문을 요약하고 있는 것인지 점수로 표시
def WordtoVec_exclusiveA(title, text):
    title_list = cm.often_top_n(title)
    article_list = cm.often_top_n(text)
    result = cm.morpheme_model_AA(title_list, article_list)
    return result

# 파라미터 배열을 가져와 최종 점수 계산
def evaluation_moduleA(num1, num2, param_arrayA):
    reliability_1 = num1 * param_arrayA[0] + num2 * param_arrayA[1] + param_arrayA[2]
    return reliability_1


# publicity_article.py
# Written by Byeongho Hwang (황병호)

# model_factcheck.py가 전반적인 기능을 크게 구현해놓은 연결이라고 한다면,
# publicity_article.py는 그 메이저 모듈 중 하나인 홍보성 기사 감지 기능의
# 각 기능의 세부 기능과 흐름을 구현해놓은 것이다.

# SPDX-FileCopyrightText: © 2021 Byeongho Hwang <crovas@kaist.ac.kr>
# SPDX-License-Identifier: BSD-3-Clause

# (2) Publicity Article Checker
# Functions Required::
# positivity_checker()
# propernoun_search()
# sudden_leap()
# conjunction_association()
# evaluation_moduleB()

# 긍정/부정 정도 측정은 인공지능 모델을 통해 이루어진다.
# 인공지능 모델이 문장을 단위로 긍정/부정을 판별하므로
# 유형에 맞추어 텍스트를 문장 단위로 쪼개주고, 문단 단위로 긍정 정도를 계산해야한다.
def positivity_checker(text, mode = 'context'):

    if mode == 'title':
        positivity = pc.use_positivity_model(text)
        return positivity
    
    if mode == 'context':
        paragraph_arr = text.split('\n')
        positivity = []
        for paragraph in paragraph_arr:
            sentence_arr = paragraph.split('.')
            sentence_positivity_sum = 0
            sentence_count = 0
            for sentence in sentence_arr:
                if len(sentence) < 3: pass
                else:
                    try:
                        positivity_sen = pc.use_positivity_model(sentence)
                        print(positivity_sen)
                        sentence_count = sentence_count + 1
                        sentence_positivity_sum = sentence_positivity_sum + positivity_sen
                    except: pass
            if sentence_count == 0: pass
            else:
                temp_positivity = sentence_positivity_sum/sentence_count
                positivity.append(temp_positivity)
        return positivity

# 고유명사 판별은 키스티의 기관 검색을 이용한다.
# 페이지의 보안에 따라 url을 통해 검색을 진행할 수 없고,
# 오로지 실제 태그와 브라우저 조종을 이용해서만 검색이 가능하기 때문에
# selenium 라이브러리를 이용해 실제 드라이버로 브라우저를 열어 검색을 진행한다.
def propernoun_search(text1, text2):
    propernoun_array1 = []
    propernoun_array2 = []
    driver_path = settingbox.get_directory('chromedriver')
    noun_arr1 = cm.get_noun_array(text1)
    noun_arr2 = []
    text2_arr = text2.split('\n')
    for paragraph in text2_arr:
        if len(paragraph) > 2:
            arraycomponent = cm.get_noun_array(paragraph)
            noun_arr2.append(arraycomponent)
    propernoun_array1, propernoun_array2 = pn.search_propernoun(noun_arr1, noun_arr2, driver_path = driver_path)
    return propernoun_array1, propernoun_array2

# 홍보하고자 하는 제시어가 나왔을 때 문장이 어느 정도로 긍정적이게 제시되느냐를 계산한다.
def sudden_leap(pos_title, pos_summary, arr_title, arr_content):
    # data type: pos_title - float, pos_summary - float array, arr_title - string array, arr_content - string array
    sudden_leap_degree = op.leap(pos_title, pos_summary, arr_title, arr_content)
    return sudden_leap_degree

# 접속사를 이용해 state를 구분, 물건을 홍보하고자 하는 목적이 어느 정도나 있는지 확인한다.
def conjunction_association(text):
    conjunction_check = op.check(text)
    return conjunction_check

# 홍보성 기사 점수 계산
def evaluation_moduleB(num1, num2, param_arrayB):
    reliability_2 = num1 * param_arrayB[0] + num2 * param_arrayB[1] + param_arrayB[2]
    return reliability_2


# republishing_same.py
# Written by Byeongho Hwang (황병호)

# model_factcheck.py가 전반적인 기능을 크게 구현해놓은 연결이라고 한다면,
# republishing_same.py는 그 메이저 모듈 중 하나인 동일 기사 반복 게재 탐지 기능의
# 각 기능의 세부 기능과 흐름을 구현해놓은 것이다.

# SPDX-FileCopyrightText: © 2021 Byeongho Hwang <crovas@kaist.ac.kr>
# SPDX-License-Identifier: BSD-3-Clause

# (3) Republishing Same Article Checker
# Functions Required::
# morpheme_separation - From modA
# sql_republish_search
# make_summary
# WordtoVec_exclusiveB
# make_keywordlist
# evaluation_moduleC

# 데이터베이스에 접근해 언론사, 기자, 유사기사를 검색한다.
def sql_republish_search(keyword_array, personname, pressname):
    similar_article, reporter_score, press_score = op.search(keyword_array, personname, pressname)
    return similar_article, reporter_score, press_score

# 원래도 기사를 요약했듯, 새롭게 검색된 기사 역시 요약한다.
def make_summary(text):
    summary = sr.rps_summary(text)
    return summary

# 유사 기사 본문과 원래 기사 본문의 유사도를 검색한다.
def WordtoVec_exclusiveB(morpheme1, morpheme2):
    similarity = cm.morpheme_model_BB(morpheme1, morpheme2)
    return similarity

# 자주 언급되는 단어의 리스트 추출
def make_keywordlist(text):
    arr = cm.often_top_n(text, n=10)
    return arr

# 동일 기사 반복 게재 점수 계산
def evaluation_moduleC(num1, num2, num3, param_array):
    reliability_3 = num1 * param_array[0] + num2 * param_array[1] + num3 * param_array[2] + param_array[3]
    return reliability_3