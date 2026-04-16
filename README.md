# 🐳 oz_Docker_prac

도커(Docker)를 활용하여 **FastAPI**, **MySQL(DB)**, 그리고 **Llama-3.2(Worker)**를 컨테이너화하고 상호 연결하는 풀스택 인프라 실습 프로젝트입니다.

## 📌 프로젝트 개요
- **FastAPI**: 백엔드 API 서버를 구축하고 외부와 통신하는 '입' 역할 수행
- **MySQL 8.0**: 서비스에 필요한 데이터를 안정적으로 저장하고 관리
- **Worker (LLM)**: `llama-cpp-python`을 이용해 로컬 LLM(Llama-3.2)을 구동하는 독립적 추론 엔진
- **Orchestration**: Docker Compose를 통해 3개의 이기종 컨테이너를 하나의 네트워크로 통합 관리
- **MySQL Workbench**: 로컬 환경에서 컨테이너 내부 DB의 데이터를 시각적으로 확인

## 🛠 기술 스택
- **Language**: Python 3.13 (FastAPI, Llama-cpp)
- **Framework**: FastAPI, SQLAlchemy
- **AI Model**: Llama-3.2-1B-Instruct (GGUF)
- **Infrastructure**: Docker, Docker Compose, MySQL 8.0

## 📂 파일 구성
- `main.py`: `/health-check` 엔드포인트를 포함한 API 코드
- `Dockerfile`: 파이썬 환경 구성 및 실행 명령 정의
- `docker-compose.yml`: API와 DB 서비스의 통합 설정 및 포트 매핑

## 📂 프로젝트 구조
```text
.
├── api/
│   ├── connection.py    # DB 엔진 및 세션 설정
│   ├── main.py          # API 엔드포인트 및 로직
│   └── Dockerfile       # FastAPI 환경 구성
├── worker/
│   ├── models/          # Llama-3.2 GGUF 모델 파일 저장
│   ├── main.py          # LLM 추론 실행 스크립트
│   └── Dockerfile       # LLM 구동 환경 (llama-cpp-python)
└── docker-compose.yml   # 멀티 컨테이너 통합 **설정**

--

## 🚀 주요 학습 및 업데이트 내용

### 1. 서비스 간 연결 (Service Discovery)
- **Network**: 도커 컴포즈 내부 네트워크를 통해 `api` 컨테이너가 `db`라는 호스트 이름으로 MySQL에 접속하는 원리 학습.
- **Depends On**: DB가 준비된 후 API가 실행되도록 서비스 시작 순서 제어.

### 2. 데이터 및 코드 보존 (Volumes)
- **DB Persistence**: `local_db` 볼륨을 설정하여 `docker compose down`으로 컨테이너가 삭제되어도 실제 데이터베이스 데이터는 유지되도록 설계.
- **Hot Reload**: 호스트의 코드 디렉토리를 컨테이너와 연결하여, 코드 수정 시 컨테이너 재시작 없이 즉시 반영(`--reload`).

### 3. AI Worker 분리 (Event-Driven 준비)
- 무거운 AI 추론 작업을 수행하는 **Worker**를 API 서버와 분리하여 설계.
- 향후 **Pub/Sub(발행/구독)** 모델을 도입하여 비동기식 이벤트 기반 아키텍처(EDA)로 확장할 수 있는 기초 구조 마련.

---

## 🚀 실행 및 접속 방법

### 1. 컨테이너 빌드 및 백그라운드 실행
터미널에서 아래 명령어를 입력합니다.
```bash
docker compose up -d --build

### 2. 엔드포인트 테스트
브라우저에서 아래 주소로 접속하여 정상 작동 여부를 확인합니다.
- Health Check: http://localhost:8000/health-check
- API Docs: http://localhost:8000/docs

### 3. B 접속 정보 (MySQL Workbench)
컨테이너 외부(호스트)에서 DB에 접속하기 위한 정보입니다.
- **Hostname**: `127.0.0.1` (또는 `localhost`)
- **Port**: `33061` (로컬 포트 충돌 방지를 위해 설정됨)
- **Username**: `root`
- **Password**: `password`
- **Default Schema**: `app_db`

### 4. Worker 로그 확인 (LLM 추론 결과)
LLM 모델(Llama-3.2)의 추론이 정상적으로 이루어지는지 터미널에서 실시간으로 확인할 수 있습니다.
```bash
docker compose logs -f worker

## 💡 주요 학습 내용
- 포트 포워딩(Port Forwarding): 호스트의 포트(8000, 33061)와 컨테이너 내부 포트(8000, 3306)를 연결하는 원리 이해.
- 의존성 관리(depends_on): DB 컨테이너가 먼저 실행된 후 API 서버가 기동되도록 설정.
- 볼륨 및 네트워크: 도커 컴포즈가 자동으로 생성하는 기본 네트워크를 통한 서비스 간 통신 확인.

