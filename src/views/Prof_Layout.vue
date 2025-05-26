<template>
  <div id="wrapper" class="d-flex">
    <!-- Sidebar -->
    <ul class="navbar-nav bg-gradient-primary sidebar sidebar-dark accordion" id="accordionSidebar">
      <!-- 상단 브랜드 -->
      <router-link class="sidebar-brand d-flex align-items-center justify-content-center" to="/professor">
        <div class="sidebar-brand-icon">
          <i class="fas fa-chalkboard-teacher"></i>
        </div>
        <div class="sidebar-brand-text mx-3">PROFESSOR</div>
      </router-link>

      <hr class="sidebar-divider my-0" />

      <!-- 질문 메뉴 -->
      <li class="nav-item my-2">
        <router-link class="nav-link" to="/professor/qna">
          <i class="fas fa-question-circle"></i>
          <span>학생들의 질문</span>
        </router-link>
      </li>

      <!-- ✅ 수업 드롭다운 메뉴 -->
      <li class="nav-item my-2">
        <a
          class="nav-link collapsed"
          href="#collapseLesson"
          data-toggle="collapse"
          data-target="#collapseLesson"
          aria-expanded="false"
          aria-controls="collapseLesson"
        >
          <i class="fas fa-chalkboard"></i>
          <span class="ml-2">수업</span>
        </a>
        <div
          id="collapseLesson"
          class="collapse"
          data-parent="#accordionSidebar"
        >
          <div class="bg-white py-2 collapse-inner rounded text-center">
            <router-link class="collapse-item" to="/professor/lesson">수업 시작</router-link>
            <router-link class="collapse-item" to="/professor/review">수업 요약</router-link>
          </div>
        </div>
      </li>

      <!-- 과제 메뉴 -->
      <li class="nav-item my-2">
        <router-link class="nav-link" to="/professor/assignments">
          <i class="fas fa-tasks"></i>
          <span>과제</span>
        </router-link>
      </li>
    </ul>

    <!-- 메인 콘텐츠 -->
    <div id="content-wrapper" class="flex-grow-1">
      <div id="content" class="p-4">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ✅ 기본 정렬 및 스타일 */
.sidebar .nav-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
}

.sidebar .nav-link i {
  margin-bottom: 4px;
  font-size: 1.6rem;
}

.sidebar .nav-link span {
  font-size: 1.1rem;
  font-weight: 600;
}

/* ✅ 드롭다운 아이콘 교체 (Font Awesome 기반) */
.sidebar .nav-link.collapsed::after {
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  content: "\f107"; /* ▼ (닫힘 상태) */
  font-size: 1rem;
  position: absolute;
  bottom: -1.2rem;
  right: 50%;
  transform: translateX(50%);
  color: #ffffff;
}

.sidebar .nav-link:not(.collapsed)::after {
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  content: "\f106"; /* ▲ (열림 상태) */
  font-size: 1rem;
  position: absolute;
  bottom: -1.2rem;
  right: 50%;
  transform: translateX(50%);
  color: #ffffff;
}

/* 메뉴 간 여백 조절 */
.nav-item {
  margin-top: 0.5rem !important;
  margin-bottom: 0.5rem !important;
}

/* 드롭다운 내부 항목 스타일 */
.collapse-inner .collapse-item {
  font-size: 1rem;
  font-weight: 500;
}
</style>
