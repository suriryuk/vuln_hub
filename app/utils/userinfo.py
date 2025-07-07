from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql import func

import datetime

from db.base import User, UserChallenge, Challenge

def get_userinfo(current_user: str, db: Session) -> dict:
    # 정보들을 담을 딕셔너리
    infos = {}

    # 문제 수 조회
    chall_cnt = db.query(Challenge).count()
    infos['chall_cnt'] = chall_cnt

    # 풀이한 문제 수 조회
    solve_chall_cnt = db.query(UserChallenge).filter(UserChallenge.userid == current_user).count()
    infos['solve_chall_cnt'] = solve_chall_cnt

    # 점수 계산
    subquery = select(UserChallenge.challName).where(UserChallenge.userid == current_user)
    score = db.query(func.sum(Challenge.challScore)).filter(Challenge.challName.in_(subquery)).scalar()
    if score is None: score = 0 # 점수가 존재하지 않으면 0으로 초기화
    infos['score'] = score

    # 활동일 계산
    firstTime = db.query(User.registerDate).filter(User.userid == current_user).first()[0]
    act_time = datetime.datetime.now() - firstTime
    infos['act_time'] = act_time.days+1

    # 사용자별 점수 계산
    # 사용자 조회
    scores = {}
    users = db.execute(select(User)).scalars().all()
    # 사용자별 점수 계산
    for user in users:
        subquery = select(UserChallenge.challName).where(UserChallenge.userid == user.userid)
        score = db.query(func.sum(Challenge.challScore)).filter(Challenge.challName.in_(subquery)).scalar()
        
        if score is None: 
            score = 0

        scores[user.userid] = score
        print(scores)
    infos['user_scores'] = scores

    # Top 5 사용자 점수
    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    infos['top_scores'] = top_scores

    # line chart에 사용할 현재 사용자의 점수 획득 추이 계산
    results = (
        db.query(
            User.userid.label("UserID"),
            UserChallenge.challName.label("ChallengeName"),
            Challenge.challScore.label("ChallengeScore"),
            UserChallenge.solveTime.label("SolveTime"),
            func.sum(Challenge.challScore)
            .over(partition_by=User.userid, order_by=UserChallenge.solveTime)
            .label("CumulativeScore"),
        )
        .join(UserChallenge, User.userid == UserChallenge.userid)
        .join(Challenge, UserChallenge.challName == Challenge.challName)
        .filter(User.userid == current_user)  # 특정 유저ID 필터링
        .order_by(UserChallenge.solveTime)    # 풀이 시간 기준 정렬
        .all()
    )

    infos['line_labels'] = [row.SolveTime.strftime('%Y-%m-%d %H:%M:%S') for row in results]
    infos['line_data'] = [int(row.CumulativeScore) for row in results]

    return infos