# coding:utf-8
# 1번 줄의 주석은 주석이 아닌 코드의 부분으로, 지우면 코드가 작동하지 않으므로 주의.

# model_factcheck.py
# Written by Byeongho Hwang (황병호)

# model_factcheck.py는 구체적인 가짜뉴스 판별기를 구현해놓은 파일로,
# 각 메이저 모듈의 전체 과정이 표현되어 있다.

# SPDX-FileCopyrightText: © 2021 Byeongho Hwang <crovas@kaist.ac.kr>
# SPDX-License-Identifier: BSD-3-Clause

# 모듈 태그: 세 가지 기능을 하는 모듈과 테스트용 파일을 가져온다.
# 메이저 모듈 이외에 필요한 크롤링 도구와 문자열 재구성 등을 할 수 있는 파일도 가져온다.
# [START Module tagging]

# sdk에서 url 배포를 위해 실행시킬 경우 위 모듈을 사용
try:
    from factcode import crawler
    from factcode import morpheme
    from factcode import positivity
    from factcode import optimization
    from factcode import settingbox

# 로컬 컴퓨터로 실행시킬 경우 아래 모듈을 사용
except:
    import crawler
    import morpheme
    import positivity
    import optimization
    import settingbox

cw = crawler
mp = morpheme
pt = positivity
op = optimization

# [END Module tagging]

# 크롤링: 페이지의 보안 설정에 따라 어떤 라이브러리를 사용할 지 구분한 뒤,
# 사용할 라이브러리에 맞추어 링크를 가공해 필요한 정보를 얻는다.
# [START Crawling]
def get_titleAndContents(link):
    try:
        press, reporter, articletitle, articlecontents = cw.crawl_news(link)
    except:
        press = None
        reporter = None
        articletitle = None
        articlecontents = None
    return press, reporter, articletitle, articlecontents
# [END Crawling]

# 스트링 가공: 본문을 그대로 가져다 쓰면 기사가 너무 길어지기 때문에,
# 각 필요에 맞추어 시간이 오래 걸리는 모듈에는 요약본을 사용해야한다.
# [START Summarizing]
def get_summary(articletitle, articlecontents, classification):

    if classification == 1:
        summary = op.sum1(articletitle, articlecontents)
    elif classification == 2:
        summary = op.sum2(articletitle, articlecontents)
    elif classification == 3:
        summary = op.sum3(articletitle, articlecontents)
    elif classification == 4:
        summary = op.sum4(articletitle, articlecontents)
    elif classification == 5:
        summary = op.sum5(articletitle, articlecontents)
    else:
        summary = ''
    
    return summary
# [END Summarizing]


# [START Major Module]
# Running modules
# 팩트체커에는 세 가지 메이저 모듈이 존재한다.
# Three modules are in the factchecker:
# 1. Provoactive Title Checker (자극적인 제목 감지)
# 2. Publicity Article Checker (홍보성 기사 감지)
# 3. Republishing Same Article Checker (같은 기사 재업로드)

# (1) Provocative Title Checker
# Functions Required::
# morpheme_separation() - 형태소를 분리하는 역할
# causal_comparison() - 조사를 이용해 단어간 인과관계 파악
# WordtoVec_exclusiveA() - 단어간의 연관성 계산
# evaluation_moduleA() - 자극적 제목 정도 계산

def provocative_title_checker(articletitle, summary1, summary2):
    # Causal Relationship Comparison
    # 인과관계 비교
    morpheme1 = morpheme_separation(articletitle)
    morpheme2 = morpheme_separation(summary1)
    relation_similarity = causal_comparison(morpheme1, morpheme2)
    # print(relation_similarity)

    # Word2Vec AI Model
    # 워드투벡터 인공지능 모델
    WordtoVec_result = WordtoVec_exclusiveA(articletitle, summary2)
    # print(WordtoVec_result)

    # Final Score Evaluation
    reliability_1 = evaluation_moduleA(relation_similarity, WordtoVec_result, param_arrayA=[0.5,0.5,0])
    return reliability_1

