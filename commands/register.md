---
name: register
description: "Korea SNS 서브사이트에 회원가입한다. 사이트 이름/도메인, 이메일, 비밀번호, 닉네임을 입력하여 새 계정을 생성하고 API 키를 획득한다. 예: '/korea:register apple.withcenter.com user@example.com pass123 홍길동'. 회원가입, 계정 생성, 가입, 신규 등록 시 사용."
---

# /korea:register — 회원가입

Korea SNS 서브사이트에 새 계정을 생성하고 API 키를 획득한다.

## 명령어 형식

```
/korea:register <사이트이름> <email> <password> <nickname>
```

**네 개의 파라미터 모두 필수이다.** 하나라도 빠지면 작업을 중단하고 사용자에게 안내한다.

## 사용 예시

```
/korea:register apple.withcenter.com user@example.com mypass123 홍길동
/korea:register bangphil.com test@example.com secure456 마닐라사람
```

## 실행 절차

### 1단계: 필수 파라미터 확인

ARGUMENTS에서 다음 4개의 파라미터를 순서대로 추출한다:

| 순서 | 파라미터 | 필수 | 설명 |
|------|----------|------|------|
| 1 | **사이트이름** | **필수** | 서브사이트 도메인 (예: `apple.withcenter.com`, `bangphil.com`) |
| 2 | **email** | **필수** | 유효한 이메일 주소 |
| 3 | **password** | **필수** | 최소 6자 이상 |
| 4 | **nickname** | **필수** | 표시 이름 (닉네임) |

**파라미터가 부족한 경우 즉시 작업을 중단하고 다음을 안내한다:**

```
회원가입에 필요한 정보가 부족합니다.
사용법: /korea:register <사이트이름> <email> <password> <nickname>
예시: /korea:register apple.withcenter.com user@example.com mypass123 홍길동

필수 항목:
  - 사이트이름: 가입할 서브사이트 도메인 (예: apple.withcenter.com)
  - email: 유효한 이메일 주소
  - password: 최소 6자 이상
  - nickname: 표시 이름 (닉네임)
```

### 2단계: 사이트 URL 구성

사이트이름에서 Base URL을 구성한다:
- `apple.withcenter.com` → `https://apple.withcenter.com/api/v1`
- `bangphil.com` → `https://bangphil.com/api/v1`

도메인에 프로토콜이 없으면 `https://`를 앞에 붙인다.

### 3단계: 회원가입 실행

```bash
python3 skills/korea/scripts/korea_api.py --api-key "" \
  --base-url "https://{사이트이름}/api/v1" \
  register --email "{EMAIL}" --password "{PASSWORD}" --display-name "{NICKNAME}"
```

### 4단계: 결과 보고 — API 키를 사용자에게 표시

**성공 시** 다음 형식으로 사용자에게 API 키를 명확하게 보여준다:

```
✅ 회원가입 성공!

사이트: {사이트이름}
이메일: {email}
닉네임: {nickname}
회원 ID: {id}

🔑 API 키: {api_key}

이 API 키를 이후 /korea:create, /korea:update 등의 명령어에서 사용할 수 있습니다.
```

**실패 시** 에러 메시지를 사용자에게 전달한다:
- `"이미 등록된 이메일입니다."` → 다른 이메일 사용 또는 로그인 안내
- `"비밀번호는 최소 6자 이상이어야 합니다."` → 비밀번호 변경 안내
- `"올바른 이메일 형식이 아닙니다."` → 이메일 형식 확인 안내
- `"메인 사이트에서는 회원가입할 수 없습니다."` → 서브사이트 도메인을 정확히 입력하라고 안내

## 주의사항

- 메인 사이트(withcenter.com)에서는 회원가입 불가 — 반드시 서브사이트 도메인 필요
- 비밀번호는 최소 6자 이상이어야 한다
- 이미 등록된 이메일로는 가입할 수 없다
- 가입 즉시 자동 로그인되며 API 키가 발급된다
- 서브사이트의 첫 번째 가입자는 자동으로 사이트 소유자(관리자)로 지정된다
