import { createRouter, createWebHistory } from 'vue-router'

// 기본 뷰들
import HomeView from '../views/HomeView.vue'

// 학생
import StudentLayout from '../views/StudentLayout.vue'
import StudentQnA from '../views/StudentQnA.vue' // 새로 만들 컴포넌트
import StudentAssignment from '../views/StudentAssignment.vue' // 과제 컴포넌트 (임시)

// 교수 레이아웃 및 서브뷰
import ProfessorLayout from '../views/ProfessorLayout.vue'
import ProfessorView from '../views/ProfessorView.vue'
import ProfessorLesson from '../views/ProfessorLesson.vue'
import ProfessorQnA from '../views/ProfessorQnA.vue'
import ProfessorAssignments from '../views/ProfessorAssignments.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/student',
    component: StudentLayout,
    children: [
      {
        path: '',
        redirect: '/student/qna',
      },
      {
        path: 'qna',
        name: 'StudentQnA',
        component: StudentQnA,
      },
      {
        path: 'assignment',
        name: 'StudentAssignment',
        component: StudentAssignment,
      },
    ],
  },
  {
    path: '/professor',
    component: ProfessorLayout, // ✅ 교수 레이아웃
    children: [
      {
        path: '',
        name: 'ProfessorDashboard',
        component: ProfessorView,
      },
      {
        path: 'lesson',
        name: 'ProfessorLesson',
        component: ProfessorLesson,
      },
      {
        path: 'qna',
        name: 'ProfessorQnA',
        component: ProfessorQnA,
      },
      {
        path: 'assignments',
        name: 'ProfessorAssignments',
        component: ProfessorAssignments,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
