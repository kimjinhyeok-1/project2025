<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>교수님 홈페이지</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      line-height: 1.6;
    }
    header {
      background: #333;
      color: #fff;
      padding: 1rem 0;
      text-align: center;
    }
    nav ul {
      list-style: none;
      padding: 0;
      display: flex;
      justify-content: center;
      background: #444;
      margin: 0;
    }
    nav ul li {
      margin: 0 1rem;
    }
    nav ul li a {
      color: #fff;
      text-decoration: none;
    }
    section {
      padding: 2rem;
      max-width: 1000px;
      margin: auto;
    }
    footer {
      background: #333;
      color: #fff;
      text-align: center;
      padding: 1rem 0;
    }
    /* 반응형 디자인 */
    @media (max-width: 600px) {
      nav ul {
        flex-direction: column;
      }
      nav ul li {
        margin: 0.5rem 0;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>교수님의 이름</h1>
    <p>전공 분야 및 간단한 소개 문구</p>
  </header>
  
  <nav>
    <ul>
      <li><a href="#home">홈</a></li>
      <li><a href="#about">소개</a></li>
      <li><a href="#research">연구</a></li>
      <li><a href="#publications">논문</a></li>
      <li><a href="#teaching">강의</a></li>
      <li><a href="#contact">연락처</a></li>
    </ul>
  </nav>
  
  <section id="home">
    <h2>환영합니다</h2>
    <p>교수님의 홈페이지에 오신 것을 환영합니다. 이곳은 교수님의 연구, 강의, 논문 등의 정보를 제공하는 공간입니다.</p>
  </section>
  
  <section id="about">
    <h2>소개</h2>
    <p>교수님의 학력, 경력 및 연구 분야 등에 대한 소개글을 작성합니다.</p>
  </section>
  
  <section id="research">
    <h2>연구</h2>
    <p>교수님의 연구 프로젝트 및 관심 연구 분야를 소개합니다.</p>
  </section>
  
  <section id="publications">
    <h2>논문</h2>
    <p>교수님의 주요 논문 및 출판물을 목록으로 작성합니다.</p>
  </section>
  
  <section id="teaching">
    <h2>강의</h2>
    <p>교수님이 진행하신 강의, 커리큘럼, 수업 자료 등을 소개합니다.</p>
  </section>
  
  <section id="contact">
    <h2>연락처</h2>
    <p>교수님과 연락할 수 있는 이메일, 연구실 위치 및 기타 정보를 기재합니다.</p>
  </section>
  
  <footer>
    <p>&copy; 2025 교수님 이름. All rights reserved.</p>
  </footer>
</body>
</html>

