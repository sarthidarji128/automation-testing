const USERNAME = 'alice';
const PASSWORD = '123';
const SIGNUP_NAME = 'Group Test User';
const SIGNUP_EMAIL = 'grouptest@example.com';
const SIGNUP_PASSWORD = 'grouptest123';

function resetCurrentUser() {
  cy.request('GET', '/api/state').then((response) => {
    expect(response.status).to.eq(200);

    const state = response.body || {};

    cy.request('POST', '/api/state', {
      ...state,
      currentUser: null
    }).then((postResponse) => {
      expect(postResponse.status).to.eq(200);
    });
  });
}

describe('User Authentication - Signup and Login', () => {
  it('successfully signs up a new user', () => {
    resetCurrentUser();

    cy.visit('/#/signup');

    cy.get('#signup-name').should('be.visible').clear().type(SIGNUP_NAME);
    cy.get('#signup-username').should('be.visible').clear().type(SIGNUP_EMAIL);
    cy.get('#signup-password').should('be.visible').clear().type(SIGNUP_PASSWORD);
    cy.get('#signup-form .auth-btn').click();

    cy.url().should('include', '/#/chat');
    cy.get('.sidebar').should('be.visible');

    cy.request('/api/state').then((response) => {
      const users = response.body.users || [];
      const newUser = users.find((user) => user.username === SIGNUP_EMAIL);
      expect(newUser, 'new user should be created').to.exist;
      expect(newUser.name).to.equal(SIGNUP_NAME);
    });
  });

  it('successfully logs in existing user', () => {
    resetCurrentUser();

    cy.visit('/#/login');

    cy.get('#login-username').should('be.visible').clear().type(USERNAME);
    cy.get('#login-password').should('be.visible').clear().type(PASSWORD);
    cy.get('#login-form .auth-btn').click();

    cy.url().should('include', '/#/chat');
    cy.get('.chat-area').should('be.visible');
  });
});