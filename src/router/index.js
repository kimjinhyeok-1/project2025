import { createRouter, createWebHistory } from 'vue-router'

// 기본 뷰들
import HomeView from '../views/HomeView.vue'

// 학생
import StudentLayout from '../views/StudentLayout.vue'
import StudentQnA from '../views/StudentQnA.vue'
import StudentAssignment from '../views/StudentAssignment.vue'
import StudentHistory from '../views/StudentHistory.vue'

// 교수 레이아웃 및 서브뷰
import ProfessorLayout from '../views/ProfessorLayout.vue'
import ProfessorView from '../views/ProfessorView.vue'
import ProfessorLesson from '../views/ProfessorLesson.vue'
import ProfessorQnA from '../views/ProfessorQnA.vue'
import ProfessorAssignments from '../views/ProfessorAssignments.vue'
import ProfessorReviewView from '../views/ProfessorReviewView.vue'
import ProfessorSummaryDetailView from '../views/ProfessorSummaryDetailView.vue'

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
      { 
        path: '/student/history',
        name: 'StudentHistory', 
        component: StudentHistory }
    ],
  },
  {
    path: '/professor/assignments/new',
    component: () => import('@/views/AssignmentPostForm.vue'),
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
        path: 'assignments',
        name: 'ProfessorAssignments',
        component: ProfessorAssignments,
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
    ],
  },
  {
    path: '/student/assignments',
    name: 'StudentAssignments',
    component: () => import('@/views/StudentAssignment.vue'),
  },
  {
    path: '/student/assignments/:id',
    name: 'AssignmentDetail',
    component: () => import('@/views/AssignmentDetail.vue'),
  },
  {
    path: '/student/history',
    name: 'StudentHistory',
    component: () => import('../views/StudentHistory.vue'),
  } 

]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
