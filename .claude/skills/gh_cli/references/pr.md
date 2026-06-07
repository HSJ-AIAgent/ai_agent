# PR (Pull Request) 관리 (gh pr)

## 생성

```bash
gh pr create                                   # PR 생성 (대화형)
gh pr create --title "제목" --body "내용"
gh pr create --base main --head feature-branch
gh pr create --draft                           # 드래프트 PR
gh pr create --reviewer alice,bob              # 리뷰어 지정
gh pr create --assignee @me                    # 나에게 할당
gh pr create --label bug,enhancement          # 라벨 지정
gh pr create --milestone "v1.0"               # 마일스톤 지정
gh pr create --web                             # 브라우저에서 생성
gh pr create --fill                            # 커밋 메시지로 자동 채우기
```

## 조회

```bash
gh pr list                                     # PR 목록
gh pr list --state open                        # 열린 PR
gh pr list --state closed                      # 닫힌 PR
gh pr list --state merged                      # 병합된 PR
gh pr list --author alice                      # 특정 작성자
gh pr list --assignee @me                      # 내가 할당된 PR
gh pr list --label bug                         # 특정 라벨
gh pr list --base main                         # 특정 base 브랜치
gh pr list --search "is:open review-requested:@me"  # 내 리뷰 요청

gh pr view <number>                            # PR 상세 조회
gh pr view --web                               # 브라우저로 열기
gh pr view --json number,title,state,url

gh pr status                                   # 내 PR 현황 (현재 브랜치 기준)
gh pr diff <number>                            # PR diff 조회
gh pr checks <number>                          # PR CI 체크 상태
gh pr checks --watch                           # CI 완료까지 대기
```

## 수정

```bash
gh pr edit <number>                            # PR 수정 (대화형)
gh pr edit <number> --title "새 제목"
gh pr edit <number> --body "새 내용"
gh pr edit <number> --add-label bug
gh pr edit <number> --remove-label enhancement
gh pr edit <number> --add-reviewer alice
gh pr edit <number> --add-assignee @me
gh pr edit <number> --milestone "v2.0"
gh pr ready <number>                           # 드래프트 → 리뷰 준비 상태
```

## 리뷰

```bash
gh pr review <number>                          # 리뷰 제출 (대화형)
gh pr review <number> --approve                # 승인
gh pr review <number> --request-changes --body "수정 필요"
gh pr review <number> --comment --body "코멘트"
```

## 병합 · 닫기

```bash
gh pr merge <number>                           # PR 병합 (대화형)
gh pr merge <number> --merge                   # 일반 병합
gh pr merge <number> --squash                  # Squash 병합
gh pr merge <number> --rebase                  # Rebase 병합
gh pr merge <number> --delete-branch           # 병합 후 브랜치 삭제
gh pr merge <number> --auto                    # 조건 충족 시 자동 병합

gh pr close <number>                           # PR 닫기
gh pr reopen <number>                          # PR 다시 열기
```

## 브랜치 체크아웃

```bash
gh pr checkout <number>                        # PR 브랜치 체크아웃
gh co <number>                                 # 단축 alias
```

## 코멘트

```bash
gh pr comment <number> --body "코멘트"
gh pr comment <number> --edit-last             # 마지막 코멘트 수정
gh pr comment <number> --delete-last           # 마지막 코멘트 삭제
```
