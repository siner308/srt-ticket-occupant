# srt-ticket-occupant
새로고침 할시간에 짜는 코드

# quickstart

## installation (mac or linux based command)

```bash
git clone https://github.com/siner308/srt-ticket-occupant
cd srt-ticket-occupant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## env.txt

|name|description|
|---|---|
|ID|핸드폰번호|
|PW|비밀번호|
|DATE|검색대상일|
|FROM|출발역|
|TO|도착역|
|FIRST_START_TIME|탐색범위(시작)|
|FIRST_END_TIME|탐색범위(끝)|

## configuration

```bash
cp env.sample.txt env.txt
vi env.txt # set env and save
```

## start

```bash
python main.py
```
