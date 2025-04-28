const { defineConfig } = require('@vue/cli-service');
const path = require('path'); // ✅ path 모듈 추가

module.exports = defineConfig({
  publicPath: '/', // 새로고침 문제 대응
  transpileDependencies: true,

  chainWebpack: config => {
    config.resolve.alias
      .set('@', path.resolve(__dirname, 'src')); // ✅ @를 src로 연결해주는 alias 추가
    config.plugin('define').tap(definitions => {
      definitions[0]['process.env'] = JSON.stringify(process.env);
      return definitions;
    });
  },

  configureWebpack: {
    plugins: [],
    optimization: {
      minimize: true,
      splitChunks: {
        chunks: 'all',
      },
    },
    performance: {
      hints: false,
    }
  },

  devServer: {
    historyApiFallback: true,
    allowedHosts: 'all',
    proxy: {
      '^/api': {
        target: 'http://localhost:8000', // ⬅️ FastAPI 백엔드 서버 주소
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' },
      }
    }
  }
});
