// Only forum image requests receive the forum Referer; local and external assets stay intact.
function __bogIsImageUrl(uri) {
  return typeof uri === 'string' && /^https?:\/\/(?:bog\.ac|(?:[a-z0-9-]+\.)*bog\.ac\.cn)\/image(?:_pre)?\//i.test(uri);
}
function __bogImageOptions(uri, options) {
  if (!__bogIsImageUrl(uri)) return options;
  var result = Object.assign({}, options || {});
  result.headers = Object.assign({}, result.headers || {}, {
    Referer: 'https://bog.ac/',
    'User-Agent': 'BOG-nimingban/1.2.0 (Android; ImageFix)'
  });
  return result;
}
function __bogImageSource(source) {
  if (Array.isArray(source)) return source.map(__bogImageSource);
  if (!source || !__bogIsImageUrl(source.uri)) return source;
  return Object.assign({}, source, __bogImageOptions(source.uri, {headers: source.headers}));
}
