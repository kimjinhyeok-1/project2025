const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  publicPath: '/', // 절대 경로 설정으로 새로고침 문제 대응
  transpileDependencies: true,

  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      definitions[0]['process.env'] = JSON.stringify(process.env);
      return definitions;
    });
  },

  configureWebpack: {
    plugins: [],
    optimization: {
      minimize: true,   // 코드 최소화
      splitChunks: {
        chunks: 'all',  // 코드 스플리팅
      },
    },
    performance: {
      hints: false,    // 빌드 파일 크기 경고 끄기
    }
  },

  devServer: {
    historyApiFallback: true, // SPA 라우팅 대응 (404 -> index.html)
    allowedHosts: 'all',      // Render나 Netlify 등 외부 프록시 지원
  }
});
