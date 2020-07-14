import pickle
import pandas as pd
import requests
from sklearn import svm, metrics

    # csv = pd.read_csv('Challenger_Ranked_Games.csv')
    #
    # blue_win = csv['blueWins']
    # red_win = csv['redWins']
    #
    # blue_data = csv.iloc[:, 3: 26]
    # red_data = csv.iloc[:, 27:50]
    #
    # blue_data['gameDuraton'] = csv['gameDuraton']
    # red_data['gameDuraton'] = csv['gameDuraton']
    #
    # blue_data['team'] = 100 # 블루진영 : 100
    # red_data['team'] = 200  # 레드진영 : 200
    #
    # new_cols = {x:y for x, y in zip(red_data.columns, blue_data.columns)}
    # train_data = blue_data.append(red_data.rename(columns=new_cols), ignore_index=True)
    # train_label = blue_win.append(red_win, ignore_index=True)


# print('train start')
# clf = svm.SVC()
# clf.fit(train_data, train_label)
# print('train complete')

# 학습한 내용을 미리 저장해놓고 train data에 변화가 없으면 학습된 데이터를 사용하도록 함.
# with open('res.pkl','wb') as f: # 학습내용 저장
#   pickle.dump(clf,f) # 오픈한 파일에 저장

user_name = input('검색할 사용자 닉네임을 입력하시오  : ')

# riot api에서 전적 가져오기
# api를 너무 자주 사용하면 제한이 걸리므로 텀을 두고 실행하는 것이 좋다.
api_key = '?api_key=' + 'api key를 여기에 적으시오.'
api = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + user_name + api_key   # user 정보 검색하기 (계정 id를 검색하기 위함)
r = requests.get(api)
api = "https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/" + r.json()['accountId'] + api_key # 계정 id를 통해 전적 검색하기
r = requests.get(api)

pre_num = 30    # 예측할 경기의 개수
count = pre_num
game_id = []    # 경기 id
player_champId = []     # 경기마다 user의 champion Id를 통해서 user의 정보를 찾아냄.
for match in r.json()['matches']:
    if match['queue'] == 420 or match['queue'] == 440 :   # solo rank or duo rank만 가져옴.
        game_id.append(match['gameId']) # 최근 10판의 gameId를 가져옴
        player_champId.append(match['champion'])
        count -= 1
    if count == 0:
        break

api = "https://kr.api.riotgames.com/lol/match/v4/matches/"  # 경기 정보를 가져오는 api

test_Alldata = []   # 검색한 전적에서 가져올 test data set
test_Alllabel = []  # 검색한 전적에서 가져올 test label set

for i, g in enumerate(game_id):
    test_data = {}  # 한 경기의 test data를 저장할 dicionary
    tmp_api = api + str(g) + api_key    # game_id를 통해 api에 접근
    r = requests.get(tmp_api)

    match = r.json()
    participants = match['participants']    # 경기의 참여자 정보를 가져옴
    for part in participants:
      if player_champId[i] == part['championId']:    # user의 champion Id를 통해 teamId 찾기 ( 랭크 경기는 champion이 중복 될 수 없음. )
          teamId = part['teamId']
          test_label = [int(part['stats']['win'])]
          test_Alllabel.append(test_label)
          break

    for t in r.json()['teams']:
       if t['teamId'] == teamId:

           test_data['blueFirstBlood'] = float(t['firstBlood'])
           test_data['blueFirstTower'] = float(t['firstTower'])
           test_data['blueFirstBaron'] = float(t['firstBaron'])
           test_data['blueFirstDragon'] = float(t['firstDragon'])
           test_data['blueFirstInhibitor'] = float(t['firstInhibitor'])
           test_data['blueDragonKills'] = float(t['dragonKills'])
           test_data['blueBaronKills'] = float(t['baronKills'])
           test_data['blueTowerKills'] = float(t['towerKills'])
           test_data['blueInhibitorKills'] = float(t['inhibitorKills'])

    test_data["blueWardPlaced"] = 0.
    test_data["blueWardkills"] = 0.
    test_data["blueKills"] = 0.
    test_data["blueDeath"]  = 0.
    test_data["blueAssist"]  = 0.
    test_data["blueChampionDamageDealt"]  = 0.
    test_data["blueTotalGold"] = 0.
    test_data["blueTotalMinionKills"]  = 0.
    test_data["blueTotalLevel"] = 0.
    test_data["blueAvgLevel"]  = 0.
    test_data["blueJungleMinionKills"] = 0.
    test_data["blueKillingSpree"] = 0.
    test_data["blueTotalHeal"] = 0.
    test_data["blueObjectDamageDealt"] = 0.

    for part in participants:
        if part['teamId'] == teamId:
            stats = part['stats']
            test_data["blueWardPlaced"] += float(stats['wardsPlaced'])
            test_data["blueWardkills"] += float(stats['wardsKilled'])
            test_data["blueKills"] += float(stats['kills'])
            test_data["blueDeath"] += float(stats['deaths'])
            test_data["blueAssist"] += float(stats['assists'])
            test_data["blueChampionDamageDealt"] += float(stats['totalDamageDealtToChampions'])
            test_data["blueTotalGold"] += float(stats['goldEarned'])
            test_data["blueTotalMinionKills"] += float(stats['totalMinionsKilled'])
            test_data["blueTotalLevel"] += float(stats['champLevel'])
            test_data["blueAvgLevel"] += float(stats['champLevel'])
            test_data["blueJungleMinionKills"] += float(stats['neutralMinionsKilledTeamJungle']+stats['neutralMinionsKilledEnemyJungle'])
            test_data["blueKillingSpree"] += float(stats['killingSprees'])
            test_data["blueTotalHeal"] += float(stats['totalHeal'])
            test_data["blueObjectDamageDealt"] += float(stats['damageDealtToObjectives'])
    test_data["blueAvgLevel"] /= 5
    test_data['gameDuraton'] = match['gameDuration']
    test_data['team'] = float(teamId)

    test_Alldata.append(test_data)

with open('res.pkl','rb') as f: # 학습 모델 파일 읽어오기
  clf = pickle.load(f)

pre_label = []
for i in range(pre_num):
  test_data = pd.DataFrame(test_Alldata[i], index=[0])
  test_label = test_Alllabel[i]
  pre = clf.predict(test_data)
  pre_label.append(pre)
  print("predict : {} ,  result : {} ".format(pre, test_label))

score = metrics.accuracy_score(test_Alllabel, pre_label)
print("predict score :", score)




