# 인증 · 설정 · SSH/GPG 키

## gh auth — 인증 관리

```bash
gh auth login                          # GitHub 로그인 (브라우저/토큰 선택)
gh auth login --with-token             # 토큰으로 로그인 (stdin으로 토큰 입력)
gh auth login --hostname <host>        # GitHub Enterprise 로그인
gh auth logout                         # 로그아웃
gh auth logout --hostname <host>       # 특정 호스트 로그아웃
gh auth status                         # 현재 인증 상태 확인
gh auth token                          # 현재 토큰 출력
gh auth refresh                        # 토큰 갱신 (스코프 추가 가능)
gh auth refresh --scopes read:org,repo # 특정 스코프 추가하여 갱신
gh auth setup-git                      # git credential helper 설정
```

## gh config — 설정 관리

```bash
gh config list                         # 모든 설정 조회
gh config get <key>                    # 특정 설정값 조회
gh config set <key> <value>            # 설정값 변경
gh config set editor vim               # 에디터 설정
gh config set git_protocol ssh         # git 프로토콜 설정 (ssh/https)
gh config set prompt enabled           # 프롬프트 활성화
gh config set pager less               # 페이저 설정
```

## gh ssh-key — SSH 키 관리

```bash
gh ssh-key list                        # SSH 키 목록 조회
gh ssh-key add <keyfile>               # SSH 키 추가
gh ssh-key add ~/.ssh/id_ed25519.pub --title "My Key"
gh ssh-key delete <id>                 # SSH 키 삭제
```

## gh gpg-key — GPG 키 관리

```bash
gh gpg-key list                        # GPG 키 목록 조회
gh gpg-key add <keyfile>               # GPG 키 추가
gh gpg-key delete <keyid>              # GPG 키 삭제
```
