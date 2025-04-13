const { defineConfig } = require('@vue/cli-service');
const path = require('path');
const fs = require('fs');

module.exports = defineConfig({
  publicPath: './',
  transpileDependencies: true,

  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      definitions[0]['process.env'] = JSON.stringify(process.env);
      return definitions;
    });
  },

  configureWebpack: {
    plugins: [
      {
        apply: (compiler) => {
          compiler.hooks.done.tap('CopyPublicFilesPlugin', () => {
            const filesToCopy = [
              { src: 'public/static.json', dest: 'dist/static.json' }
            ];

            filesToCopy.forEach(({ src, dest }) => {
              const absSrc = path.resolve(__dirname, src);
              const absDest = path.resolve(__dirname, dest);
              if (fs.existsSync(absSrc)) {
                fs.copyFileSync(absSrc, absDest);
                console.log(`✅ ${path.basename(src)} 복사 완료`);
              } else {
                console.warn(`⚠️ ${src} 파일이 존재하지 않음`);
              }
            });
          });
        }
      }
    ]
  }
});
