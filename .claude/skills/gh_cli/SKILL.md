---
name: gh_cli
description: |
  GitHub CLI(gh) 명령어를 활용하여 GitHub 작업을 수행하는 스킬. 리포지토리 관리, PR/이슈 생성·수정·병합, 릴리즈 관리, GitHub Actions 워크플로우 실행, Gist 관리, 시크릿/변수 관리, API 직접 호출 등 gh CLI의 모든 기능을 포함한다.

  사용자가 다음과 같은 요청을 할 때 반드시 이 스킬을 활용하라:
  - GitHub 리포지토리 생성/클론/삭제/포크
  - PR(풀 리퀘스트) 생성, 조회, 머지, 리뷰
  - 이슈 생성, 조회, 댓글, 닫기
  - GitHub Actions 워크플로우/런 조회 및 실행
  - 릴리즈 생성 및 파일 업로드
  - Gist 생성 및 관리
  - SSH 키, GPG 키, 시크릿, 변수 관리
  - GitHub API 직접 호출
  - gh와 관련된 모든 GitHub 작업 자동화
---

# gh CLI 스킬

gh CLI를 사용하여 GitHub 작업을 효율적으로 수행한다. 각 카테고리별 상세 명령어는 `references/` 파일을 참고한다.

## 카테고리별 참고 파일

| 카테고리 | 파일 | 내용 |
|---|---|---|
| 인증·설정 | `references/auth_config.md` | auth, config, ssh-key, gpg-key |
| 리포지토리 | `references/repo.md` | repo 전체 서브커맨드 |
| PR | `references/pr.md` | pr 전체 서브커맨드 |
| 이슈 | `references/issue.md` | issue 전체 서브커맨드 |
| Actions | `references/actions.md` | run, workflow, cache |
| 릴리즈 | `references/release.md` | release 전체 서브커맨드 |
| 기타 | `references/misc.md` | gist, search, secret, variable, api, label, alias, extension, copilot, status |

## 작업 흐름

1. 사용자 요청의 카테고리를 파악한다.
2. 해당 `references/` 파일을 읽어 정확한 명령어와 플래그를 확인한다.
3. 명령어를 실행하고 결과를 사용자에게 설명한다.
4. 오류 발생 시 `gh <command> --help`로 추가 정보를 확인한다.

## 핵심 원칙

- 파괴적 작업(삭제, 강제 푸시 등)은 실행 전 반드시 사용자에게 확인한다.
- `--json` 플래그와 `--jq` 플래그를 활용하면 출력을 구조화하여 파싱할 수 있다.
- `gh api`로 CLI에 없는 GitHub API 엔드포인트도 직접 호출할 수 있다.
- 인증 상태는 `gh auth status`로 먼저 확인한다.
