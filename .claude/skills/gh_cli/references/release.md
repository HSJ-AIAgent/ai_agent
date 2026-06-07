# 릴리즈 관리 (gh release)

## 생성

```bash
gh release create <tag>                        # 릴리즈 생성 (대화형)
gh release create v1.0.0 --title "v1.0.0" --notes "변경사항"
gh release create v1.0.0 --generate-notes      # 변경사항 자동 생성
gh release create v1.0.0 --draft               # 드래프트 릴리즈
gh release create v1.0.0 --prerelease          # 프리릴리즈
gh release create v1.0.0 --target main         # 대상 브랜치/커밋
gh release create v1.0.0 ./dist/*.zip          # 파일 첨부
gh release create v1.0.0 ./dist/app.zip#"App Binary"  # 파일명 지정

gh release create v1.0.0 \
  --title "Release v1.0.0" \
  --notes "버그 수정 및 기능 개선" \
  --generate-notes \
  ./dist/app-linux.tar.gz \
  ./dist/app-windows.zip
```

## 조회

```bash
gh release list                                # 릴리즈 목록
gh release list --limit 10
gh release list --json tagName,name,publishedAt

gh release view <tag>                          # 특정 릴리즈 상세
gh release view --json tagName,body,assets
gh release view --web                          # 브라우저로 열기
gh release view v1.0.0 --json assets --jq '.assets[].url'
```

## 수정 · 삭제

```bash
gh release edit <tag>                          # 릴리즈 수정 (대화형)
gh release edit v1.0.0 --title "새 제목"
gh release edit v1.0.0 --notes "새 내용"
gh release edit v1.0.0 --draft=false           # 드래프트 해제
gh release edit v1.0.0 --prerelease=false      # 프리릴리즈 해제

gh release delete <tag>                        # 릴리즈 삭제
gh release delete <tag> --yes                  # 확인 없이 삭제
gh release delete <tag> --cleanup-tag          # 태그도 함께 삭제
```

## 파일 업로드 · 다운로드

```bash
gh release upload <tag> <files...>             # 파일 업로드
gh release upload v1.0.0 ./dist/app.zip
gh release upload v1.0.0 ./dist/*.tar.gz       # 글로브 패턴
gh release upload v1.0.0 file.zip --clobber    # 기존 파일 덮어쓰기

gh release download <tag>                      # 모든 에셋 다운로드
gh release download v1.0.0 --pattern "*.zip"   # 특정 패턴만
gh release download --dir ./downloads          # 저장 경로 지정
gh release download --archive zip              # 소스 아카이브 다운로드
```
