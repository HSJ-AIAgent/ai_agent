# 이슈 관리 (gh issue)

## 생성

```bash
gh issue create                                # 이슈 생성 (대화형)
gh issue create --title "버그 제목" --body "내용"
gh issue create --assignee @me                 # 나에게 할당
gh issue create --assignee alice,bob           # 복수 할당
gh issue create --label bug,urgent             # 라벨 지정
gh issue create --milestone "v1.0"             # 마일스톤 지정
gh issue create --project "My Project"         # 프로젝트 추가
gh issue create --web                          # 브라우저에서 생성
gh issue create --template "bug_report.md"     # 템플릿 사용
```

## 조회

```bash
gh issue list                                  # 이슈 목록 (기본: 열린 이슈)
gh issue list --state open                     # 열린 이슈
gh issue list --state closed                   # 닫힌 이슈
gh issue list --state all                      # 모든 이슈
gh issue list --assignee @me                   # 내가 할당된 이슈
gh issue list --author alice                   # 특정 작성자
gh issue list --label bug                      # 특정 라벨
gh issue list --milestone "v1.0"               # 특정 마일스톤
gh issue list --search "is:open sort:created"  # 검색 쿼리
gh issue list --limit 20                       # 최대 20개
gh issue list --json number,title,state

gh issue view <number>                         # 이슈 상세 조회
gh issue view --web                            # 브라우저로 열기
gh issue view --json number,title,body,comments

gh issue status                                # 내 이슈 현황
```

## 수정

```bash
gh issue edit <number>                         # 이슈 수정 (대화형)
gh issue edit <number> --title "새 제목"
gh issue edit <number> --body "새 내용"
gh issue edit <number> --add-label bug
gh issue edit <number> --remove-label enhancement
gh issue edit <number> --add-assignee alice
gh issue edit <number> --remove-assignee bob
gh issue edit <number> --milestone "v2.0"
```

## 상태 변경

```bash
gh issue close <number>                        # 이슈 닫기
gh issue close <number> --reason "completed"   # 이유 포함 닫기
gh issue close <number> --reason "not planned"
gh issue reopen <number>                       # 이슈 다시 열기
```

## 코멘트

```bash
gh issue comment <number> --body "코멘트 내용"
gh issue comment <number> --edit-last          # 마지막 코멘트 수정
gh issue comment <number> --delete-last        # 마지막 코멘트 삭제
```

## 고정 · 전환

```bash
gh issue pin <number>                          # 이슈 고정
gh issue unpin <number>                        # 이슈 고정 해제
gh issue develop <number>                      # 이슈에서 브랜치 생성
gh issue develop <number> --branch "fix/issue-123"
gh issue lock <number>                         # 이슈 잠금
gh issue unlock <number>                       # 이슈 잠금 해제
gh issue transfer <number> <repo>              # 다른 리포로 이슈 이전
```
