// const CLIENT_ID = process.env.CLIENT_ID || '0oa4xgkk5kZIur0o55d6';
// const ISSUER = process.env.ISSUER || 'https://dev-87311569.okta.com/oauth2/default';
const OKTA_TESTING_DISABLEHTTPSCHECK = process.env.OKTA_TESTING_DISABLEHTTPSCHECK || false;
const REDIRECT_URI = `${window.location.origin}/login/callback`;

export default {
  oidc: {
    // clientId: CLIENT_ID,
    // issuer: ISSUER,
    clientId: '0oa4xgkk5kZIur0o55d6',
    issuer: 'https://dev-87311569.okta.com/oauth2/default',
    redirectUri: REDIRECT_URI,
    scopes: ['openid', 'profile', 'email', 'messages'],
    pkce: true,
    disableHttpsCheck: OKTA_TESTING_DISABLEHTTPSCHECK,
  },
  resourceServer: {
    messagesUrl: 'http://localhost:8000/api/messages',
  },
};
