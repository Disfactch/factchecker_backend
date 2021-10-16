# coding:UTF-8
# 1번 줄의 주석은 주석이 아닌 코드의 부분으로, 지우면 코드가 작동하지 않으므로 주의.

# 여섯 개의 최적화 함수가 포함되어 있다.
# (1) causal analysis:: Written by Yunji Lee (이윤지)
# 명사간의 인과관계를 파악해 문장 내 도치 여부를 파악한다.

# (2) conjunction analysis:: Written by Subin Kim (김수빈)
# 문장 내 접속사를 이용해 분위기 전환 정도를 파악한다.

# (3) sqlsearch database searching:: Written by Yunji Lee (이윤지), Editted by Byeongho Hwang (황병호)
# 데이터베이스에 접근해 기사, 언론사, 유사 기사 정보를 얻는 과정을 수행한다.

# (4) sudden leap analysis:: Written by Byeongho Hwang (황병호)
# 분석된 정보들을 이용해 홍보성 기사일 가능성을 계산한다.

# (5) propernoun searching:: Written by Byeongho Hwang (황병호)
# 주어진 명사가 기업/기관의 이름인지 파악한다.

# (6) summary making:: Written by Hanna Jeon (전한나)
# 본문을 그대로 가져와 처리할 때 너무 많은 시간이 소요될 경우, 요약을 통해 시간을 단축하기 위한 함수이다.

# Arranged by Byeongho Hwang (황병호)

# SPDX-FileCopyrightText: © Byeongho Hwang <crovas@kaist.ac.kr>, Subin Kim <subinga18@naver.com>, Yunji Lee <qwerty5098@kyonggi.ac.kr>, Hanna Jeon <jhn90928@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# (1) causal analysis:: Written by Yunji Lee (이윤지)
# 명사간의 인과관계를 파악해 문장 내 도치 여부를 파악한다.

def comparison(morpheme1, morpheme2):
    
    print(type(morpheme1))
    print(type(morpheme2))

    for i in range(len(morpheme1)):
        print(type(morpheme1[i]))
        print(morpheme1[i])
        morpheme1[i] = str(morpheme1[i][0])
        print(morpheme1[i])
    for j in range(len(morpheme2)):
        morpheme2[j] = str(morpheme2[j][0])
    
    #string화
    s_morpheme1 = ",".join(str(i) for i in morpheme1)
    s_morpheme2 = ",".join(str(j) for j in morpheme2)

    print(type(s_morpheme1))
    print(type(s_morpheme2))

    morphemelist = []
    morphemelist.append(str(s_morpheme1))
    morphemelist.append(str(s_morpheme2))
    # morphemelist = [s_morpheme1, s_morpheme2]
    
    #TF-IDF값을 활용하여 유사도 계산
    tfidf_vectorizer=TfidfVectorizer(min_df=1)  
    tfidf_matrix=tfidf_vectorizer.fit_transform(morphemelist)
    
    mat_relation_similarity=(tfidf_matrix*tfidf_matrix.T)
    
    #float화
    relation_similarity=(round(float(mat_relation_similarity[0, 1]),2)*100)*10
    
    return relation_similarity


# (2) conjunction analysis:: Written by Subin Kim (김수빈)
# 문장 내 접속사를 이용해 분위기 전환 정도를 파악한다.

def check(text):
    conjunction_check = 0.5
    return conjunction_check

# 순접,인과,보완,종결 : 1 / 역접,전환 : 0
def conj(article):
    
    state = 0.5
    same =['이어','그리고','게다가','더욱이','더구나''뿐만 아니라','동시에','그런 점에서'
    ,'그러므로','따라서','그러니까','그리하여','그렇게','때문에','그래서','그러면','그러니'
    ,'즉','곧','예를 들면','사실상'
    ,'결국','결론적으로']

    differ = ['그러나','하지만','그렇지만','그럼에도','반면에','오히려','반대로','그런데','다른 한편','다만','바꿔 말하면']

    for i in range(len(article)):
        for j in range(len(same)):
            if same[j] in article[i]:
                state = 1
                list_same=[i]
        
        for j in range(len(differ)):
            if differ[j] in article[i]:
                state = 0
                list_differ=[i]

    print(state)
    print('same이 들어간 list 번호: ',list_same)
    print('differ이 들어간 list 번호: ',list_differ)

    return state