# (2) Publicity Article Checker
# Functions Required::
# positivity_checker() - 긍정/부정 정도 측정
# propernoun_search() - 고유명사 여부 판별
# sudden_leap() - 제품이 소개됨과 동시에 분위기의 전환 정도 계산
# conjunction_association() - 접속사 연결관계 파악
# evaluation_moduleB() - 홍보성 기사 정도 계산

def publicity_article_checker(articletitle, summary3, summary4):
    # Propernoun-Atmosphere Relation Check
    # 고유명사 - 분위기 연관도 체크
    positivity_title = positivity_checker(articletitle, mode = 'title')
    positivity_summary = positivity_checker(summary3, mode = 'context')
    propernoun_titlesearch, propernoun_contentsearch = propernoun_search(articletitle, summary3)
    sudden_leap_degree = sudden_leap(positivity_title, positivity_summary, propernoun_titlesearch, propernoun_contentsearch)
    # print(sudden_leap_degree)

    # Conjuction Association
    # 접속사 연결 관계 파악
    conjunction_check = conjunction_association(summary4)
    # print(conjunction_check)

    # Final Score Evaluation
    reliability_2 = evaluation_moduleB(sudden_leap_degree, conjunction_check, param_arrayB=[0.5,0.5,0])
    return reliability_2

# (3) Republishing Same Article Checker
# Functions Required::
# morpheme_separation() - 형태소를 분리하는 역할
# sql_republish_search() - 데이터베이스의 탐색
# make_summary() - 유사 기사를 요약하는 과정
# WordtoVec_exclusiveB() - 단어간의 연관성 계산
# make_keywordlist() - 기사의 주요단어 추출
# evaluation_moduleC() - 기사간 유사도 계산

def republishing_same_checker(summary5, reporter, press):
    morpheme_processed_A = make_keywordlist(summary5)
    similar_article, reporter_score, press_score = sql_republish_search(morpheme_processed_A, reporter, press)
    summarized_s_article = make_summary(similar_article)
    morpheme_processed_B = make_keywordlist(summarized_s_article)
    similarity = WordtoVec_exclusiveB(morpheme_processed_A, morpheme_processed_B)

    # Final Score Evaluation
    reliability_3 = evaluation_moduleC(similarity, reporter_score, press_score, param_array=[0.3,0.3,0.3,10])
    return reliability_3

# [END Major Module]


# 세 가지 모듈에서 각 신뢰도가 계산되었으면, 마지막으로 최종 점수를 계산해주어야 한다.
# [START Manufacturing]
def manufacture_reliability(reliability_1, reliability_2, reliability_3, param_array):
    reliability_result = param_array[0]*reliability_1+param_array[1]*reliability_2+param_array[2]*reliability_3+param_array[3]
    return reliability_result
# [END Manufacturing]

# 웹페이지에 표시될 형태로 가공한다. 원래의 점수는 0~100으로 표현된다.
# Showing to the web
# [START Webbing]
def how_to_show_in_web(rel1, rel2, rel3, reliability_result):

    howtoshowinweb_1 = rel1
    howtoshowinweb_2 = rel2
    howtoshowinweb_3 = rel3
    howtoshowinweb_res = reliability_result

    if rel1 <= 0: howtoshowinweb_1 = 0
    elif rel1 > 100: howtoshowinweb_1 = 100
    if rel2 <= 0: howtoshowinweb_2 = 0
    elif rel2 > 100: howtoshowinweb_2 = 100
    if rel3 <= 0: howtoshowinweb_3 = 0
    elif rel3 > 100: howtoshowinweb_3 = 100
    if reliability_result <= 0: howtoshowinweb_res = 0
    elif reliability_result > 100: howtoshowinweb_res = 100

    return howtoshowinweb_1, howtoshowinweb_2, howtoshowinweb_3, howtoshowinweb_res
