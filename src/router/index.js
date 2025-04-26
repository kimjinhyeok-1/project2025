import { createRouter, createWebHistory } from 'vue-router'

// 기본 뷰
import HomeView from '../views/HomeView.vue'

// 학생 관련 뷰
import StudentLayout from '../views/StudentLayout.vue'
import StudentQnA from '../views/StudentQnA.vue'
import StudentAssignment from '../views/StudentAssignment.vue'
import StudentHistory from '../views/StudentHistory.vue'

// 교수 관련 뷰
import ProfessorLayout from '../views/ProfessorLayout.vue'
import ProfessorView from '../views/ProfessorView.vue'
import ProfessorLesson from '../views/ProfessorLesson.vue'
import ProfessorQnA from '../views/ProfessorQnA.vue'
import ProfessorAssignments from '../views/ProfessorAssignments.vue'
import ProfessorReviewView from '../views/ProfessorReviewView.vue'
import ProfessorSummaryDetailView from '../views/ProfessorSummaryDetailView.vue'
import AssignmentPostForm from '../views/AssignmentPostForm.vue'
import AssignmentSubmit from '../views/AssignmentSubmit.vue'
import ProfessorRealtimeQuestion from '../views/ProfessorRealtimeQuestion.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/',
    redirect: '/student/assignment' // 메인 페이지 → 과제 페이지로 리디렉션
  },
  {
    path: '/student',
    name: 'StudentLayout',
    component: StudentLayout,
    children: [
      {
        path: '',
        redirect: '/student/assignment',
      },
      {
        path: 'qna',
        name: 'StudentQnA',
        component: StudentQnA,
      },
      {
        path: 'history',
        name: 'StudentHistory',
        component: StudentHistory,
      },
      {
        path: 'assignment',
        name: 'StudentAssignment',
        component: StudentAssignment,
      },
      {
        path: 'assignments/:id',
        name: 'AssignmentSubmit',
        component: AssignmentSubmit,
      }
    ],
  },
  {
    path: '/professor',
    component: ProfessorLayout,
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
        path: 'review',
        name: 'ProfessorReviewView',
        component: ProfessorReviewView,
      },
      {
        path: 'review/:id',
        name: 'ProfessorSummaryDetailView',
        component: ProfessorSummaryDetailView,
      },
      {
        path: 'assignments',
        name: 'ProfessorAssignments',
        component: ProfessorAssignments,
      },
      {
        path: 'assignments/new',
        name: 'AssignmentPostForm',
        component: AssignmentPostForm,
      },
      {
        path: 'realtime-question', // ✅ 새로 추가된 경로
        name: 'ProfessorRealtimeQuestion',
        component: ProfessorRealtimeQuestion,
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/' // fallback 처리
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
