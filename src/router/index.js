import { createRouter, createWebHistory } from 'vue-router'

// 기본 뷰
import HomeView from '../views/HomeView.vue'

// 학생 관련 뷰
import StudentLayout from '../views/Stu_Layout.vue'
import StudentQnA from '../views/Stu_AIQnAprof.vue'
import StudentAssignment from '../views/Stu_Assign.vue'
import StudentHistory from '../views/StudentHistory.vue'
import StudentLessonSummary from '../views/Stu_LessonSummary.vue'
import StudentLessonQnA from '../views/Stu_LessonQnA.vue'
import StudentReviewDetail from '../views/Stu_ReviewDetail.vue'

// 교수 관련 뷰
import ProfessorLayout from '../views/Prof_Layout.vue'
import ProfessorView from '../views/Prof_DashBoard.vue'
import ProfessorLesson from '../views/Prof_Lesson.vue'
import ProfessorQnA from '../views/Prof_QnA.vue'
import ProfessorReviewView from '../views/Prof_Review.vue'
import ProfessorReviewDetail from '../views/Prof_ReviewDetail.vue' // ✅ 추가된 import
import ProfessorAssignments from '../views/Prof_Assign.vue'
import AssignmentPostForm from '../views/AssignmentPostForm.vue'
import AssignmentSubmit from '../views/AssignmentSubmit.vue'
import ProfessorRealtimeQuestion from '../views/Prof_Lesson.vue'
import AssignmentFeedback from '../views/AssignmentFeedback.vue'


const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/',
    redirect: '/student/assignment'
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
        path: 'lessonquestion',
        name: 'StudentLessonQnA',
        component: StudentLessonQnA,
      },
      {
        path: 'summary',
        name: 'StudentLessonSummary',
        component: StudentLessonSummary,
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
      },
      {
        path: 'review/:id',
        name: 'StudentReviewDetail',
        component: StudentReviewDetail,
      },
      {
        path: 'feedback/:id',
        name: 'AssignmentFeedback',
        component: AssignmentFeedback,
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
        path: 'review/:id', // ✅ 상세 페이지 경로 추가
        name: 'ProfessorReviewDetail',
        component: ProfessorReviewDetail,
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
        path: 'realtime-question',
        name: 'ProfessorRealtimeQuestion',
        component: ProfessorRealtimeQuestion,
      },
      {
        path: 'feedback/:id',
        name: 'ProfessorAllFeedback',
        component: () => import('../views/Prof_AllFeedback.vue'),
      }
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
 