# [END Webbing]

# ------------------------------------------------------------------------------ #

# (1) Provocative Title Checker
# Functions Required:: morpheme_separation(), causal_comparison(), WordtoVec_exclusiveA(), evaluation_moduleA()

# 형태소 감지기
def morpheme_separation(text):
    morpheme_array = mp.get_morpheme(text)
    return morpheme_array

# 조사 비교를 통한 자극적 도치 가능성 판별
def causal_comparison(morpheme1, morpheme2):
    relation_similarity = op.comparison(morpheme1, morpheme2)
    return relation_similarity

# 제목과 본문에서 자주 언급되어 있는 가져온 뒤, 
# 제목이 실제로 본문을 요약하고 있는 것인지 점수로 표시
def WordtoVec_exclusiveA(title, text):
    title_list = mp.often_top_n(title)
    article_list = mp.often_top_n(text)
    result = mp.morpheme_model_AA(title_list, article_list)
    return result

# 파라미터 배열을 가져와 최종 점수 계산
def evaluation_moduleA(num1, num2, param_arrayA):
    reliability_1 = num1 * param_arrayA[0] + num2 * param_arrayA[1] + param_arrayA[2]
    return reliability_1


# (2) Publicity Article Checker
# Functions Required:: positivity_checker(), propernoun_search(), sudden_leap(), conjunction_association(), evaluation_moduleB()

# 긍정/부정 정도 측정은 인공지능 모델을 통해 이루어진다.
# 인공지능 모델이 문장을 단위로 긍정/부정을 판별하므로
# 유형에 맞추어 텍스트를 문장 단위로 쪼개주고, 문단 단위로 긍정 정도를 계산해야한다.
def positivity_checker(text, mode = 'context'):

    if mode == 'title':
        positivity = pt.use_positivity_model(text)
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
                        positivity_sen = pt.use_positivity_model(sentence)
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
def propernoun_search(text1, text2):
    propernoun_array1 = []
    propernoun_array2 = []
    driver_path = settingbox.get_directory('chromedriver')
    noun_arr1 = mp.get_noun_array(text1)
    noun_arr2 = []
    text2_arr = text2.split('\n')
    for paragraph in text2_arr:
        if len(paragraph) > 2:
            arraycomponent = mp.get_noun_array(paragraph)
            noun_arr2.append(arraycomponent)
    propernoun_array1, propernoun_array2 = op.search_propernoun(noun_arr1, noun_arr2, driver_path = driver_path)
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


# (3) Republishing Same Article Checker
# Functions Required::
# morpheme_separation(), sql_republish_search(), make_summary(), WordtoVec_exclusiveB(), make_keywordlist(), evaluation_moduleC()

# 데이터베이스에 접근해 언론사, 기자, 유사기사를 검색한다.
def sql_republish_search(keyword_array, personname, pressname):
    similar_article, reporter_score, press_score = op.search(keyword_array, personname, pressname)
    return similar_article, reporter_score, press_score

# 원래도 기사를 요약했듯, 새롭게 검색된 기사 역시 요약한다.
def make_summary(text):
    summary = op.rps_summary(text)
    return summary

# 유사 기사 본문과 원래 기사 본문의 유사도를 검색한다.
def WordtoVec_exclusiveB(morpheme1, morpheme2):
    similarity = mp.morpheme_model_BB(morpheme1, morpheme2)
    return similarity

# 자주 언급되는 단어의 리스트 추출
def make_keywordlist(text):
    arr = mp.often_top_n(text, n=10)
    return arr

# 동일 기사 반복 게재 점수 계산
def evaluation_moduleC(num1, num2, num3, param_array):
    reliability_3 = num1 * param_array[0] + num2 * param_array[1] + num3 * param_array[2] + param_array[3]
    return reliability_3