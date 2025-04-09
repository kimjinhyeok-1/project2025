const { defineConfig } = require('@vue/cli-service');
const path = require('path');   // ✅ 경로 다루기
const fs = require('fs');       // ✅ 파일 복사용


module.exports = defineConfig({
  publicPath: '/',
  transpileDependencies: true,
  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      definitions[0]['process.env'] = JSON.stringify(process.env); // 환경 변수 적용
      return definitions;
    });
  },
  // ✅ 아래 부분을 추가!
  configureWebpack: {
    plugins: [
      {
        apply: (compiler) => {
          compiler.hooks.done.tap('CopyRedirectsPlugin', () => {
            const src = path.resolve(__dirname, 'public/_redirects');
            const dest = path.resolve(__dirname, 'dist/_redirects');
            if (fs.existsSync(src)) {
              fs.copyFileSync(src, dest);
              console.log('✅ _redirects 파일을 dist 폴더에 복사 완료');
            }
          });
        }
      }
    ]
  }
});