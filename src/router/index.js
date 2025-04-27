import { createRouter, createWebHistory } from 'vue-router'

// 기본 뷰
import HomeView from '../views/HomeView.vue'

// 학생 관련 뷰
import StudentLayout from '../views/Stu_Layout.vue'
import StudentQnA from '../views/Stu_AIQnAprof.vue'
import StudentAssignment from '../views/Stu_Assign.vue'
import StudentHistory from '../views/StudentHistory.vue'

// 교수 관련 뷰
import ProfessorLayout from '../views/Prof_Layout.vue'
import ProfessorView from '../views/Prof_DashBoard.vue'
import ProfessorLesson from '../views/Prof_Lesson.vue'
import ProfessorQnA from '../views/Prof_QnA.vue'
import ProfessorAssignments from '../views/Prof_Assign.vue'
import ProfessorReviewView from '../views/Prof_Review.vue'
import ProfessorSummaryDetailView from '../views/Prof_SummaryDetail.vue'
import AssignmentPostForm from '../views/AssignmentPostForm.vue'
import AssignmentSubmit from '../views/AssignmentSubmit.vue'
import ProfessorRealtimeQuestion from '../views/Prof_AIQnAStu.vue'

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
        path: 'test',
        name: 'Daesungtest',
        component: DaesungTest,
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
