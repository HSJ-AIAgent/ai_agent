# GitHub Actions 관리 (gh run, gh workflow, gh cache)

## gh run — 워크플로우 실행 조회

```bash
gh run list                                    # 실행 목록
gh run list --workflow ci.yml                  # 특정 워크플로우 실행 목록
gh run list --branch main                      # 특정 브랜치
gh run list --status failure                   # 실패한 실행만
gh run list --limit 20
gh run list --json databaseId,status,conclusion

gh run view <run-id>                           # 실행 상세 조회
gh run view --log                              # 로그 출력
gh run view --log-failed                       # 실패 단계 로그만
gh run view --web                              # 브라우저로 열기
gh run view --exit-status                      # 종료 코드 반환

gh run watch <run-id>                          # 실행 완료까지 모니터링
gh run watch --exit-status                     # 완료 후 성공/실패 코드 반환

gh run rerun <run-id>                          # 실행 재시작
gh run rerun --failed-only                     # 실패 잡만 재시작
gh run rerun --debug                           # 디버그 모드로 재시작

gh run cancel <run-id>                         # 실행 취소
gh run delete <run-id>                         # 실행 삭제

gh run download <run-id>                       # 아티팩트 다운로드
gh run download <run-id> --name my-artifact    # 특정 아티팩트
gh run download --dir ./artifacts              # 저장 디렉토리 지정
```

## gh workflow — 워크플로우 관리

```bash
gh workflow list                               # 워크플로우 목록
gh workflow list --all                         # 비활성 포함 모두
gh workflow list --json id,name,state

gh workflow view ci.yml                        # 워크플로우 상세
gh workflow view --web                         # 브라우저로 열기

gh workflow run ci.yml                         # 워크플로우 수동 실행
gh workflow run ci.yml --ref feature-branch    # 특정 브랜치/태그로 실행
gh workflow run ci.yml --field env=production  # 입력값 전달
gh workflow run ci.yml --json '{"env":"prod"}' # JSON 입력

gh workflow enable ci.yml                      # 워크플로우 활성화
gh workflow disable ci.yml                     # 워크플로우 비활성화
```

## gh cache — Actions 캐시 관리

```bash
gh cache list                                  # 캐시 목록
gh cache list --limit 20
gh cache list --json id,key,size

gh cache delete <id>                           # 특정 캐시 삭제
gh cache delete --all                          # 모든 캐시 삭제
```
