const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  publicPath: '/', // 새로고침 문제 대응
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
        target: 'http://localhost:8000', // ⬅️ 백엔드 FastAPI 서버 주소 (개발 모드용)
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' },
      }
    }
  }
});
