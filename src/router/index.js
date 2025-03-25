import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import StudentView from '../views/StudentView.vue';
import ProfessorView from '../views/ProfessorView.vue'; // 교수자 대시보드
import ProfessorLesson from '../views/ProfessorLesson.vue'; // 수업하기 (녹화/녹음)
import ProfessorQnA from '../views/ProfessorQnA.vue'; // 질문 & 답변 확인하기
import ProfessorAssignments from '../views/ProfessorAssignments.vue'; // 과제 확인하기

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/student',
    name: 'Student',
    component: StudentView,
  },
  {
    path: '/professor',
    name: 'ProfessorDashboard',
    component: ProfessorView, // 교수자 메인 화면
  },
  {
    path: '/professor/lesson',
    name: 'ProfessorLesson',
    component: ProfessorLesson, // 수업하기 (녹화/녹음)
  },
  {
    path: '/professor/qna',
    name: 'ProfessorQnA',
    component: ProfessorQnA, // 질문 & 답변
  },
  {
    path: '/professor/assignments',
    name: 'ProfessorAssignments',
    component: ProfessorAssignments, // 과제 확인
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