# (3) sqlsearch database searching:: Written by Yunji Lee (이윤지), Editted by Byeongho Hwang (황병호)
# 데이터베이스에 접근해 기사, 언론사, 유사 기사 정보를 얻는 과정을 수행한다.

def rpt_score(data1, data2):
    if data1 == 0: result = -1
    else: result = 20*data2/data1
    return result

def prs_score(data1, data2):
    if data1 == 0: result = -1
    else: result = 20*data2/data1
    return result

def search(keyword_array, personname, pressname):
    connect = pymysql.connect(host='34.64.153.163', user='root', password='passw0rd', db='factchecker', charset='utf8mb4')
    cur = connect.cursor()

    keyword_plusarray = []
    for keyword in keyword_array:
        keyword_plus = keyword + ';'
        keyword_plusarray.append(keyword_plus)

    # keyword searching query
    # 아래 식을 만들기 위해 for문을 사용한다.
    # query_key ="((REPLACE((...),'noun8','noun8_plus')),'noun9','noun9_plus'))"
    query_key = ""
    if keyword_array == []: query_key = "content"
    else:
        for i in range(len(keyword_array)):
            if i == 0: query_key = "(REPLACE(content, '" + keyword_array[i] + "', '" + keyword_plusarray[i] + "'))"
            else: query_key = "(REPLACE(" + query_key + ", '" + keyword_array[i] + "', '" + keyword_plusarray[i] + "'))"
    query_keyword = "SELECT content FROM newsbox ORDER BY (((LENGTH(" + query_key + ")) - LENGTH(content))/LENGTH(';')) DESC LIMIT 1"

    data_keyword = cur.execute(query_keyword)
    connect.commit()
    data_keyword = cur.fetchmany(size=1)
    data_keyword = data_keyword[0][0]
    print(data_keyword)

    # reporter reliablity query
    query_reporter1 = "SELECT COUNT(*) FROM newsbox WHERE (reporter = '" + personname + "')"
    data_reporter1 = cur.execute(query_reporter1)
    connect.commit()
    data_reporter1 = cur.fetchmany(size=1)
    data_reporter1 = data_reporter1[0][0]

    query_reporter2 = "SELECT SUM(rel3) FROM newsbox WHERE (reporter = '" + personname + "')"
    data_reporter2 = cur.execute(query_reporter2)
    connect.commit()
    data_reporter2 = cur.fetchmany(size=1)
    data_reporter2 = data_reporter2[0][0]

    # pressname reliability query
    query_press1 = "SELECT COUNT(*) FROM newsbox WHERE (reporter = '" + pressname + "')"
    data_press1 = cur.execute(query_press1)
    connect.commit()
    data_press1 = cur.fetchmany(size=1)
    data_press1 = data_press1[0][0]

    query_press2 = "SELECT SUM(rel3) FROM newsbox WHERE (reporter = '" + pressname + "')"
    data_press2 = cur.execute(query_press2)
    connect.commit()
    data_press2 = cur.fetchmany(size=1)
    data_press2 = data_press2[0][0]

    if data_reporter2 == 'None': data_reporter2 = 0
    if data_press2 == 'None': data_press2 = 0

    similar_article = data_keyword
    reporter_score = rpt_score(data_reporter1, data_reporter2)
    press_score = prs_score(data_press1, data_press2)

    if reporter_score == -1: reporter_score = 70
    if press_score == -1: press_score = 70

    

    return similar_article, reporter_score, press_score


# (4) sudden leap analysis:: Written by Byeongho Hwang (황병호)
# 분석된 정보들을 이용해 홍보성 기사일 가능성을 계산한다.

def decide_type(pos_title, pos_summary):
    pos = 0
    count = 0
    for i in pos_summary:
        count = count + 1
        pos = pos + i
    pos_sum = float(pos/count)

    if pos_title > 0 and pos_sum > 0: return 1
    if pos_title == 0 and pos_sum > 0: return 2
    if pos_title < 0 and pos_sum > 0: return 3
    if pos_title > 0 and pos_sum == 0: return 4
    if pos_title == 0 and pos_sum == 0: return 5
    if pos_title < 0 and pos_sum == 0: return 6
    if pos_title > 0 and pos_sum < 0: return 7
    if pos_title == 0 and pos_sum < 0: return 8
    if pos_title < 0 and pos_sum < 0: return 9
    return 0


