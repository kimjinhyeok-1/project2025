const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  publicPath: '/', // 절대 경로 설정으로 새로고침 대응
  transpileDependencies: true,

  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      definitions[0]['process.env'] = JSON.stringify(process.env);
      return definitions;
    });
  },

  // static.json 복사 플러그인은 Render에서 필요 없으므로 제거함
  configureWebpack: {
    plugins: []
  }
});
