# 기타 명령어 (gist, search, secret, variable, api, label, alias, extension, status, browse)

## gh gist — Gist 관리

```bash
gh gist create <file>                          # Gist 생성
gh gist create file.py --desc "설명" --public  # 공개 Gist
gh gist create *.py                            # 여러 파일
gh gist create - <<< "echo hello"              # stdin으로 생성

gh gist list                                   # 내 Gist 목록
gh gist list --limit 20
gh gist list --public                          # 공개만

gh gist view <id>                              # Gist 조회
gh gist view <id> --raw                        # 원본 텍스트
gh gist view <id> --web                        # 브라우저로

gh gist edit <id>                              # Gist 수정
gh gist edit <id> --filename "new.py"

gh gist clone <id>                             # Gist 클론
gh gist delete <id>                            # Gist 삭제
```

## gh search — 검색

```bash
gh search repos "ai agent" --language python   # 리포지토리 검색
gh search repos --stars ">1000" --limit 20
gh search repos --topic "machine-learning"

gh search issues "memory leak" --repo owner/repo
gh search issues --assignee @me --state open

gh search prs "fix authentication" --state merged
gh search prs --author alice --base main

gh search commits "feat: add login" --repo owner/repo
gh search code "function main" --repo owner/repo
```

## gh secret — 시크릿 관리

```bash
gh secret list                                 # 시크릿 목록
gh secret list --repo owner/repo
gh secret list --org myorg --visibility all

gh secret set MY_SECRET                        # 시크릿 설정 (stdin 입력)
gh secret set MY_SECRET --body "value"         # 직접 값 지정
gh secret set MY_SECRET < secret.txt           # 파일에서 읽기
gh secret set MY_SECRET --repo owner/repo
gh secret set MY_SECRET --org myorg --visibility all

gh secret delete MY_SECRET                     # 시크릿 삭제
```

## gh variable — Actions 변수 관리

```bash
gh variable list                               # 변수 목록
gh variable get MY_VAR                         # 변수 값 조회
gh variable set MY_VAR --body "value"          # 변수 설정
gh variable set MY_VAR --env production        # 환경별 변수
gh variable delete MY_VAR                      # 변수 삭제
```

## gh api — GitHub API 직접 호출

```bash
gh api /user                                   # 현재 사용자 정보
gh api /repos/owner/repo                       # 리포지토리 정보
gh api /repos/owner/repo/issues                # 이슈 목록 API
gh api /repos/owner/repo/releases --paginate   # 페이지네이션

# POST 요청
gh api --method POST /repos/owner/repo/issues \
  --field title="버그 보고" \
  --field body="상세 내용"

# PATCH 요청
gh api --method PATCH /repos/owner/repo/issues/1 \
  --field state="closed"

# JSON 입력
gh api --method POST /gists \
  --input gist.json

# jq로 결과 파싱
gh api /repos/owner/repo/issues \
  --jq '.[].title'

# GraphQL
gh api graphql -f query='
  query {
    viewer { login }
  }
'
```

## gh label — 라벨 관리

```bash
gh label list                                  # 라벨 목록
gh label create "my-label" --color "#FF0000" --desc "설명"
gh label edit "bug" --name "버그" --color "#CC0000"
gh label delete "old-label"
gh label clone owner/source-repo               # 다른 리포에서 라벨 복사
```

## gh alias — 단축 명령어

```bash
gh alias list                                  # alias 목록
gh alias set pv 'pr view'                      # alias 생성
gh alias set bugs 'issue list --label=bug'
gh alias set --shell co 'git checkout $(gh pr list --json number,title | jq -r ".[] | \"\(.number) \(.title)\"" | fzf | awk "{print $1}")'
gh alias delete pv                             # alias 삭제
```

## gh extension — 확장 관리

```bash
gh extension list                              # 설치된 확장 목록
gh extension install <repo>                    # 확장 설치
gh extension install github/gh-copilot
gh extension upgrade <name>                    # 확장 업그레이드
gh extension upgrade --all                     # 모두 업그레이드
gh extension remove <name>                     # 확장 제거
gh extension search <query>                    # 확장 검색
gh extension exec <name>                       # 확장 실행
```

## gh status — 전체 현황

```bash
gh status                                      # 이슈, PR, 알림 현황
gh status --org myorg                          # 조직 필터
gh status --exclude owner/repo                 # 특정 리포 제외
```

## gh browse — 브라우저로 열기

```bash
gh browse                                      # 현재 리포 열기
gh browse --repo owner/repo                    # 특정 리포
gh browse main.py                              # 특정 파일
gh browse main.py:42                           # 특정 파일 특정 줄
gh browse --branch feature                     # 특정 브랜치
gh browse --commit <sha>                       # 특정 커밋
gh browse --releases                           # 릴리즈 페이지
gh browse --wiki                               # 위키 페이지
gh browse --settings                           # 설정 페이지
```

## gh project — GitHub Projects

```bash
gh project list                                # 프로젝트 목록
gh project list --owner alice
gh project view <number>                       # 프로젝트 상세
gh project create --title "My Project"         # 프로젝트 생성
gh project item-list <number>                  # 프로젝트 아이템 목록
gh project item-add <number> --url <issue-url> # 아이템 추가
gh project item-edit --id <item-id> --field-id <field-id> --text "value"
gh project item-delete --id <item-id>          # 아이템 삭제
gh project close <number>                      # 프로젝트 닫기
gh project delete <number>                     # 프로젝트 삭제
```

## gh org — 조직 관리

```bash
gh org list                                    # 내 조직 목록
```

## gh copilot — GitHub Copilot CLI

```bash
gh copilot suggest "도커 이미지 빌드하는 명령어"   # 명령어 제안
gh copilot explain "git rebase -i HEAD~3"       # 명령어 설명
```

## 출력 포맷 팁

```bash
# JSON 출력 후 jq 파싱
gh issue list --json number,title,state \
  --jq '.[] | "\(.number) \(.state) \(.title)"'

# 테이블 형식
gh issue list --json number,title \
  --template '{{range .}}{{.number}}\t{{.title}}{{"\n"}}{{end}}'

# 페이지네이션 (모든 결과)
gh api /repos/owner/repo/issues --paginate \
  --jq '.[].title'
```