def check_there(noun, content):
    which_paragraph_has_the_pnoun = []
    paragraph_number = 1
    for paragraph in content:
        if noun in paragraph: which_paragraph_has_the_pnoun.append(paragraph_number)
        paragraph_number = paragraph_number + 1
    return which_paragraph_has_the_pnoun


def first_leap_calculation(title_propernoun_leap, max_leap,checker):
    leap_degree = 0
    if checker == 1: leap_degree = (title_propernoun_leap + max_leap/2)
    if checker == 0: leap_degree = 2*(title_propernoun_leap + max_leap/2)
    return leap_degree


def second_leap_calculation(sudden_leap_degree, mode):
    
    leap_degree = sudden_leap_degree

    if mode == 1: # 제목 긍정, 기사 긍정 -> 100% 반영
        leap_degree = sudden_leap_degree * 1.0
    if mode == 2: # 제목 중립, 기사 긍정 -> 80% 반영
        leap_degree = sudden_leap_degree * 0.8
    if mode == 3: # 제목 부정, 기사 긍정 -> 80% 반영
        leap_degree = sudden_leap_degree * 0.8
    if mode == 4: # 제목 긍정, 기사 중립 -> 100% 반영
        leap_degree = sudden_leap_degree * 1.0
    if mode == 5: # 제목 중립, 기사 중립 -> 50% 반영
        leap_degree = sudden_leap_degree * 0.5
    if mode == 6: # 제목 부정, 기사 중립 -> 30% 반영
        leap_degree = sudden_leap_degree * 0.3
    if mode == 7: # 제목 긍정, 기사 부정 -> 100% 반영
        leap_degree = sudden_leap_degree * 1.0
    if mode == 8: # 제목 중립, 기사 부정 -> 10% 반영
        leap_degree = sudden_leap_degree * 0.1
    if mode == 9: # 제목 부정, 기사 부정 -> 30% 반영
        leap_degree = sudden_leap_degree * 0.3
    
    return leap_degree

def leap(pos_title, pos_summary, arr_title, arr_content):
    sudden_leap_degree = -1

    # Decide type
    art_type = decide_type(pos_title, pos_summary)

    # Search propernoun which is in title first
    title_propernoun_leap = 0
    checked_p = ''
    for pnoun in arr_title:
        check_in_there = check_there(pnoun, arr_content)
        if check_in_there == []:
            scaled_leap = 0
        else:
            pos_pyes = 0
            pos_pno = 0
            paragraph_count_pyes = 0
            paragraph_count_pno = 0
            total = len(pos_summary)
            
            for i in range(total):
                j = i + 1
                if j in check_in_there:
                    paragraph_count_pyes = paragraph_count_pyes + 1
                    pos_pyes = pos_pyes + pos_summary[i]
                else:
                    paragraph_count_pno = paragraph_count_pno + 1
                    pos_pno = pos_pno + pos_summary[i]
            if paragraph_count_pyes == 0: pyes = 0
            else: pyes = pos_pyes/paragraph_count_pyes
            if paragraph_count_pno == 0: pno = 0
            else: pno = pos_pno/paragraph_count_pno
            scaled_leap = 50*(pyes-pno)+50
        if title_propernoun_leap < scaled_leap:
            title_propernoun_leap = scaled_leap
            checked_p = pnoun

    # Search by leap scale
    leap_arr = []
    for i in range(len(pos_summary)-1):
        j = i + 1
        pos_leap = pos_summary[j] - pos_summary[i]
        leap_arr.append(pos_leap)
    max_leap = max(leap_arr)
    checked_a = []
    for i in range(len(pos_summary)-1):
        j = i + 1
        if max_leap == leap_arr[i]: checked_a.append(arr_content[j])
    checking = check_there(checked_p, checked_a)
    if checking == []: checker = 1
    else: checker = 0

    print(title_propernoun_leap)
    print(max_leap)
    print(checker)

    sudden_leap_degree = first_leap_calculation(title_propernoun_leap, max_leap, checker)
    sudden_leap_degree = second_leap_calculation(sudden_leap_degree, art_type)

    sudden_leap_degree = 100-(100*sudden_leap_degree)

    return sudden_leap_degree

