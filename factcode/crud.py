# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Original by Google Inc.,
# Editted by Byeongho Hwang (황병호)

# crud.py에서는 url에 따라 어떤 정보를 표시해야하는 지 
# 구분해 그에 따른 정보를 불러오도록 명령한다.
# 현재 페이지는 두 가지 밖에 표시되지 않으며, 
# 필요한 확장 기능에 따라 url을 배정해 추가 기능 구현

# SPDX-FileCopyrightText: © 2021 Byeongho Hwang <crovas@kaist.ac.kr>
# SPDX-License-Identifier: BSD-3-Clause

from factcode import get_model
from flask import Blueprint, Flask, redirect, render_template, request, url_for, jsonify
import base64

crud = Blueprint('crud', __name__)

# 신뢰도 Web/App 환산
def conversion(reliability):
    if reliability == -1: convertedReliability = -1
    elif reliability > -0.1 and reliability <= 20: convertedReliability = 1
    elif reliability > 20 and reliability <= 40: convertedReliability = 2
    elif reliability > 40 and reliability <= 60: convertedReliability = 3
    elif reliability > 60 and reliability <= 80: convertedReliability = 4
    elif reliability > 80: convertedReliability = 5
    return convertedReliability

# ------------ base ------------
# 기본 url로, 처음 접속하게 되면 표시되는 페이지다.
@crud.route("/")
def list():
    
    # 페이지 토큰 받아오기
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')
    
    # 데이터베이스에서 요구하는 기본 리스트 정보 받아오기
    bestarticles, next_page_token = get_model().list(cursor=token)
    
    # html template 렌더링
    return render_template(
        "list.html",
        barticles=bestarticles,
        next_page_token=next_page_token)

# ------------ factchecked API ------------
@crud.route('/factchecked/<type>/<path:link>')
def factchecking(type, link):

    # 반복적인 호출로 인한 오류를 방지하기 위한 0 세팅
    rel1 = 0
    rel2 = 0
    rel3 = 0
    relf = 0

    try:
        # btoa 인코딩 결과를 utf-8로 변환
        b64link = base64.b64decode(link)
        decodedlink = b64link.decode('utf-8')
        print(decodedlink)

        # 뉴스에 대한 신뢰도 얻어오기
        rel1, rel2, rel3, relf = get_model().factchecking(decodedlink)

        # 형태에 따른 반환 수치 환산
        if type == 'html':
            rel1 = conversion(rel1)
            rel2 = conversion(rel2)
            rel3 = conversion(rel3)
            relf = conversion(relf)
    except: pass

    if type == 'html':
        # 페이지 토큰 받아오기
        token = request.args.get('page_token', None)
        if token:
            token = token.encode('utf-8')

        # html template 렌더링
        return render_template(
        "list.html",
        reliability_1=rel1,
        reliability_2=rel2,
        reliability_3=rel3,
        reliability_final=relf)

    elif type == 'rest':
        # json 반환
        return jsonify(
            reliability_1=rel1,
            reliability_2=rel2,
            reliability_3=rel3,
            reliability_final=relf)

