const USERNAME = 'alice';
const PASSWORD = '123';
const SIGNUP_NAME = 'TanaySTest User';
const SIGNUP_EMAIL = 'tanaystest@example.com';
const SIGNUP_PASSWORD = 'testpass123';

function setCurrentUserNull() {
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

describe('Chat Application - Signup and Login', () => {
  it('signs up with new account', () => {
    setCurrentUserNull();

    cy.visit('/#/signup');

    // Fill signup form
    cy.get('#signup-name').should('be.visible').clear().type(SIGNUP_NAME);
    cy.get('#signup-username').should('be.visible').clear().type(SIGNUP_EMAIL);
    cy.get('#signup-password').should('be.visible').clear().type(SIGNUP_PASSWORD);
    cy.get('#signup-form .auth-btn').click();

    // Verify redirected to chat page after signup
    cy.url().should('include', '/#/chat');
    cy.get('.sidebar').should('be.visible');
    cy.get('.chat-area').should('be.visible');
  });

  it('logs in with existing account', () => {
    setCurrentUserNull();

    cy.visit('/#/login');

    // Fill login form
    cy.get('#login-username').should('be.visible').clear().type(USERNAME);
    cy.get('#login-password').should('be.visible').clear().type(PASSWORD);
    cy.get('#login-form .auth-btn').click();

    // Verify chat page is loaded
    cy.url().should('include', '/#/chat');
    cy.get('.sidebar').should('be.visible');
  });
});