# (5) propernoun searching:: Written by Byeongho Hwang (황병호)
# 주어진 명사가 기업/기관의 이름인지 파악한다.

def search_propernoun(noun_arr1, noun_arr2):

    searcharray_1 = []
    searcharray_2 = []
    for noun1 in noun_arr1:
        if len(noun1) > 2: searcharray_1.append(noun1)
    for paragraph_noun in noun_arr2:
        paragraph_noun_arr = []
        for noun2 in paragraph_noun:
            if len(noun2) > 2: paragraph_noun_arr.append(noun2)
        searcharray_2.append(paragraph_noun_arr)
    
    connect = pymysql.connect(host='34.64.153.163', user='root', password='passw0rd', db='factchecker', charset='utf8mb4')
    cur = connect.cursor()

    # keyword searching query
    propernoun_arr1 = []
    for target_nounA in searcharray_1:
        try:
            query_keyword = "SELECT count(*) FROM nounbox WHERE noun LIKE '%" + target_nounA + "%' ORDER BY id;"
            data_keyword = cur.execute(query_keyword)
            connect.commit()
            data_keyword = cur.fetchmany(size=1)
            data_keyword = data_keyword[0][0]
            print(data_keyword)
            if data_keyword != 0: propernoun_arr1.append(target_nounA)
        except: pass
    
    propernoun_arr2 = []
    for paragraph_nouns in searcharray_2:
        propernoun_semiarr2 = []
        for target_nounB in paragraph_nouns:
            try:
                query_keyword = "SELECT count(*) FROM nounbox WHERE noun LIKE '%" + target_nounB + "%' ORDER BY id;"
                data_keyword = cur.execute(query_keyword)
                connect.commit()
                data_keyword = cur.fetchmany(size=1)
                data_keyword = data_keyword[0][0]
                print(data_keyword)
                if data_keyword != 0: propernoun_semiarr2.append(target_nounB)
            except: pass
        propernoun_arr2.append(propernoun_semiarr2)

    return propernoun_arr1, propernoun_arr2

# (6) summary making:: Written by Hanna Jeon (전한나)
# 본문을 그대로 가져와 처리할 때 너무 많은 시간이 소요될 경우, 요약을 통해 시간을 단축하기 위한 함수이다.

# summary 1
def sum1(title, content):
    summary = content
    return summary

# summary 2
def sum2(title, content):
    summary = content
    return summary

# summary 3
def sum3(title, content):
    summary = ''
    paragraph_list = content.split('\n')
    for paragraph in paragraph_list:
        sentence_list = []
        sentence_list_mft = paragraph.split('. ')
        for sentence in sentence_list_mft:
            if len(sentence) > 3: sentence_list.append(sentence)
        if len(sentence_list) == 0: paragraph_summary = ''
        elif len(sentence_list) <= 2: paragraph_summary = paragraph + '\n'
        else: paragraph_summary = sentence_list[0] + ". " + sentence_list[-1] + '\n'
        if len(paragraph) < 2: paragraph_summary = ''
        summary = summary + paragraph_summary
    return summary

# summary 4
def sum4(title, content):
    summary = ''
    paragraph_list = content.split('\n')
    for paragraph in paragraph_list:
        sentence_list = []
        sentence_list_mft = paragraph.split('. ')
        for sentence in sentence_list_mft:
            if len(sentence) > 3: sentence_list.append(sentence)
        if len(sentence_list) == 0: paragraph_summary = ''
        elif len(sentence_list) == 1: paragraph_summary = paragraph + '\n'
        else: paragraph_summary = sentence_list[0] + '.\n'
        if len(paragraph) < 2: paragraph_summary = ''
        summary = summary + paragraph_summary
    return summary

# summary 5
def sum5(title, content):    
    from gensim.summarization.summarizer import summarize #gesnim 라이브러리 이용해서 기사 요약

    snews_contents = summarize(content)
    summary = snews_contents

    return summary

# summary for republishing module
def rps_summary(content):

    from gensim.summarization.summarizer import summarize #gesnim 라이브러리 이용해서 기사 요약

    snews_contents = summarize(content)
    summary = snews_contents
    text = summary
    return text

