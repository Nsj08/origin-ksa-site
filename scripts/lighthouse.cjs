const origin = process.env.TEST_ORIGIN || 'http://127.0.0.1:4322';
module.exports = {ci:{
  collect:{url:['en/','ar/','en/product/848180/','ar/product/848180/','en/browse/','ar/browse/'].map(path=>origin+'/'+path),
    numberOfRuns:3,settings:{chromeFlags:'--headless --no-sandbox --disable-dev-shm-usage',onlyCategories:['performance','accessibility','best-practices','seo']}},
  assert:{assertions:Object.fromEntries(['performance','accessibility','best-practices','seo'].map(key=>['categories:'+key,['error',{minScore:0.95,aggregationMethod:'median'}]]))},
  upload:{target:'filesystem',outputDir:'.lighthouseci/local'}
}};
