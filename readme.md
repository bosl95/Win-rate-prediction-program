## Win rate prediction program
- Pandas
- Sklearn : svm, metrics
- pickle

## Detail
- [league of legends](https://kr.leagueoflegends.com/ko-kr/) 게임의 승률을 예측하는 프로그램
- 닉네임을 입력 받고, 해당 유저의 최근 경기 기록을 가져와 그 경기 데이터를 이용한 승률을 예측한다.


> #### 1. 학습할 데이터와 학습 모델 만들기
- kaggle에 등록된 challenger 랭크의 경기 데이터를 가져온다. [(출처)](https://www.kaggle.com/gyejr95/league-of-legends-challenger-ranked-games2020)
- 하나의 행마다 매 경기의 데이터들이 들어있는데, red 팀과 blue 팀의 데이터가 같이 들어있으므로 red팀과 blue 팀 데이터를 나눈 다음 하나의 학습 데이터로 만들어준다. (같은 위치에 놓여야할 blue, red 데이터가 컬럼명이 살짝 달라서 컬럼명을 바꿔서 다시 합치는데  시간이 오래 걸렸다.)
		
		# blue, red 데이터를 하나의 데이터 프레임으로 합치기. (같은 내용인데 컬럼명만 다르기 때문에 데이터 가공이 필요하다.)
		new_cols = {x:y for x, y in zip(red_data.columns, blue_data.columns)}  
		train_data = blue_data.append(red_data.rename(columns=new_cols), ignore_index=True)  
		train_label = blue_win.append(red_win, ignore_index=True)

pickle 모듈을 통해 학습 데이터 모델을 저장해 불필요한 학습 시간을 단축시킨다.

> #### 2. 경기 데이터 가져오기 (test data)
- 닉네임을 입력받은 다음 Liot API를 이용해 account ID를 우선적으로 알아낸다. 
- 찾아낸 account ID를 통해 최근 전적을 검색한다. 
- 이때 최근 전적 중에서 솔로 혹은 듀오 랭크로만 데이터이어야 하고, 최근 전적을 나타내는 데이터에 유저의 game ID와 champion number를 가져온다. ( 솔로 랭크는 10명의 게임 참가자 중 중복되는 챔피언(캐릭터)를 가질 수 없으므로, 경기 데이터마다 챔피언을 통해 검색하는 유저의 정보를 찾는다.)
- 그 game ID를 통해 경기 데이터에 접근하고, champion number를 통해 검색한 유저가 해당하는 팀(red or blue)을 찾을 수 있다. 
- 검열된 경기데이터에서 테스트하는데 필요한 정보를 뽑아 딕셔너리 타입으로 저장해준다.
~~처음엔 defaultdict(float)로 만들어서 DataFrame을 생성해주려고 했으나 에러가 계속 떴다...~~ 

		pd.DataFrame(test_Alldata[i], index=[0])
		# dictionary 타입의 테스트 데이터를 DataFrame으로 만들어주는 모드
		# 각 딕셔너리의 값이 리스트 형태가 아닌 단일 형태의 값인 경우 DataFrame으로 변환 시 에러가 발생한다. 따라서 index = [0]으로 지정해주거나 값을 리스트 형태로 만들어준다.