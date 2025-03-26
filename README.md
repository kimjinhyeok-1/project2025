<<<<<<< HEAD

오케이! 팀원이 GitHub에 수정된 `test` 파일을 **푸시(pushed)** 했다면,  
이제 너는 그 변경사항을 **받아오기(pull)**만 하면 돼! 🙌

---

## ✅ 내가 팀원의 수정사항 받아오는 방법

### 👣 1단계: 내 `test` 폴더로 이동

```bash
cd ~/abcde/test
```

---

### 👣 2단계: 현재 상태 확인 (혹시 내 수정사항이 남아있을 수도 있으니까)

```bash
git status
```

→ **수정 중인 파일이 없거나 커밋한 상태여야 안전하게 pull 가능해.**

---

### 👣 3단계: GitHub에서 팀원 변경사항 가져오기

```bash
git pull origin main
```

> 여기서 `main`은 GitHub 기본 브랜치 이름이야 (보통 `main`)

---

## ⚠️ pull 중에 충돌(conflict)이 생기는 경우?

Git이 아래처럼 물어볼 수 있어:

```
CONFLICT (content): Merge conflict in src/App.vue
Automatic merge failed; fix conflicts and then commit the result.
```

이 경우는 Git이 자동 병합 못한 거라 **VS Code에서 충돌 부분**을 수정하고:

```bash
git add .
git commit -m "Fix: merge conflict"
git push origin main
```

이렇게 병합 완료하면 돼!

---

## ✅ 추가로: 혹시 팀원이 다른 브랜치에 올렸다면?

```bash
git fetch
git branch -r
```

→ 원격 브랜치 목록이 나오고, 예: `origin/feature-xxx`  
그 브랜치를 가져오고 싶다면:

```bash
git checkout -b feature-xxx origin/feature-xxx
```

---

## ✨ 정리

| 하고 싶은 일 | 명령어 |
|---------------|---------|
| 팀원 변경사항 받아오기 | `git pull origin main` |
| 내 수정사항 커밋 안 한 상태일 때 | `git add .` → `git commit -m "작업 중 저장"` 후 pull |
| 충돌났을 때 | 수정 후 `git add .` → `git commit` |

---

필요하면 지금 `git status` 결과 보여줘도 돼!  
바로 도와줄게 😄

# test

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
=======

>>>>>>> 2a98cca67691431e4800e939dd93a42fc62d67f9
