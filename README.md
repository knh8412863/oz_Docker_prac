# 🐳 oz_Docker_prac

도커(Docker)를 활용하여 **FastAPI**, **MySQL(DB)**, 그리고 **Llama-3.2(Worker)**를 컨테이너화하고 상호 연결하는 풀스택 인프라 실습 프로젝트입니다.

## 📌 프로젝트 개요
- **FastAPI**: 백엔드 API 서버를 구축하고 외부와 통신하는 '입' 역할 수행
- **Redis**: API 서버와 Worker 사이의 **메시지 브로커**. 요청 대기열(Queue) 관리 및 실시간 답변 전달(Pub/Sub) 수행.
- **MySQL 8.0**: 서비스에 필요한 데이터를 안정적으로 저장하고 관리
- **Worker (LLM)**: `llama-cpp-python`을 이용해 로컬 LLM(Llama-3.2)을 구동하는 독립적 추론 엔진
- **Orchestration**: Docker Compose를 통해 3개의 이기종 컨테이너를 하나의 네트워크로 통합 관리
- **MySQL Workbench**: 로컬 환경에서 컨테이너 내부 DB의 데이터를 시각적으로 확인

## 🛠 기술 스택
- **Language**: Python 3.13 (FastAPI, Llama-cpp)
- **Framework**: FastAPI (Backend), Llama-cpp-python (AI Inference)
- **AI Model**: Llama-3.2-1B-Instruct (GGUF)
- **Infrastructure**: Docker, Docker Compose, Redis 8, MySQL 8.0


## 📂 프로젝트 구조
```text
.
├── api/
│   ├── main.py          # Redis LPUSH 요청 및 StreamingResponse 처리
│   ├── connection.py    # DB 세션 설정
│   └── Dockerfile       # FastAPI 환경 구성
├── worker/
│   ├── models/          # Llama-3.2 GGUF 모델 파일
│   ├── main.py          # Redis BRPOP 작업 수신 및 LLM 추론/Publish
│   └── Dockerfile       # llama-cpp-python 환경 구성
├── .gitignore           # 대용량 모델 파일 및 캐시 제외 설정
└── docker-compose.yml   # 4개 서비스(API, DB, Worker, Redis) 통합 설정
```
---

## 🚀 주요 학습 내용

### 1. 비동기 메시지 큐 아키텍처 (Event-Driven)
- **Decoupling**: API 서버가 직접 추론하지 않고 Redis 큐에 작업을 넘김으로써, 무거운 AI 작업 중에도 API 서버가 응답 불능 상태가 되지 않도록 설계.
- **FIFO Queue**: Redis의 `LPUSH` / `BRPOP` 구조를 활용하여 요청이 들어온 순서대로 공정하게 처리.
- **Pub/Sub Streaming**: 특정 채널을 구독(`Subscribe`)하여 Worker가 생성하는 토큰을 실시간으로 클라이언트에게 스트리밍 전송.

### 2. 비동기 데이터베이스 연동 (Async SQLAlchemy)
- **aiomysql & AsyncSession**: 기존의 동기 방식이 아닌 `create_async_engine`을 활용하여 I/O 바운드 작업 시 서버 성능을 극대화하는 비동기 DB 처리 기법 학습.
- **관계형 모델링 (1:N)**: `Conversation`과 `Message` 테이블 간의 외래키(ForeignKey) 관계를 설정하고, `Mapped` 방식을 통해 현대적인 SQLAlchemy 선언적 매핑 구현.

### 3. 대화 맥락 유지 및 히스토리 관리 (Context Awareness)
- **History Tracking**: DB에 저장된 이전 대화 내역을 조회하여 LLM에 전달함으로써, 단발성 응답이 아닌 이전 맥락을 기억하는 지속적인 대화 시스템 구축.
- **데이터 일관성**: 사용자 메시지와 AI 응답 메시지를 각각 DB에 비동기로 저장하여 대화의 영속성을 보장.

### 4. 서비스 간 연결 및 인프라 최적화
- **Docker Network**: 컨테이너 서비스 이름(`db`, `redis` 등)을 호스트명으로 사용하여 격리된 환경 내에서 서비스 간 통신 구현.
- **Persistence & Scaling**: 도커 볼륨을 통한 데이터 유실 방지 및 Worker 컨테이너 확장을 통한 병렬 처리 가능성(Scale-out) 이해.
- **Error Handling**: `VARCHAR` 길이 제한 등 MySQL 엔진의 특성에 따른 디버깅과 데이터 타입 최적화 경험.

---

## 🚀 실행 및 확인 방법

### 1. 컨테이너 빌드 및 백그라운드 실행
터미널에서 아래 명령어를 입력합니다.
```bash
docker compose up -d --build
```

### 2. API 주요 엔드포인트
- **대화 시작 (새 방 생성)**: `POST /conversations`
- **메시지 전송 (대화하기)**: `POST /conversations/{id}/messages`
- **대화 내역 조회**: `GET /conversations/{id}/messages`
  
### 3. 로그 실시간 모니터링
- **전체 로그**: `docker compose logs -f`
- **Worker 추론 로그**: `docker compose logs -f worker`

### 3. B 접속 정보 (MySQL Workbench)
컨테이너 외부(호스트)에서 DB에 접속하기 위한 정보입니다.
- **Hostname**: `127.0.0.1` | **Port**: `33061`
- **User/PW**: `root` / `password`
- **Default Schema**: `app_db`

---

## 💡 주요 개념 정리

### 1. 비동기 메시지 큐 및 자료구조 (LIFO vs FIFO)
- **FIFO(First-In, First-Out) 원리**: 큐(Queue) 자료구조의 핵심인 선입선출 원리를 이해하고, Redis List의 `LPUSH`와 `BRPOP` 명령어를 조합하여 요청이 들어온 순서대로 공정하게 처리되는 메시지 대기열을 구현함.
- **비동기 처리**: 무거운 AI 추론 작업을 API 요청과 분리하여, 서버가 중단되지 않고 지속적으로 요청을 수용할 수 있는 아키텍처를 학습함.

### 2. 도커 네트워크 및 서비스 발견 (Service Discovery)
- **Docker Network**: 각 컨테이너가 독립된 격리 환경임에도 불구하고, 도커 컴포즈 내부 네트워크를 통해 서비스 이름(`db`, `redis` 등)만으로 서로 통신할 수 있는 방식을 체득함.
- **Port Forwarding**: 호스트의 포트와 컨테이너 내부 포트를 연결하여 외부(WorkBench, Curl)에서 내부 서비스에 접근하는 메커니즘을 이해함.

### 3. 인프라 확장성 및 유연성 (Scale-out)
- **Scale-out 설계**: Redis를 중앙 브로커로 두는 구조를 통해, 향후 AI 요청량이 증가할 경우 `worker` 컨테이너의 개수만 늘려 병렬 처리 성능을 즉각적으로 향상시킬 수 있는 확장성 있는 구조를 설계함.
- **Data Persistence**: 볼륨(Volumes) 설정을 통해 컨테이너 재시작이나 삭제 시에도 DB 데이터와 학습 모델 파일이 보존되는 영속성 관리 기법을 익힘.

### 4. MSA(Microservice Architecture) 기반 풀스택 구성
- FastAPI(Backend), MySQL(DB), Redis(Broker), Llama(AI Worker) 등 서로 다른 역할을 가진 기술 스택을 하나의 인프라로 통합 관리하며 현대적인 웹 서비스 구축 흐름을 경험함.
