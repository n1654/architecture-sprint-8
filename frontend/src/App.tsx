import React from 'react';
import { ReactKeycloakProvider } from '@react-keycloak/web';
import Keycloak, { KeycloakConfig } from 'keycloak-js';
import ReportPage from './components/ReportPage';

const keycloakConfig: KeycloakConfig = {
  url: process.env.REACT_APP_KEYCLOAK_URL,
  realm: process.env.REACT_APP_KEYCLOAK_REALM||"",
  clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID||""
};

const keycloak = new Keycloak(keycloakConfig);

// PKCE: START -----------------------------------------------------------------
const initOptions = {
  pkceMethod: 'S256',
  checkLoginIframe: false,
  onLoad: 'login-required',
  flow: 'standard'
};

const eventLogger = (event: string, error?: unknown) => {
  console.log('Keycloak event:', event, error);
};

const tokenLogger = (tokens: { token?: string; refreshToken?: string }) => {
  console.log('Keycloak tokens:', tokens);
};
// PKCE: STOP ------------------------------------------------------------------

const App: React.FC = () => {
  return (
    <ReactKeycloakProvider
      authClient={keycloak}
// PKCE: START -----------------------------------------------------------------
      initOptions={initOptions}
      onEvent={eventLogger}
      onTokens={tokenLogger}
// PKCE: STOP ------------------------------------------------------------------
    >
      <div className="App">
        <ReportPage />
      </div>
    </ReactKeycloakProvider>
  );
};

export default App;