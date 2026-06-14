# 리포지토리 관리 (gh repo)

## 기본 조작

```bash
gh repo create <name>                          # 리포지토리 생성 (대화형)
gh repo create <name> --public                 # 공개 리포지토리 생성
gh repo create <name> --private                # 비공개 리포지토리 생성
gh repo create <name> --description "설명"     # 설명 포함 생성
gh repo create <name> --clone                  # 생성 후 바로 클론
gh repo create <org>/<name>                    # 조직 리포지토리 생성

gh repo clone <repo>                           # 리포지토리 클론
gh repo clone <owner>/<repo>                   # owner 지정하여 클론
gh repo clone <repo> <dir>                     # 특정 디렉토리에 클론

gh repo view                                   # 현재 리포지토리 정보
gh repo view <owner>/<repo>                    # 특정 리포지토리 정보
gh repo view --web                             # 브라우저로 열기
gh repo view --json name,description,url       # JSON 출력

gh repo list                                   # 내 리포지토리 목록
gh repo list <owner>                           # 특정 유저/조직 목록
gh repo list --limit 50                        # 최대 50개 조회
gh repo list --language python                 # 언어 필터
gh repo list --public                          # 공개 리포지토리만
gh repo list --private                         # 비공개 리포지토리만
gh repo list --fork                            # 포크 리포지토리만
gh repo list --json name,url --jq '.[].url'    # URL만 추출
```

## 수정 · 삭제

```bash
gh repo edit                                   # 현재 리포 설정 수정 (대화형)
gh repo edit --description "새 설명"
gh repo edit --visibility public               # 공개/비공개 전환
gh repo edit --enable-issues                   # 이슈 활성화
gh repo edit --enable-wiki=false               # 위키 비활성화
gh repo edit --default-branch main             # 기본 브랜치 변경

gh repo rename <new-name>                      # 리포지토리 이름 변경
gh repo rename <new-name> --repo <owner>/<repo>

gh repo delete <repo>                          # 리포지토리 삭제 (확인 필요)
gh repo delete --yes                           # 확인 없이 삭제
```

## 포크 · 동기화 · 아카이브

```bash
gh repo fork                                   # 현재 리포 포크
gh repo fork <owner>/<repo>                    # 특정 리포 포크
gh repo fork --clone                           # 포크 후 바로 클론
gh repo fork --remote                          # upstream 원격 추가

gh repo sync                                   # 포크를 upstream과 동기화
gh repo sync --branch main

gh repo archive                                # 리포지토리 아카이브
gh repo unarchive                              # 아카이브 해제
```

## 기타

```bash
gh repo deploy-key list                        # 배포 키 목록
gh repo deploy-key add <keyfile> --title "CI"  # 배포 키 추가
gh repo deploy-key delete <id>                 # 배포 키 삭제

gh repo set-default <owner>/<repo>             # 기본 리포지토리 설정
```
